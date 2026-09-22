import re
from typing import List, Dict, Any, Set
from backend.models.variable import VariableModel

TYPE_MAPPING = {
    "string": "String variable",
    "number": "Integer / Float variable",
    "boolean": "Boolean variable",
    "list": "Array variable",
    "dictionary": "Object variable",
    "table": "Datatable variable (PAD) / Array of Objects (Cloud)",
    "record": "Object variable",
    "datetime": "String (ISO 8601 DateTime)",
    "file": "File / Binary content",
    "credential": "Secure text / Azure Key Vault secret",
    "window": "UI Window instance (PAD)",
}

VARIABLE_REGEX = re.compile(r'\$([a-zA-Z0-9_]+)(?:\.[a-zA-Z0-9_]+)?\$')

class VariableAnalyzer:
    @staticmethod
    def extract_and_analyze_variables(
        raw_json_data: Any,
        actions: List[Dict[str, Any]],
        task_name: str = "MainTask"
    ) -> List[VariableModel]:
        variables_map: Dict[str, VariableModel] = {}

        # 1. Extract declared variables from raw A360 JSON if present
        raw_vars = []
        if isinstance(raw_json_data, dict):
            raw_vars = raw_json_data.get("variables", [])
            if not isinstance(raw_vars, list):
                raw_vars = []

        for v in raw_vars:
            if not isinstance(v, dict):
                continue
            name = v.get("name")
            if not name:
                continue

            var_type = (v.get("type") or "String").capitalize()
            type_lower = var_type.lower()
            pa_equiv = TYPE_MAPPING.get(type_lower, "String variable")

            # Extract initial value if available
            init_val = None
            if "defaultValue" in v:
                val_obj = v["defaultValue"]
                if isinstance(val_obj, dict):
                    init_val = next(iter(val_obj.values()), None) if val_obj else None
                else:
                    init_val = val_obj

            is_input = bool(v.get("input", False))
            is_output = bool(v.get("output", False))
            desc = v.get("description", "")

            variables_map[name] = VariableModel(
                name=name,
                type=var_type,
                scope=task_name,
                task=task_name,
                initialValue=init_val,
                usage="Unused",
                isInput=is_input,
                isOutput=is_output,
                expression=None,
                powerAutomateEquivalent=pa_equiv,
                usedInSteps=[],
                createdInStep=None,
                dependencies=[],
                description=desc
            )

        # 2. Inspect all actions to find references ($VarName$), assignments, inputs/outputs
        for action in actions:
            step = action.get("step", 0)
            command = action.get("command", "")
            attrs = action.get("attributes", {})
            output_var = action.get("outputVariable") or (attrs.get("variable") if isinstance(attrs, dict) else None)

            # Record write/creation
            if output_var and isinstance(output_var, str):
                clean_out = output_var.replace("$", "").strip()
                if clean_out:
                    if clean_out not in variables_map:
                        variables_map[clean_out] = VariableModel(
                            name=clean_out,
                            type="String",
                            scope=task_name,
                            task=task_name,
                            usage="Write",
                            powerAutomateEquivalent="String variable",
                            usedInSteps=[step],
                            createdInStep=step
                        )
                    else:
                        v = variables_map[clean_out]
                        if step not in v.usedInSteps:
                            v.usedInSteps.append(step)
                        if v.createdInStep is None:
                            v.createdInStep = step
                        v.usage = "Read/Write" if "Read" in v.usage else "Write"

            # Scan text content of attributes for $VarName$
            attr_str = str(attrs)
            matches = VARIABLE_REGEX.findall(attr_str)
            for m in matches:
                if m not in variables_map:
                    # Dynamically discovered variable
                    variables_map[m] = VariableModel(
                        name=m,
                        type="String",
                        scope=task_name,
                        task=task_name,
                        usage="Read",
                        powerAutomateEquivalent="String variable",
                        usedInSteps=[step]
                    )
                else:
                    v = variables_map[m]
                    if step not in v.usedInSteps:
                        v.usedInSteps.append(step)
                    if v.usage == "Unused":
                        v.usage = "Read"
                    elif v.usage == "Write":
                        v.usage = "Read/Write"

        # Sort variables by name
        results = sorted(variables_map.values(), key=lambda x: x.name)
        return results
