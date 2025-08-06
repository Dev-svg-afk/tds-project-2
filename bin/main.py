# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "beautifulsoup4",
#   "playwright",
#    "asyncio",
# ]
# ///

# from tools import scrape_website, get_relevant_data
from playwright.async_api import async_playwright
import asyncio

import httpx
import os
from typing import Dict, Any
from bs4 import BeautifulSoup

def get_relevant_data(file_name: str, js_selector: str = None) -> Dict[str, Any]:
    with open(file_name, encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    if js_selector:
        elements = soup.select(js_selector)
        data = "\n".join(el.get_text(strip=True) for el in elements)
    else:
        data = soup.get_text(strip=True)

    # let's write this soup.get_text(strip=True) into a new file
    with open("relevant_data.txt", "w", encoding="utf-8") as f:
        f.write(data)
    return {"executed": get_relevant_data}

async def scrape_website(url: str, output_file: str = "scraped_content.html"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            content = await page.content()
            # write content to a file
            with open(output_file, "w", encoding="utf-8") as file:
                await file.write(content)
        except Exception as e:
            print(f"Failed to load page: {e}")
            await browser.close()
            return
        await browser.close()
    return {"executed": scrape_website} 

async def execute_code(code: str) -> Dict[str, Any]:
    # write code to a python file and execute it with subprocess module 
    with open("temp_script.py", "w") as f:
        f.write(code)
    import subprocess
    result = subprocess.run(["python", "temp_script.py"], capture_output=True, text=True)
    return result.stdout

async def answer_questions(query: str):
    model = 'gemini-2.5-flash-lite'
    response = genai.GenerativeModel(model).generate_content(query)

    return {
        "response": response
    }

tools = [
    {
        "type": "function",
        "function": {
            "name": "scrape_website",
            "description": "scrapes a website and saves the content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the website to scrape"
                    },
                    "output_file": {
                        "type": "string",
                        "description": "The file to save the scraped content"
                    }
                },
                "required": ["url", "output_file"], # output_file is optional
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_relevant_data",
            "description": "Extracts relevant data from a webpage",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_name": {
                        "type": "string",
                        "description": "Name of the file containing the HTML content"
                    },
                    "js_selector": {
                        "type": "string",
                        "description": "CSS selector to identify the target data"
                    }
                },
                "required": ["file_name", "js_selector"], # js_selector is optional
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "answer_questions",
            "description": "Executes a Python script passed as a string and returns the output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query needs to be answered"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            },
            "strict": True
        }
    }

]
    

def query_gpt(prompt: str, tools: list[Dict[str, Any]]) -> Dict[str, Any]:
    url = "https://aipipe.org/openai/v1/chat/completions"
    token = os.getenv('AIPIPE_TOKEN')
    # url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    # token = os.getenv('AIPROXY_TOKEN')
    response = httpx.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "tools": tools,
            "tool_choice": "auto",
        },
    )
    # Write response to a file for debugging
    with open("gpt_response.json", "w", encoding="utf-8") as f:
        f.write(response.text)
    return response.json()["choices"][0]["message"]


async def main(prompt: str):
    response = query_gpt(prompt, tools)

    if "tool_calls" in response:
        for tool_call in response["tool_calls"]:
            if tool_call["type"] == "function":
                function_name = tool_call["function"]["name"]
                parameters = tool_call["function"]["arguments"]
                # return {
                #     "parameters": parameters
                # }
                # {"parameters":"{\"url\":\"https://en.wikipedia.org/wiki/List_of_highest-grossing_films\",\"output_file\":\"highest_grossing_films.html\"}"}
                # above line is the sample parameter I'm getting, modify the below lines to use these parameters correctly
                import json
                if isinstance(parameters, str):
                    parameters = json.loads(parameters)
                
                if function_name == "scrape_website":
                    return await scrape_website(**parameters)
                elif function_name == "get_relevant_data":
                    return get_relevant_data(**parameters)
                elif function_name == "answer_questions":
                    return await answer_questions(**parameters)
    
    # print("Response:", response.get("content", "No content returned."))

if __name__ == "__main__":
    asyncio.run(main())