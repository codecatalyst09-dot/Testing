from typing import List, Dict, Any, Set
from backend.models.workflow import DependencyModel
from backend.models.action import ActionModel

class DependencyAnalyzer:
    @staticmethod
    def extract_dependencies(actions: List[ActionModel]) -> List[DependencyModel]:
        dep_dict: Dict[str, DependencyModel] = {}

        def add_dep(name: str, dep_type: str, step: int, task: str, desc: str, pa_mech: str):
            if name not in dep_dict:
                dep_dict[name] = DependencyModel(
                    name=name,
                    type=dep_type,
                    requiredByTasks=[task],
                    requiredBySteps=[step],
                    description=desc,
                    suggestedPAMechanism=pa_mech
                )
            else:
                dep = dep_dict[name]
                if task not in dep.requiredByTasks:
                    dep.requiredByTasks.append(task)
                if step not in dep.requiredBySteps:
                    dep.requiredBySteps.append(step)

        for a in actions:
            cmd = a.command.lower()
            op = (a.operation or "").lower()
            attrs = a.attributes or {}
            attr_str = str(attrs).lower()

            # Excel
            if "excel" in cmd:
                add_dep(
                    name="Microsoft Excel Desktop",
                    dep_type="Application",
                    step=a.step,
                    task=a.task,
                    desc="Local Microsoft Office Excel installation for spreadsheet processing.",
                    pa_mech="Power Automate Desktop Excel actions (Launch Excel / Read/Write)"
                )

            # Web Browser
            if "browser" in cmd or "web" in cmd or "html" in cmd or "url" in attr_str:
                browser_name = "Microsoft Edge / Google Chrome"
                if "chrome" in attr_str:
                    browser_name = "Google Chrome"
                elif "edge" in attr_str:
                    browser_name = "Microsoft Edge"
                add_dep(
                    name=browser_name,
                    dep_type="Browser",
                    step=a.step,
                    task=a.task,
                    desc="Web browser runtime with Power Automate browser extension installed.",
                    pa_mech="Launch new Microsoft Edge / Chrome in PAD"
                )

            # HTTP / REST APIs
            if "http" in cmd or "rest" in cmd or "api" in cmd:
                uri = attrs.get("url") or attrs.get("uri") or "REST API Endpoint"
                add_dep(
                    name=f"External API ({str(uri)[:40]})",
                    dep_type="API",
                    step=a.step,
                    task=a.task,
                    desc="REST/HTTP API web service endpoint.",
                    pa_mech="HTTP Action in Power Automate Cloud Flow"
                )

            # Email / Outlook
            if "email" in cmd or "outlook" in cmd or "mail" in cmd:
                add_dep(
                    name="Office 365 Outlook Mailbox",
                    dep_type="API",
                    step=a.step,
                    task=a.task,
                    desc="Exchange / Office 365 Outlook account for automated email handling.",
                    pa_mech="Office 365 Outlook Connector in Cloud Flow"
                )

            # Database / SQL
            if "database" in cmd or "sql" in cmd:
                add_dep(
                    name="Database (SQL / ODBC)",
                    dep_type="Database",
                    step=a.step,
                    task=a.task,
                    desc="Relational database connection.",
                    pa_mech="SQL Server Connector (Cloud) or Execute SQL Statement (PAD)"
                )

            # SAP GUI
            if "sap" in cmd:
                add_dep(
                    name="SAP GUI Client",
                    dep_type="Desktop Software",
                    step=a.step,
                    task=a.task,
                    desc="SAP GUI client with scripting enabled on both client and SAP server.",
                    pa_mech="Power Automate Desktop SAP GUI actions"
                )

            # Local File System
            if "file" in cmd or "folder" in cmd or "csv" in cmd:
                add_dep(
                    name="Local File System / Storage Path",
                    dep_type="File",
                    step=a.step,
                    task=a.task,
                    desc="Host file system read/write permissions for document storage.",
                    pa_mech="PAD File actions or OneDrive/SharePoint Cloud Connector"
                )

            # Credentials
            if "credential" in attr_str or "locker" in attr_str or "password" in attr_str:
                add_dep(
                    name="A360 Credential Locker",
                    dep_type="Credential",
                    step=a.step,
                    task=a.task,
                    desc="Secure credential storage for bot authentication.",
                    pa_mech="Azure Key Vault or Power Automate Environment Variable (Secret type)"
                )

            # Scripts (PowerShell / VBScript / Python)
            if "script" in cmd or "powershell" in cmd or "vbs" in cmd or "python" in cmd:
                script_type = "PowerShell / VBScript Runtime"
                if "python" in cmd:
                    script_type = "Python 3 Runtime"
                elif "powershell" in cmd:
                    script_type = "PowerShell 5.1 / 7"
                add_dep(
                    name=script_type,
                    dep_type="Desktop Software",
                    step=a.step,
                    task=a.task,
                    desc="Local script execution environment.",
                    pa_mech="PAD Run PowerShell / Run VBScript / Run Python script"
                )

        return sorted(list(dep_dict.values()), key=lambda x: x.name)
