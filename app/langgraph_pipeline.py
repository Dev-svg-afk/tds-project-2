from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import asyncio

# this is gtps:
# class GlobalState(BaseModel):
#     task_queue: List[Dict[str, Any]]
#     current_task: Optional[Dict[str, Any]]
#     file_path: Optional[str] = None
#     step: Optional[str] = None
#     execution_result: Optional[Dict[str, Any]] = None
#     retry_count: int = 0
#     debug_files: List[str] = Field(default_factory=list)

class GlobalState(BaseModel):
    tasks: List[Dict[str, Any]]
    file_path: Optional[str] = None
    step: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    debug_files: List[str] = Field(default_factory=list)


def write_code_node(state: GlobalState) -> GlobalState:
    task = state.current_task
    file_path = f"python/code{task['id']}.py"
    return state.model_copy(update={
        "file_path": file_path,
        "step": "written"
    })


def execute_code_node(state: GlobalState) -> GlobalState:
    file_path = state.file_path
    result = asyncio.run(execute_code(file_path))
    return state.model_copy(update={
        "execution_result": result,
        "step": "executed"
    })


def debug_code_node(state: GlobalState) -> GlobalState:
    task_id = state.current_task["id"]
    error = state.execution_result.get("error", "Unknown error")
    debug_file = f"python/debugged{task_id}_{state.retry_count}.py"
    asyncio.run(debug_code(state.file_path, error, debug_file))
    return state.model_copy(update={
        "file_path": debug_file,
        "step": "debugged",
        "retry_count": state.retry_count + 1,
        "debug_files": state.debug_files + [debug_file]
    })


def load_next_task_node(state: GlobalState) -> GlobalState:
    if state.task_queue:
        next_task = state.task_queue[0]
        return state.model_copy(update={
            "current_task": state.task_queue.pop(0),
            "retry_count": 0,  # reset retries for next task
            "step": "loaded"
        })
    else:
        return END


def decide_next_node(state: GlobalState) -> str:
    result = state.execution_result or {}
    if "error" in result:
        if state.retry_count >= 3:
            return "load_next_task"  # give up and continue
        return "debug_code"
    return "load_next_task"


builder = StateGraph(GlobalState)

builder.add_node("write_code", write_code_node)
builder.add_node("execute_code", execute_code_node)
builder.add_node("debug_code", debug_code_node)
builder.add_node("load_next_task", load_next_task_node)

builder.set_entry_point("write_code")

builder.add_edge("write_code", "execute_code")
builder.add_conditional_edges("execute_code", decide_next_node)
builder.add_edge("debug_code", "execute_code")
builder.add_edge("load_next_task", "write_code")

graph = builder.compile()

# async def run_graph(tasks: List[Dict[str, Any]]):
#     initial_state = GlobalState(
#         task_queue=tasks[1:],  # queue
#         current_task=tasks[0],  # start with first
#     )
#     final_state = await graph.ainvoke(initial_state)
#     return final_state
