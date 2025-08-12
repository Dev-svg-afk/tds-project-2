import os
import asyncio
import shutil
import subprocess
import aiofiles
from pathlib import Path
import json


from services.llm_utils import call_llm
from services.get_metadata import summarize_csv, summarize_json, summarize_text, summarize_image, summarize_html

async def setup(files):
    if not files:
        raise ValueError("At least one file is required.")
    file_names = [x for x,_ in (dict(files)).items()]
    file = files[file_names[0]]
    questions_txt = (await file.read()).decode("utf-8")
    with open("questions.txt", "w", encoding="utf-8") as f:
        f.write(questions_txt)

    task_breakdown_file = os.path.join("prompts", "task_breakdown.txt")
    async with aiofiles.open(task_breakdown_file, "r", encoding="utf-8") as f:
        task_breakdown_prompt = (await f.read()).strip()

    combined_prompt = f"{task_breakdown_prompt}\nTask to analyze:\n{questions_txt}"

    print("calling gemini to create tasks")
    gemini_task = asyncio.create_task(call_llm(combined_prompt, "gemini"))

    all_metadata = await warmup(files, file_names)

    gemini_response = await gemini_task

    with open("tasks.json", "w", encoding="utf-8") as resp_file:
            resp_file.write('\n'.join(gemini_response.splitlines()[1:-1]))

    return all_metadata

async def warmup(files,file_names):

    all_metadata = {}

    loop = asyncio.get_running_loop()

    if os.path.exists("codes"):
        await loop.run_in_executor(None, shutil.rmtree, "codes")

    for file in file_names:
        if "questions.txt" == file:
            continue
        async with aiofiles.open(file, "wb") as out_file:
            content = await files[file].read()
            await out_file.write(content)
            await out_file.seek(0)

            all_metadata[file] = get_metadata(file)

    print("all files set up")
    return all_metadata

def get_metadata(file_name:str):

    _, ext = os.path.splitext(file_name)

    ext = ext.lower()

    if os.path.exists(file_name):
        if ext == ".csv":
            metadata = summarize_csv(file_name)
        elif ext == ".json":
            metadata = summarize_json(file_name)
        elif ext in [".txt", ".md"]:
            metadata = summarize_text(file_name)
        elif ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"]:
            metadata = summarize_image(file_name)
        elif ext.lower() in [".html", ".htm"]:
            metadata = summarize_html(file_name)
        else:
            metadata = "file contents unknown"
    else:
        metadata = "file does not exist"

    return metadata

async def modify_task(task, metadata):
    
    metadata = await get_image_data(task, metadata)

    modify_task_file = os.path.join("prompts", "modify_task.txt")

    with open(modify_task_file, "r", encoding="utf-8") as f:
        modify_task_prompt = f.read()

    prompt = f"{modify_task_prompt}\n{task}\nStructure:{metadata}"

    print(f"modifying task")
    response = await call_llm(prompt, "gemini")

    return response

async def write_code(task,metadata=None):
    writing_prompt_file = os.path.join("prompts", "writing_code.txt")

    with open(writing_prompt_file, "r") as f:
        writing_prompt = f.read()

    if metadata:
        prompt = f"{writing_prompt}\n{task}\nFile structures:{metadata}"

    else:
        prompt = f"{writing_prompt}\n{task}"

    print(f"writing code for task {task['id']}")
    response = await call_llm(prompt, "gpt")

    code = await include_dependencies(response)

    code = quick_format(code)

    file_path = f"codes/task{task['id']}/code0.py"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as code_file:
        code_file.write(code)

    return {
        "file_path": file_path,
    }

async def include_dependencies(response):

    promp_file = os.path.join("prompts", "include_dependencies.txt")

    with open(promp_file, "r") as f:
        prompt = f.read()

    print(f"including deps")
    response = await call_llm(f"{prompt}\n{response}", "gpt")

    return response

async def execute_code(file_path: str):
    print(f"running {file_path}")
    try:
        project_root = Path(__file__).resolve().parent.parent  # points to maindir
        result = subprocess.run(
            [
                "uv", "run",
                "--directory", str(project_root),  # force use of maindir env
                file_path
            ],
            capture_output=True,
            text=True,
            check=True
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
    
async def explain_error(code_file_path:str, error: str):
    explain_error_file = os.path.join("prompts", "explain_error.txt")

    with open(code_file_path, "r", encoding="utf-8") as code_file:
        code = code_file.read()

    with open(explain_error_file, "r", encoding="utf-8") as f:
        explain_error_prompt = f.read().strip()

    prompt = f"{explain_error_prompt}\nCode:\n{code}\nError:\n{error}"

    # response = await call_llm(prompt, "gemini")
    print(f"explaining error")
    response = await call_llm(prompt, "gpt")

    return response
    
async def debug_code(task, code_file_path: str, error: str, i: int = 1, metadata=None):

    debug_prompt_path = os.path.join("prompts", "debug_code.txt")
    output_file_path = os.path.join("codes", f"task{task['id']}", f"code{i}.py")

    with open(code_file_path, "r", encoding="utf-8") as code_file:
        code = code_file.read()

    with open(debug_prompt_path, "r", encoding="utf-8") as debug_file:
        debug_prompt = debug_file.read().strip()

    error_explained = await explain_error(code_file_path, error)

    if metadata:
        prompt = f"{debug_prompt}\nCode:\n{code}\nError:\n{error}\nTask:\n{task}\nFile structures:{metadata}\nSuggested fix:{error_explained}"

    else:
        prompt = f"{debug_prompt}\nCode:\n{code}\nError:\n{error}\nTask:\n{task}\nSuggested fix:{error_explained}"


    print(f"debugging code for task {task['id']}")
    if "ImportError:" in error or "ModuleNotFoundError:" in error:
        code = await debug_dependencies(code,error.strip().split("\n")[-1])
    else:
        response = await call_llm(prompt, "gpt")
        code = await include_dependencies(response)

    code = quick_format(code)

    with open(output_file_path, "w", encoding="utf-8") as code_file:
        code_file.write(code)

    return {"message": f"Debugged code saved to {output_file_path}"}

async def debug_dependencies(response,error):

    promp_file = os.path.join("prompts", "debug_dependencies.txt")

    with open(promp_file, "r") as f:
        prompt = f.read()

    response = await call_llm(f"{prompt}\n{response}\n{error}", "gpt")

    return response

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

def get_image_base64(image_path):
    import base64
    import mimetypes
    try:
        # Guess the correct MIME type from the file extension
        mime_type, _ = mimetypes.guess_type(image_path)
        if mime_type is None:
            mime_type = "application/octet-stream"

        with open(image_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode("utf-8")

        # Return full data URI
        return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        return str(e)
    
async def get_image_data(task,metadata):
    image_files = [
        key
        for x in metadata
        for key, value in x.items()
        if f"\"type\": \"image\"" in value and x in task["files_for_reference"]
    ]

    if image_files:

        with open("prompts/get_image_prompt.txt", "r", encoding="utf-8") as f:
            get_image_prompt = f.read()

        for image in image_files:
            image_prompt = await call_llm(f"{get_image_prompt}", "gemini")
            image_base64 = get_image_base64(image)
            image_data = await call_llm(image_prompt, image_base64, "gpt")
            metadata[image] = image_data

    return metadata

def final_check(file):
    _, ext = os.path.splitext(file)

    if ext == ".json":
        with open(file, "r", encoding="utf-8") as f:
            content = json.load(f)
    else:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            
    return content
    # with open("questions.txt", "r", encoding="utf-8") as f:
    #     questions = f.read()

    # with open("prompts/final_check.txt", "r", encoding="utf-8") as f:
    #     final_check_prompt = f.read()

    # prompt = f"{final_check_prompt}\nQuestion:\n{questions}\nAnswer:\n{content}"

    # response = await call_llm(prompt, "gemini", "gemini-2.5-pro")

def quick_format(code):
    if code.startswith("```"):
        code = '\n'.join(code.splitlines()[1:])
    if code.endswith("```"):
        code = '\n'.join(code.splitlines()[:-1])
    
    return code