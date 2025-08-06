import os
import subprocess
from fastapi import UploadFile, HTTPException
import json

from llm_utils import call_gpt, call_gemini
import shutil

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
            # resp_file.write(response)

        return {
            "message": "Response saved to tasks.json"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

async def write_code(task):

    # shutil.rmtree("codes", ignore_errors=True) #dangerous

    writing_code_file = os.path.join("prompts", "writing_code.txt")

    with open(writing_code_file, "r") as f:
        writing_code_prompt = f.read()

    prompt = f"{writing_code_prompt}\n{task}"
    
    response = await call_gpt(prompt)

    file_path = f"codes/task{task['id']}/code.py"
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
            ["python", file_path],
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
    
async def debug_code(task, code_file_path:str, error: str, i: int = 1):
    
    debug_prompt = os.path.join("prompts", "debug_code.txt")
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

async def get_metadata(code_file_path:str):
    try:
        with open(code_file_path, "r", encoding="utf-8") as code_file:
            code = code_file.read()

        get_metadata_prompt = os.path.join("prompts", "get_metadata.txt")

        response = await call_gpt(f"{get_metadata_prompt}\n{code}")

        with open("metadata.json", "w", encoding="utf-8") as metadata_file:
            json.dump(response, metadata_file, ensure_ascii=False, indent=4)

        return {
            "response": "saved to metadata.json"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")