import tiktoken
import httpx
import os
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
        return {"error": "timeout"}  
    except httpx.HTTPStatusError as e:
        return {"error": f"Received HTTP {e.response.status_code} from the API."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


async def call_gemini(prompt: str, model: str = "gemini-2.5-flash") -> str:
    try:
        response = genai.GenerativeModel(model).generate_content(prompt)

        # Make sure there's at least one candidate with content
        if not response.candidates:
            return {"error": "No candidates returned from Gemini."}

        content = response.candidates[0].content
        if not content.parts:
            return {"error": "Gemini response has no parts."}

        return content.parts[0].text
    
    except Exception as e:
        return {"error": str(e)}

async def count_tokens(prompt: str, model: str = "gpt-4o-mini"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(prompt))
    return num_tokens

async def call_llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    if model.startswith("gemini"):
        response = await call_gemini(prompt, model)
        if isinstance(response, dict) and "error" in response:
            response = await call_gpt(prompt)

    else:
        response = await call_gpt(prompt)
        if isinstance(response, dict) and "error" in response:
            response = await call_gemini(prompt)

    return response