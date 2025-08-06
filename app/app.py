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
#   "asyncio",
#   "httpx",
#   "tiktoken",
#   "langgraph",
#   "langchain",
#   "langchain-openai",
#   "pydantic",
#   "pandas",
#   "requests",
# ]
# ///

import os
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai

from pipelines_utils import break_tasks,write_code,execute_code,debug_code,get_metadata


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

# Agent

async def agent():

    try:
        with open("tasks.json", "r", encoding="utf-8") as resp_file:
            tasks = json.load(resp_file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="tasks.json not found.")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding tasks.json.")

    
    for task in tasks["tasks"]:
        response = await write_code(task)
        response = await execute_code(f"codes/task{task['id']}/code.py")

        if "error" in response:
            i = 0
            while "error" in response and i < 2:
                i += 1
                response = await debug_code(task,f"codes/task{task['id']}/code.py", response["error"],i)
                response = await execute_code(f"codes/task{task['id']}/code{i}.py")

        break # for testing

    return response

# API Endpoints

@app.get("/")
async def root():
    if not genai:
        raise HTTPException(status_code=500, detail="Gemini client not initialized.")
    return {"message": "Welcome to the Gemini FastAPI Server!"}

@app.post("/api")
async def api(file: UploadFile = File(...)):
    # await break_tasks(file)
    return await agent()
    # return await get_metadata("codes/task1/code.py")

if __name__ == "__main__":
    import uvicorn
    import json
    print("Starting server at http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)