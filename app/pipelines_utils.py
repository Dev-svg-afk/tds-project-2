import os
import subprocess
from fastapi import UploadFile, HTTPException
import glob
import json

from llm_utils import call_gpt, call_gemini
from get_metadata import summarize_csv, summarize_json, summarize_text

async def break_tasks(file: UploadFile):
    try:
        contents = await file.read()
        task = contents.decode("utf-8")

        task_breakdown_file = os.path.join("prompts", "task_breakdown.txt")
         
        with open(task_breakdown_file, "r") as f:   
            task_breakdown_prompt = f.read().strip()

        combined_prompt = f"{task_breakdown_prompt}\nTask to analyze:\n{task}"

        response = await call_gemini(combined_prompt)

        with open("tasks.json", "w", encoding="utf-8") as resp_file:
            resp_file.write('\n'.join(response.splitlines()[1:-1]))

        return {
            "message": "Response saved to tasks.json"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

async def write_first_code(task):

    # shutil.rmtree("codes", ignore_errors=True) #dangerous

    writing_code_file = os.path.join("prompts", "writing_first_code.txt")

    with open(writing_code_file, "r") as f:
        writing_code_prompt = f.read()

    prompt = f"{writing_code_prompt}\n{task}"
    
    response = await call_gpt(prompt)

    file_path = f"codes/task{task['id']}/code0.py"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as code_file:
        code = '\n'.join(response.splitlines()[1:-1])
        code_file.write(code)

    return {
        "file_path": file_path,
    }

async def write_code_old(task,ref_file_path=None,structure_file=None):
    writing_code_file = os.path.join("prompts", "writing_code.txt")

    with open(writing_code_file, "r") as f:
        writing_code_prompt = f.read()

    with open(structure_file, "r", encoding="utf-8") as f:
        ref_file_structure = json.load(f)

    prompt = f"{writing_code_prompt}\n{task}\nReferenceFile:{ref_file_path}\nStructure:{ref_file_structure}"

    response = await call_gpt(prompt)
    
    file_path = f"codes/task{task['id']}/code0.py"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as code_file:
        code = '\n'.join(response.splitlines()[1:-1])
        code_file.write(code)

    return {
        "file_path": file_path,
    }

async def write_code(task,all_metadata):
    writing_prompt_file = os.path.join("prompts", "writing_code.txt")

    with open(writing_prompt_file, "r") as f:
        writing_prompt = f.read()

    if task["files_for_reference"]:
        metadata = [
            {key: value}
            for key, value in all_metadata.items()
            if key in task["files_for_reference"]
        ]
        prompt = f"{writing_prompt}\n{task}\nFile structures:{metadata}"

    else:
        prompt = f"{writing_prompt}\n{task}"

    response = await call_gpt(prompt)
    
    file_path = f"codes/task{task['id']}/code0.py"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as code_file:
        code = '\n'.join(response.splitlines()[1:-1])
        code_file.write(code)

    return {
        "file_path": file_path,
    }

async def execute_code(file_path: str):
    try:
        result = subprocess.run(
            ["uv", "run", file_path],
            capture_output=True,  # Capture stdout and stderr
            text=True,            # Decode output as text
            check=True            # Raise CalledProcessError on non-zero exit code
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

    except subprocess.CalledProcessError as e:
        return {
            "error": str(e),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode
        }
    
async def debug_first_code(task, code_file_path:str, error: str, i: int = 1):
    
    debug_prompt = os.path.join("prompts", "debug_first_code.txt")
    output_file_path = os.path.join("codes", f"task{task['id']}", f"code{i}.py")

    with open(code_file_path, "r", encoding="utf-8") as code_file:
        code = code_file.read()

    with open(debug_prompt, "r", encoding="utf-8") as debug_file:
        debug_prompt = debug_file.read().strip()

    response = await call_gpt(f"{debug_prompt}\nTask:\n{task}\nCode:\n{code}\nError:\n{error}")

    with open(output_file_path, "w", encoding="utf-8") as code_file:
        code = '\n'.join(response.splitlines()[1:-1])
        code_file.write(code)

    return {"message": f"Debugged code saved to {output_file_path}"}

async def debug_code_old(task, code_file_path: str, error: str, i: int = 1, ref_file_path=None, structure_file=None):
    debug_prompt = os.path.join("prompts", "debug_code.txt")
    output_file_path = os.path.join("codes", f"task{task['id']}", f"code{i}.py")

    with open(code_file_path, "r", encoding="utf-8") as code_file:
        code = code_file.read()

    with open(debug_prompt, "r", encoding="utf-8") as debug_file:
        debug_prompt = debug_file.read().strip()

    with open(structure_file, "r", encoding="utf-8") as f:
        ref_file_structure = json.load(f)

    response = await call_gpt(f"{debug_prompt}\nCode:\n{code}\nError:\n{error}\nTask:\n{task}\nReference File: {ref_file_path}\nStructure: {ref_file_structure}")

    with open(output_file_path, "w", encoding="utf-8") as code_file:
        code = '\n'.join(response.splitlines()[1:-1])
        code_file.write(code)

    return {"message": f"Debugged code saved to {output_file_path}"}

async def debug_code(task, all_metadata, code_file_path: str, error: str, i: int = 1):
    debug_prompt_path = os.path.join("prompts", "debug_code.txt")
    output_file_path = os.path.join("codes", f"task{task['id']}", f"code{i}.py")

    with open(code_file_path, "r", encoding="utf-8") as code_file:
        code = code_file.read()

    with open(debug_prompt_path, "r", encoding="utf-8") as debug_file:
        debug_prompt = debug_file.read().strip()

    if task["files_for_reference"]:
        metadata = [
            {key: value}
            for key, value in all_metadata.items()
            if key in task["files_for_reference"]
        ]
        prompt = f"{debug_prompt}\nCode:\n{code}\nError:\n{error}\nTask:\n{task}\nFile structures:{metadata}"

    else:
        prompt = f"{debug_prompt}\nCode:\n{code}\nError:\n{error}\nTask:\n{task}"

    response = await call_gpt(prompt)

    with open(output_file_path, "w", encoding="utf-8") as code_file:
        code = '\n'.join(response.splitlines()[1:-1])
        code_file.write(code)

    return {"message": f"Debugged code saved to {output_file_path}"}

async def debug_new(task, code_file_path:str, error: str, i: int = 1):
    
    debug_file = os.path.join("prompts", "debug_new.txt")
    output_file_path = os.path.join("codes", f"task{task['id']}", f"code{i}.py")

    with open(code_file_path, "r", encoding="utf-8") as code_file:
        code = code_file.read()

    with open(debug_file, "r", encoding="utf-8") as f:
        debug_prompt = f.read().strip()

    # error_explained = await explain_error(code_file_path, error)
    # return error_explained

    response = await call_gpt(f"{debug_prompt}\nCode:\n{code}\nError:\n{error}")

    with open(output_file_path, "w", encoding="utf-8") as code_file:
        code = '\n'.join(response.splitlines()[1:-1])
        code_file.write(code)

    return {"message": f"Debugged code saved to {output_file_path}"}

async def explain_error(code_file_path:str, error: str):
    explain_error_file = os.path.join("prompts", "explain_error.txt")

    with open(code_file_path, "r", encoding="utf-8") as code_file:
        code = code_file.read()

    with open(explain_error_file, "r", encoding="utf-8") as f:
        explain_error_prompt = f.read().strip()

    response = await call_gemini(f"{explain_error_prompt}\nCode:\n{code}\nError:\n{error}")

    return response

async def get_metadata(file_name:str):

    _, ext = os.path.splitext(file_name)

    ext = ext.lower()

    if os.path.exists(file_name):
        if ext == ".csv":
            metadata = summarize_csv(file_name)
        elif ext == ".json":
            metadata = summarize_json(file_name)
        elif ext in [".txt", ".md"]:
            metadata = summarize_text(file_name)
        else:
            metadata = "file contents unknown"
    else:
        metadata = "caution: file does not exist"

    return metadata
    
    # metadata_file = "basicStructure.json"

    # with open(metadata_file, "w", encoding="utf-8") as f:
    #     f.write(metadata)

    # return {"message": "Metadata generated successfully"}

async def modify_task(task, metadata):
    modify_task_file = os.path.join("prompts", "modify_task.txt")

    with open(modify_task_file, "r", encoding="utf-8") as f:
        modify_task_prompt = f.read()

    prompt = f"{modify_task_prompt}\n{task}\nStructure:{metadata}"

    response = await call_gemini(prompt)

    return response
