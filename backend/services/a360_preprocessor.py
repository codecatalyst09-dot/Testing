import json
from copy import deepcopy
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

REMOVE_COMMANDS = {
    "Comment",
    "messageBox",
    "logToFile",
    "SetTitle",
}

REMOVE_TASKBOTS = {
    "LogLine",
    "LogException",
    "LogTaskEnd",
}

REMOVE_KEYS = {
    "uid",
    "packageName",
    "disabled",
    "returns",
    "capture",
    "description",
    "properties",
    "variables",
    "packages",
    "workItemTemplateName",
}

def remove_empty(value):
    return value in (
        None,
        {},
        [],
        "",
    )


def unwrap(value):
    while isinstance(value, dict):
        if len(value) == 1:
            key = next(iter(value))
            if key in (
                "string",
                "number",
                "boolean",
                "expression",
                "value",
            ):
                value = value[key]
                continue
        break
    return value


def simplify_attributes(attributes):
    result = {}
    if not isinstance(attributes, list):
        return result

    for attr in attributes:
        if not isinstance(attr, dict):
            continue
        name = attr.get("name")
        if not name:
            continue
        value = unwrap(attr.get("value"))
        result[name] = value
    return result


def should_remove_node(node):
    if not isinstance(node, dict):
        return False

    command = node.get("commandName")

    if node.get("disabled") is True:
        return True

    if command in REMOVE_COMMANDS:
        return True

    if command == "runTask":
        try:
            # Check if taskbot name matches any REMOVE_TASKBOTS
            attrs = node.get("attributes", [])
            for a in attrs:
                val = unwrap(a.get("value"))
                if any(x in str(val) for x in REMOVE_TASKBOTS):
                    return True
        except Exception:
            pass

    return False


class A360Preprocessor:
    def __init__(self):
        self.step_counter = 0
        self.raw_step_counter = 0
        self.disabled_actions: List[Dict[str, Any]] = []

    def extract_disabled_actions(
        self,
        node: Any,
        task_name: str = "MainTask",
        file_path: str = "",
        parent_command: Optional[str] = None
    ) -> None:
        """
        Recursively identify and capture disabled actions BEFORE cleaning/removal.
        """
        if isinstance(node, list):
            for item in node:
                self.extract_disabled_actions(item, task_name, file_path, parent_command)
            return

        if isinstance(node, dict):
            is_action_node = "commandName" in node or "command" in node
            current_command = node.get("commandName") or node.get("command") or parent_command

            if is_action_node:
                self.raw_step_counter += 1

            if node.get("disabled") is True:
                attrs = {}
                if "attributes" in node and isinstance(node["attributes"], list):
                    attrs = simplify_attributes(node["attributes"])
                elif "attributes" in node and isinstance(node["attributes"], dict):
                    attrs = node["attributes"]

                action_name = (
                    node.get("actionName")
                    or node.get("action")
                    or attrs.get("action")
                    or (attrs.get("operation") if isinstance(attrs, dict) else None)
                    or "Execute"
                )

                self.disabled_actions.append({
                    "task": task_name,
                    "file": file_path,
                    "originalStep": self.raw_step_counter,
                    "command": current_command or "UnknownCommand",
                    "action": action_name,
                    "attributes": attrs,
                    "location": f"Line/Step {self.raw_step_counter}",
                    "parent": parent_command,
                    "reason": "Action was disabled in A360"
                })

            # Traverse child keys recursively (children, branches, nodes, etc.)
            for key, val in node.items():
                if isinstance(val, (dict, list)):
                    self.extract_disabled_actions(val, task_name, file_path, current_command if is_action_node else parent_command)

    def clean_json(self, obj):
        obj = unwrap(obj)

        if isinstance(obj, list):
            cleaned = []
            for item in obj:
                result = self.clean_json(item)
                if not remove_empty(result):
                    cleaned.append(result)
            return cleaned

        if isinstance(obj, dict):
            if should_remove_node(obj):
                return None

            cleaned = {}
            for key, value in obj.items():
                if key in REMOVE_KEYS:
                    continue

                value = unwrap(value)

                if key == "attributes" and isinstance(value, list):
                    cleaned.update(
                        simplify_attributes(value)
                    )
                    continue

                result = self.clean_json(value)
                if remove_empty(result):
                    continue

                cleaned[key] = result

            if "commandName" in cleaned:
                cleaned["command"] = cleaned.pop(
                    "commandName"
                )
                self.step_counter += 1
                cleaned["step"] = self.step_counter

            return cleaned

        return obj

    def process(
        self,
        raw_data: Any,
        task_name: str = "MainTask",
        file_path: str = ""
    ) -> Tuple[Any, List[Dict[str, Any]]]:
        """
        Full preprocessing run:
        1. Extract disabled actions before removal
        2. Clean JSON with authoritative algorithm
        Returns (cleaned_data, disabled_actions)
        """
        self.step_counter = 0
        self.raw_step_counter = 0
        self.disabled_actions = []

        # 1. Capture disabled actions
        self.extract_disabled_actions(raw_data, task_name, file_path)

        # 2. Clean
        cleaned = self.clean_json(deepcopy(raw_data))

        return cleaned, self.disabled_actions


# Standalone functions matching required interface in prompt Section 4

STEP_COUNTER = 0

def clean_json(obj):
    global STEP_COUNTER
    obj = unwrap(obj)

    if isinstance(obj, list):
        cleaned = []
        for item in obj:
            result = clean_json(item)
            if not remove_empty(result):
                cleaned.append(result)
        return cleaned

    if isinstance(obj, dict):
        if should_remove_node(obj):
            return None

        cleaned = {}
        for key, value in obj.items():
            if key in REMOVE_KEYS:
                continue

            value = unwrap(value)

            if key == "attributes" and isinstance(value, list):
                cleaned.update(
                    simplify_attributes(value)
                )
                continue

            result = clean_json(value)
            if remove_empty(result):
                continue

            cleaned[key] = result

        if "commandName" in cleaned:
            cleaned["command"] = cleaned.pop(
                "commandName"
            )
            STEP_COUNTER += 1
            cleaned["step"] = STEP_COUNTER

        return cleaned

    return obj


def cleanup_a360_json(
    input_path,
    output_path,
):
    global STEP_COUNTER
    STEP_COUNTER = 0

    input_path = Path(input_path)
    output_path = Path(output_path)

    with open(
        input_path,
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    cleaned = clean_json(
        deepcopy(data)
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            cleaned,
            f,
            indent=2,
            ensure_ascii=False,
        )


def split_json_file(
    input_file,
    output_dir="chunks",
    chunk_size=25000
):
    output_path = Path(output_dir)
    output_path.mkdir(
        exist_ok=True
    )

    content = Path(
        input_file
    ).read_text(
        encoding="utf-8"
    )

    total_chunks = (
        len(content) + chunk_size - 1
    ) // chunk_size

    for i in range(total_chunks):
        start = i * chunk_size
        end = start + chunk_size

        chunk = content[start:end]

        chunk_file = (
            output_path /
            f"chunk_{i+1:03d}_of_{total_chunks:03d}.txt"
        )

        chunk_file.write_text(
            chunk,
            encoding="utf-8"
        )
