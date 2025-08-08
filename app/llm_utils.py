import tiktoken
import httpx
import os
from fastapi import HTTPException
import google.generativeai as genai


async def call_gpt(prompt: str) -> str:
    url = "https://aipipe.org/openai/v1/chat/completions"
    token = os.getenv('AIPIPE_TOKEN')

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    json_data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=json_data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
    except httpx.ReadTimeout:
        return "Error: The request to the model timed out."
    except httpx.HTTPStatusError as e:
        return f"Error: Received HTTP {e.response.status_code} from the API."
    except Exception as e:
        return f"Unexpected error: {str(e)}"


import google.generativeai as genai
from fastapi import HTTPException

async def call_gemini(prompt: str, model: str = "gemini-2.5-flash") -> str:
    try:
        response = genai.GenerativeModel(model).generate_content(prompt)

        # Make sure there's at least one candidate with content
        if not response.candidates:
            raise ValueError("Gemini returned no candidates.")

        content = response.candidates[0].content
        if not content.parts:
            raise ValueError("Gemini response has no parts.")

        return content.parts[0].text
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

async def count_tokens(prompt: str, model: str = "gpt-4o-mini"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(prompt))
    return num_tokens