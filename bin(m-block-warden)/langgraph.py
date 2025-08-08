# langgraph_app.py
import json
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any

# Import your existing functions
from pipelines_utils import (
    write_code, execute_code, debug_code, get_metadata, modify_task
)

# ---------- STATE DEFINITION ----------
class WorkflowState(TypedDict):
    tasks: List[Dict[str, Any]]
    task_index: int
    all_metadata: Dict[str, Any]
    response: Dict[str, Any]
    debug_attempts: int

# ---------- NODES ----------
async def load_tasks(state: WorkflowState) -> WorkflowState:
    with open("tasks.json", "r", encoding="utf-8") as resp_file:
        tasks = json.load(resp_file)["tasks"]

    return {
        "tasks": tasks,
        "task_index": 0,
        "all_metadata": {},
        "response": {},
        "debug_attempts": 0
    }

async def modify_task_node(state: WorkflowState) -> WorkflowState:
    task = state["tasks"][state["task_index"]]
    if task["id"] > 1:
        metadata = [
            {key: value}
            for key, value in state["all_metadata"].items()
            if key in task["files_for_reference"]
        ]
        task["description"] = await modify_task(task["description"], metadata)
    return state

async def write_node(state: WorkflowState) -> WorkflowState:
    task = state["tasks"][state["task_index"]]
    state["response"] = await write_code(task, state["all_metadata"])
    return state

async def execute_node(state: WorkflowState) -> WorkflowState:
    task = state["tasks"][state["task_index"]]
    file_path = f"codes/task{task['id']}/code{state['debug_attempts']}.py"
    state["response"] = await execute_code(file_path)
    return state

async def debug_node(state: WorkflowState) -> WorkflowState:
    task = state["tasks"][state["task_index"]]
    file_path = f"codes/task{task['id']}/code{state['debug_attempts']}.py"
    err = state["response"]["stderr"]
    state["debug_attempts"] += 1
    state["response"] = await debug_code(task, state["all_metadata"], file_path, err, state["debug_attempts"])
    return state

async def get_metadata_node(state: WorkflowState) -> WorkflowState:
    task = state["tasks"][state["task_index"]]
    if task["output_file_name"]:
        metadata = await get_metadata(task["output_file_name"])
        state["all_metadata"][task["output_file_name"]] = metadata
    return state

async def next_task_or_end(state: WorkflowState) -> WorkflowState:
    state["task_index"] += 1
    state["debug_attempts"] = 0
    return state

# ---------- CONDITIONALS ----------
def need_debug(state: WorkflowState) -> str:
    if "error" in state["response"]:
        if state["debug_attempts"] < 2:
            return "debug"
    return "get_metadata"

def more_tasks(state: WorkflowState) -> str:
    if state["task_index"] < len(state["tasks"]):
        return "modify_task"
    return END

# ---------- BUILD GRAPH ----------
workflow = StateGraph(WorkflowState)

workflow.add_node("load_tasks", load_tasks)
workflow.add_node("modify_task", modify_task_node)
workflow.add_node("write", write_node)
workflow.add_node("execute", execute_node)
workflow.add_node("debug", debug_node)
workflow.add_node("get_metadata", get_metadata_node)
workflow.add_node("next_task", next_task_or_end)

# Entry point
workflow.set_entry_point("load_tasks")

# Edges for flow
workflow.add_edge("load_tasks", "modify_task")
workflow.add_edge("modify_task", "write")
workflow.add_edge("write", "execute")

workflow.add_conditional_edges("execute", need_debug, {
    "debug": "debug",
    "get_metadata": "get_metadata"
})

workflow.add_edge("debug", "execute")
workflow.add_edge("get_metadata", "next_task")
workflow.add_conditional_edges("next_task", more_tasks, {
    "modify_task": "modify_task",
    END: END
})

app = workflow.compile()

# ---------- RUN ----------
if __name__ == "__main__":
    import asyncio
    result = asyncio.run(app.ainvoke({}))
    print("Workflow finished:", result)
