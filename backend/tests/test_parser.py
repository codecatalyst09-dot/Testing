import json
from pathlib import Path
from backend.services.a360_preprocessor import A360Preprocessor
from backend.services.a360_parser import A360Parser

def test_parser_nested_actions_and_loops():
    raw_json = {
        "name": "OrderProcessor",
        "variables": [
            {"name": "OrderNumber", "type": "String", "input": True},
            {"name": "ItemsList", "type": "List", "input": False}
        ],
        "nodes": [
            {
                "commandName": "Loop",
                "attributes": [{"name": "collection", "value": {"string": "$ItemsList$"}}],
                "children": [
                    {
                        "commandName": "If",
                        "attributes": [{"name": "condition", "value": {"string": "$OrderNumber$ == ''"}}],
                        "children": [
                            {
                                "commandName": "HTTP",
                                "attributes": [{"name": "url", "value": {"string": "https://api.orders.com/validate"}}]
                            }
                        ]
                    }
                ]
            }
        ]
    }

    preprocessor = A360Preprocessor()
    cleaned, disabled = preprocessor.process(raw_json, "OrderProcessor", "OrderProcessor.json")

    parser = A360Parser()
    wf = parser.parse(
        cleaned_taskbots_data=[("OrderProcessor", "OrderProcessor.json", cleaned)],
        raw_data_map={"OrderProcessor": raw_json},
        disabled_actions=disabled,
        workflow_id="wf-test",
        workflow_name="OrderProcessor"
    )

    assert wf.statistics.totalActions == 3
    assert len(wf.variables) >= 2
    var_names = [v.name for v in wf.variables]
    assert "OrderNumber" in var_names
    assert "ItemsList" in var_names

    # Check parent-child hierarchy
    loop_act = next(a for a in wf.actions if a.command == "Loop")
    assert len(loop_act.children) == 1
    if_act_id = loop_act.children[0]
    if_act = next(a for a in wf.actions if a.id == if_act_id)
    assert if_act.command == "If"
    assert len(if_act.children) == 1
    http_act = next(a for a in wf.actions if a.id == if_act.children[0])
    assert http_act.command == "HTTP"

def test_parser_subtask_and_task_relationships():
    main_task_json = {
        "nodes": [
            {
                "commandName": "runTask",
                "attributes": [{"name": "taskbot", "value": {"string": "SubWorker"}}]
            }
        ]
    }
    sub_task_json = {
        "nodes": [
            {
                "commandName": "Excel",
                "attributes": [{"name": "action", "value": {"string": "Open"}}]
            }
        ]
    }

    p = A360Preprocessor()
    main_clean, d1 = p.process(main_task_json, "MainTask", "MainTask.json")
    sub_clean, d2 = p.process(sub_task_json, "SubWorker", "SubWorker.json")

    parser = A360Parser()
    wf = parser.parse(
        cleaned_taskbots_data=[
            ("MainTask", "MainTask.json", main_clean),
            ("SubWorker", "SubWorker.json", sub_clean)
        ],
        raw_data_map={"MainTask": main_task_json, "SubWorker": sub_task_json},
        disabled_actions=d1 + d2,
        workflow_id="wf-sub-test",
        workflow_name="MultiTaskBot"
    )

    assert len(wf.tasks) == 2
    main_t = next(t for t in wf.tasks if t.name == "MainTask")
    sub_t = next(t for t in wf.tasks if t.name == "SubWorker")
    assert "SubWorker" in main_t.subtasks
    assert sub_t.parentTask == "MainTask"
