# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastapi",
#   "uvicorn",
#   "python-dotenv",
#   "google-generativeai",
#   "python-multipart",
#   "httpx",
#   "beautifulsoup4",
#   "playwright",
#   "pandas",
#   "asyncio",
#   "httpx",
#   "tiktoken",
#   "langgraph",
#   "langchain",
#   "langchain-openai",
#   "pydantic"
# ]
# ///

import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai

from pipelines_utils import break_tasks,write_code,execute_code,debug_code,get_metadata,write_first_code,debug_first_code,modify_task,debug_new

load_dotenv()

try:
    api_key = os.getenv("GEMINI_KEY")    
    genai.configure(api_key=api_key)

except (ValueError, Exception) as e:
    print(f"Error initializing Gemini: {e}")
    genai = None 

app = FastAPI(title="Gemini API with FastAPI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def hunt():

    try:
        with open("tasks.json", "r", encoding="utf-8") as resp_file:
            tasks = json.load(resp_file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="tasks.json not found.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding tasks.json.")

    # with open("modified_task.json", "r", encoding="utf-8") as f:
    #     task = json.load(f)

    all_metadata = {}

    for task in tasks["tasks"]:

        if task["id"]>1:

            metadata = [
                {key: value}
                for key, value in all_metadata.items()
                if key in task["files_for_reference"]
            ]

            task["description"] = await modify_task(task["description"], metadata)

        response = await write_code(task, all_metadata)
        response = await execute_code(f"codes/task{task['id']}/code0.py")

        if "error" in response:
            i = 0
            while "error" in response and i < 2:
                i += 1
                # response = await debug_new(task,f"codes/task{task['id']}/code{i-1}.py", response["stderr"],i)
                response = await debug_code(task, all_metadata, f"codes/task{task['id']}/code{i-1}.py", response["stderr"], i)
                response = await execute_code(f"codes/task{task['id']}/code{i}.py")

        if task["output_file_name"]:
            metadata = await get_metadata(task["output_file_name"])
            all_metadata[task["output_file_name"]] = metadata

    return {
        "message": "All tasks processed successfully."
    }

    all_metadata = {}

    task = tasks["tasks"][0]

    if task["output_file_name"]:
        metadata = await get_metadata(task["output_file_name"])
        if metadata == "caution: file does not exist":
            return metadata
        all_metadata[task["output_file_name"]] = metadata

    task = tasks["tasks"][1]

    response = await write_code(task, all_metadata)
    response = await execute_code(f"codes/task{task['id']}/code0.py")

    if "error" in response:
        i = 0
        with open(f"codes/task{task['id']}/error{i}.txt", "w", encoding="utf-8") as error_file:
            error_file.write(response["stderr"])
        while "error" in response and i < 2:
            i += 1
            # response = await debug_new(task,f"codes/task{task['id']}/code{i-1}.py", response["stderr"],i)
            response = await debug_code(task, all_metadata, f"codes/task{task['id']}/code{i-1}.py", response["stderr"], i)
            response = await execute_code(f"codes/task{task['id']}/code{i}.py")
            with open(f"codes/task{task['id']}/error{i}.txt", "w", encoding="utf-8") as error_file:
                error_file.write(response["stderr"])


    if task["output_file_name"]:
        metadata = await get_metadata(task["output_file_name"])
        if metadata == "caution: file does not exist":
            return metadata
        all_metadata[task["output_file_name"]] = metadata

    return all_metadata

# API Endpoints

@app.get("/")
async def root():
    if not genai:
        raise HTTPException(status_code=500, detail="Gemini client not initialized.")
    return {"message": "Welcome to the Gemini FastAPI Server!"}

@app.post("/api")
async def api(file: UploadFile = File(...)):
    # response = await break_tasks(file)
    response = await hunt()
    return response


if __name__ == "__main__":
    import uvicorn
    import json
    print("Starting server at http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)