import os
from typing import TypedDict, Union, Literal, Optional
import httpx
import asyncio
import google.generativeai as genai

class SuccessResponse(TypedDict):
    content: str

class ErrorResponse(TypedDict):
    error: Literal[True]
    message: str
    code: Optional[int]
    type: str

CommonReturn = Union[SuccessResponse, ErrorResponse]

async def call_gpt(prompt: str, image_url:str = None) -> CommonReturn:
    url = "https://aipipe.org/openai/v1/chat/completions"
    token = os.getenv('AIPIPE_TOKEN')

    if not token:
        return {
            "error": True,
            "message": "Missing API token",
            "code": None,
            "type": "AuthError"
        }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    if image_url:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ]
    else:
        messages = [{"role": "user", "content": prompt}]

    json_data = {
        "model": "gpt-4o-mini",
        "messages": messages,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=json_data)
            response.raise_for_status()
            data = response.json()

            choices = data.get("choices")
            if not choices or not isinstance(choices, list):
                return {
                    "error": True,
                    "message": "Malformed response: missing choices",
                    "code": response.status_code,
                    "type": "MalformedResponse"
                }

            message = choices[0].get("message")
            if not message or "content" not in message:
                return {
                    "error": True,
                    "message": "Malformed response: missing message content",
                    "code": response.status_code,
                    "type": "MalformedResponse"
                }

            return {"content": message["content"]}

    except httpx.TimeoutException:
        return {
            "error": True,
            "message": "Request timed out",
            "code": None,
            "type": "TimeoutException"
        }
    except httpx.HTTPStatusError as e:
        return {
            "error": True,
            "message": f"Received HTTP {e.response.status_code} from API",
            "code": e.response.status_code,
            "type": "HTTPError"
        }
    except Exception as e:
        return {
            "error": True,
            "message": f"Unexpected error: {str(e)}",
            "code": None,
            "type": "UnexpectedError"
        }

async def call_gemini(prompt: str, model: str = "gemini-2.5-flash") -> CommonReturn:
    try:
        loop = asyncio.get_running_loop()

        def sync_gemini_call():
            response = genai.GenerativeModel(model).generate_content(prompt)
            return response

        response = await loop.run_in_executor(None, sync_gemini_call)

        if not response.candidates:
            return {
                "error": True,
                "message": "No candidates returned from Gemini.",
                "code": None,
                "type": "EmptyResponse"
            }

        content = response.candidates[0].content
        if not content.parts:
            return {
                "error": True,
                "message": "Gemini response has no parts.",
                "code": None,
                "type": "MalformedResponse"
            }

        return {"content": content.parts[0].text}

    except Exception as e:
        return {
            "error": True,
            "message": str(e),
            "code": None,
            "type": "UnexpectedError"
        }

async def call_llm(prompt: str, llm:str, model:str = "gemini-2.5-flash") -> Union[str, CommonReturn]:

    if llm == "gemini":

        result = await call_gemini(prompt, model=model)

        if "error" in result:
            print("gemini crashed")

            result = await call_gpt(prompt)

        if "error" not in result:
            return result["content"]
        
    else:

        result = await call_gpt(prompt)        

        if "error" in result:
            print("gpt crashed")

            if result["type"] == "HTTPError":
                result = await call_gpt(prompt)
            if "error" in result:
                await call_gemini(prompt, model=model)

        if "error" not in result:
            return result["content"]

    return "all llms crashed"
