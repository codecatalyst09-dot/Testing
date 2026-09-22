import pytest
from backend.migration.classifier import ActionClassifier
from backend.migration.mapping_engine import MappingEngine

def test_cloud_action_classification():
    platform, reason, conf = ActionClassifier.classify_action("HTTP")
    assert platform == "Power Automate Cloud"
    assert conf >= 0.90

    platform, reason, conf = ActionClassifier.classify_action("SendEmail")
    assert platform == "Power Automate Cloud"

    platform, reason, conf = ActionClassifier.classify_action("SharePoint")
    assert platform == "Power Automate Cloud"

def test_desktop_action_classification():
    platform, reason, conf = ActionClassifier.classify_action("Excel", "Open")
    assert platform == "Power Automate Desktop"
    assert "Excel" in reason

    platform, reason, conf = ActionClassifier.classify_action("Browser", "Launch")
    assert platform == "Power Automate Desktop"

    platform, reason, conf = ActionClassifier.classify_action("SAP", "ExecuteTransaction")
    assert platform == "Power Automate Desktop"

def test_hybrid_classification():
    platform, reason, conf = ActionClassifier.classify_action(
        command="runTask",
        context_has_cloud=True,
        context_has_desktop=True
    )
    assert platform == "Hybrid"
    assert "desktop" in reason.lower()

def test_unknown_command_policy():
    # Unknown commands must NEVER be silently ignored.
    # Must be categorized as Manual Review with details.
    mapped = MappingEngine.map_action(
        command="SomeSuperProprietaryA360CommandV99",
        attributes={"param1": "val1"}
    )
    assert mapped["targetPlatform"] == "Manual Review"
    assert mapped["strategy"] == "Manual Review"
    assert mapped["complexity"] == "High"
    assert "Manual Review" in mapped["targetAction"]
    assert len(mapped["manualSteps"]) > 0
    assert "proprietary" in mapped["reason"].lower() or "unknown" in mapped["reason"].lower()

def test_excel_detailed_mapping():
    mapped_open = MappingEngine.map_action("Excel", operation="Open", attributes={"filePath": "C:\\book.xlsx"})
    assert mapped_open["targetPlatform"] == "Power Automate Desktop"
    assert mapped_open["targetAction"] == "Launch Excel"
    assert mapped_open["complexity"] == "Low"

    mapped_read = MappingEngine.map_action("Excel", operation="Read", attributes={"cell": "A1"})
    assert mapped_read["targetAction"] == "Read from Excel worksheet"
