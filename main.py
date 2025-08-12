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
#   "pydantic",
#   "aiofiles",
#   "pillow",
# ]
# ///

import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List

from services.pipelines_utils import setup, write_code, execute_code, debug_code, get_metadata, modify_task

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


async def analyze(all_metadata):

    try:
        with open("tasks.json", "r", encoding="utf-8") as resp_file:
            tasks = json.load(resp_file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="tasks.json not found.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding tasks.json.")


    for task in tasks["tasks"]:
        
        metadata = []

        if task["files_for_reference"]:

            metadata = [
                {key: value}
                for key, value in all_metadata.items()
                if key in task["files_for_reference"]
            ]

            task["files_for_reference"] = [
                key
                for x in metadata
                for key, value in x.items()
                if value != "file does not exist"
            ]

            task["description"] = await modify_task(task["description"], metadata)


        response = await write_code(task, metadata)

        response = await execute_code(f"codes/task{task['id']}/code0.py")

        if response["returncode"] != 0:
            i = 0
            with open(f"codes/task{task['id']}/error{i}.txt", "w", encoding="utf-8") as error_file:
                error_file.write(response["stderr"])  # FOR TESTING PURPOSES ONLY
            while response["returncode"] != 0 and i < 2:
                i += 1
                response = await debug_code(task, f"codes/task{task['id']}/code{i-1}.py", response["stderr"], i, metadata)
                response = await execute_code(f"codes/task{task['id']}/code{i}.py")
                if response["returncode"] != 0:
                    with open(f"codes/task{task['id']}/error{i}.txt", "w", encoding="utf-8") as error_file:
                        error_file.write(response["stderr"])  # FOR TESTING PURPOSES ONLY

            if response["returncode"] != 0:
                return "Task processed unsuccessfully"  # FOR TESTING PURPOSES ONLY

        if task["output_file_name"]:
            metadata = get_metadata(task["output_file_name"])
            all_metadata[task["output_file_name"]] = metadata

    return tasks["tasks"][-1]["output_file_name"]

# API Endpoints

@app.get("/")
async def root():
    return {"Server": "Healthy"}

@app.post("/api")
async def api(request: Request):
    form = await request.form()
    # all_metadata = await setup(form)
    final_result = await analyze({})

    # read the file with respect to its extension
    output_file_name = final_result
    _, ext = os.path.splitext(output_file_name)

    if ext == ".json":
        with open(output_file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    else:
        with open(output_file_name, "r", encoding="utf-8") as f:
            content = f.read()
            return content

if __name__ == "__main__":
    import uvicorn
    import json
    print("Starting server at http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

# if __name__ == "__main__":
#     import uvicorn
#     import json
#     print("Starting server at http://0.0.0.0:8000")
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000) # for production