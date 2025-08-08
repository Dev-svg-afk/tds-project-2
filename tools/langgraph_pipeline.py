from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import json
from task_utils import break_tasks, write_code, execute_code, debug_code, get_metadata
import asyncio

# ------------------------
# Define the State schema
# ------------------------

class WorkflowState(TypedDict):
    file: Optional[object]         # UploadFile
    tasks: Optional[List[dict]]
    current_task: Optional[dict]
    task_index: int
    code_path: Optional[str]
    execution_result: Optional[dict]

# ---------------------
# Define LangGraph nodes
# ---------------------

async def node_break_tasks(state: WorkflowState) -> WorkflowState:
    await break_tasks(state["file"])

    with open("tasks.json", "r", encoding="utf-8") as f:
        tasks = [json.loads(line) for line in f.readlines()]
    
    return {**state, "tasks": tasks, "task_index": 0}

async def node_write_code(state: WorkflowState) -> WorkflowState:
    task = state["tasks"][state["task_index"]]
    result = await write_code(task)
    return {**state, "current_task": task, "code_path": result["file_path"]}

async def node_execute_code(state: WorkflowState) -> WorkflowState:
    result = await execute_code(state["code_path"])
    return {**state, "execution_result": result}

async def node_debug_code(state: WorkflowState) -> WorkflowState:
    error = state["execution_result"]["stderr"]
    index = state["task_index"]
    task = state["tasks"][index]
    await debug_code(task, state["code_path"], error, i=1)
    return {**state, "code_path": f"codes/task{task['id']}/code1.py"}

async def node_extract_metadata(state: WorkflowState) -> WorkflowState:
    await get_metadata(state["code_path"])
    return state

def should_debug(state: WorkflowState) -> str:
    result = state["execution_result"]
    if result.get("returncode", 1) != 0:
        return "debug"
    return "next_task"

def should_continue(state: WorkflowState) -> str:
    if state["task_index"] + 1 < len(state["tasks"]):
        return "write_code"
    return "extract_metadata"

def increment_index(state: WorkflowState) -> WorkflowState:
    return {**state, "task_index": state["task_index"] + 1}

# ---------------------
# Build the graph
# ---------------------

graph = StateGraph(WorkflowState)

graph.add_node("break_tasks", node_break_tasks)
graph.add_node("write_code", node_write_code)
graph.add_node("execute_code", node_execute_code)
graph.add_node("debug_code", node_debug_code)
graph.add_node("extract_metadata", node_extract_metadata)
graph.add_node("increment_index", increment_index)

graph.set_entry_point("break_tasks")

graph.add_edge("break_tasks", "write_code")
graph.add_edge("write_code", "execute_code")

graph.add_conditional_edges("execute_code", should_debug, {
    "debug": "debug_code",
    "next_task": "increment_index"
})

graph.add_edge("debug_code", "execute_code")
graph.add_edge("increment_index", should_continue)
graph.add_edge("extract_metadata", END)

app = graph.compile()
