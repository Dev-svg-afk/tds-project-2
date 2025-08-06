# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastapi",
#   "uvicorn",
#   "python-dotenv",
#   "google-generativeai",
#   "python-multipart",
# ]
# ///

import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import google.generativeai as genai

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


@app.get("/")
async def root():
    """A simple route to check if the server is running."""
    return {"message": "Welcome to the Gemini FastAPI Server!"}


@app.get("/gemini_test")
async def gemini_test():
    """A test route to check the Gemini API connection."""
    if not genai:
        raise HTTPException(status_code=500, detail="Gemini client not initialized.")
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Tell me a fun fact about the Roman Empire.")
        return {"response": response.text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting server at http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)