import pytest
from backend.services.a360_preprocessor import (
    A360Preprocessor,
    unwrap,
    simplify_attributes,
    remove_empty,
    should_remove_node
)

def test_unwrap_single_key_wrappers():
    assert unwrap({"string": "Hello"}) == "Hello"
    assert unwrap({"number": 42}) == 42
    assert unwrap({"boolean": True}) is True
    assert unwrap({"value": {"string": "Nested"}}) == "Nested"
    assert unwrap("plain_string") == "plain_string"

def test_simplify_attributes():
    raw_attrs = [
        {"name": "filePath", "value": {"string": "C:\\test.xlsx"}},
        {"name": "timeout", "value": {"number": 30}},
        {"name": "enabled", "value": {"boolean": True}}
    ]
    simplified = simplify_attributes(raw_attrs)
    assert simplified == {
        "filePath": "C:\\test.xlsx",
        "timeout": 30,
        "enabled": True
    }

def test_remove_empty():
    assert remove_empty(None) is True
    assert remove_empty({}) is True
    assert remove_empty([]) is True
    assert remove_empty("") is True
    assert remove_empty("valid") is False
    assert remove_empty(0) is False
    assert remove_empty(False) is False

def test_should_remove_node():
    assert should_remove_node({"commandName": "Comment"}) is True
    assert should_remove_node({"commandName": "messageBox"}) is True
    assert should_remove_node({"commandName": "logToFile"}) is True
    assert should_remove_node({"commandName": "SetTitle"}) is True
    assert should_remove_node({"commandName": "Excel", "disabled": True}) is True
    assert should_remove_node({"commandName": "Excel", "disabled": False}) is False

def test_preprocessor_disabled_action_detection():
    preprocessor = A360Preprocessor()
    test_json = {
        "nodes": [
            {
                "commandName": "Excel",
                "disabled": True,
                "attributes": [
                    {"name": "filePath", "value": {"string": "C:\\legacy.xls"}},
                    {"name": "action", "value": {"string": "Open"}}
                ]
            },
            {
                "commandName": "Excel",
                "disabled": False,
                "attributes": [
                    {"name": "filePath", "value": {"string": "C:\\active.xlsx"}},
                    {"name": "action", "value": {"string": "Open"}}
                ]
            }
        ]
    }

    cleaned, disabled_actions = preprocessor.process(test_json, task_name="InvoiceBot", file_path="InvoiceBot.json")

    # Disabled action must be recorded BEFORE removal
    assert len(disabled_actions) == 1
    assert disabled_actions[0]["command"] == "Excel"
    assert disabled_actions[0]["action"] == "Open"
    assert disabled_actions[0]["reason"] == "Action was disabled in A360"
    assert disabled_actions[0]["task"] == "InvoiceBot"

    # In cleaned output, disabled action must be removed
    nodes = cleaned.get("nodes", [])
    assert len(nodes) == 1
    assert nodes[0]["command"] == "Excel"
    assert nodes[0]["filePath"] == "C:\\active.xlsx"
    assert nodes[0]["step"] == 1

def test_preprocessor_comment_and_logging_removal():
    preprocessor = A360Preprocessor()
    test_json = {
        "nodes": [
            {"commandName": "Comment", "attributes": [{"name": "text", "value": {"string": "test"}}]},
            {"commandName": "messageBox", "attributes": [{"name": "msg", "value": {"string": "popup"}}]},
            {"commandName": "HTTP", "attributes": [{"name": "url", "value": {"string": "https://api.test.com"}}]},
            {"commandName": "logToFile", "attributes": [{"name": "log", "value": {"string": "audit"}}]}
        ]
    }
    cleaned, _ = preprocessor.process(test_json)
    nodes = cleaned.get("nodes", [])
    assert len(nodes) == 1
    assert nodes[0]["command"] == "HTTP"
    assert nodes[0]["step"] == 1
