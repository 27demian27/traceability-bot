from openai import OpenAI

import os
from dotenv import load_dotenv, dotenv_values 

import requests
import json
import re
import time
import re

def extract_requirement_candidates(text: str, k: int = 2, requirement_id_only: bool = False) -> list:
    lines = text.splitlines()
    candidates = []
    requirement_keywords = {"shall", "must", "should", "can", "may", "will", "has"}
    requirement_id_pattern = re.compile(r'(US\d+-[A-Z]\d+|REQ-\d+)', re.IGNORECASE)

    for i, line in enumerate(lines):
        stripped_line = line.strip()

        if re.search(r'(author|date|log|version|page|table of contents)', stripped_line.lower()):
            continue

        has_req_id = bool(requirement_id_pattern.search(stripped_line))

        has_keyword = any(kword in stripped_line.lower() for kword in requirement_keywords)

        if has_req_id:
            if not requirement_id_only and not has_keyword:
                continue

            start = max(0, i - k)
            end = min(len(lines), i + k + 1)
            context_block = lines[start:end]

            if any(re.search(r'\d', l) for l in context_block):
                candidates.append("\n".join(context_block).strip())

    return candidates

import re

def preprocess_requirements(text: str) -> list:
    lines = text.splitlines()
    req_id_pattern = re.compile(r'^(?!US-\d+$)[A-Z]{1,3}[A-Z0-9]*(?:[-_][A-Z0-9]+)+\b')
    requirement_keywords = {"shall", "must", "should", "can", "may", "will", "has"}
    blocks = []
    current_block = []

    for line in lines:
        if req_id_pattern.match(line):
            if current_block:
                blocks.append("\n".join(current_block))
            current_block = [line]
        elif current_block and len(current_block) < 3:
            current_block.append(line)

    if current_block:
        blocks.append("\n".join(current_block))
    
    keyword_filtered_blocks = []

    for block in blocks:
        if any(keyword in block.lower() for keyword in requirement_keywords):
            keyword_filtered_blocks.append(block)
    return keyword_filtered_blocks

def extract_requirements(text):
    
    start = time.time()

    local_model = True

    load_dotenv() 

    mode = os.getenv("LLM_MODE")

    if mode == "API":
        local_model = False

    print("EXTRACTING REQUIREMENTS IN ", mode, " MODE")

    prompt = f"""
    You will extract software requirements to structured JSON.

    Return ONLY a JSON array of requirements, where each requirement contains these four fields:
    - "id" (string)
    - "description" (the description exactly as given)
    - "type" ("Functional" (F) or "Non-functional" (NF))
    - "priority" ("Must", "Should", "Could", "Will Not")

    Rules:
    - DO NOT include any explanation, comments, markdown, or extra formatting.
    - DO NOT include any fields except the four above.
    - Determine type if not specified
    - Default priority is "Must" if not specified

    Example format you will provide:
    [
    {{
        "id": "US0-S0",
        "description": "This is an example requirement [DONT INCLUDE THIS]",
        "type": "Functional",
        "priority": "Must"
    }},
    ...
    ]

    MAKE SURE TO EXTRACT ALL LISTED REQUIREMENTS. 
    EACH ID (USx-Yz) HAS A CORRESPONDING REQUIREMENT.
    DONT REPHRASE ANY DESCRIPTIONS.
    IF YOU CANT FIND "Must" or "Want" default to "Must"


    ### Input:
    \"\"\"{text}\"\"\"

    ### JSON Output:
    """



    if local_model:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }
        )

        raw_output = response.json().get("response", "")

    else:
        client = OpenAI(
            api_key=os.getenv("LLM_API_KEY")
        )

        completion = client.chat.completions.create(
            model=os.getenv("LLM_API_MODEL"),
            store=True,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        raw_output = completion.choices[0].message.content

    print("\n\nRound 1 Elapsed:", round(time.time() - start, 2), "seconds")

    # Debug
    with open("debug/debug_requirements_p1.txt", "w") as debug_file:
                    debug_file.write(prompt)
    with open("debug/debug_requirements_r1.txt", "w") as debug_file:
                    debug_file.write(raw_output)

    #raw_output = raw_output.split("</think>", 1)[-1].lstrip('\n')

    # Check for valid JSON
    match = re.search(r"\[\s*{[\s\S]*?}\s*]", raw_output)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print("⚠️ JSON decoding failed:", e)
    
    return [{"id": "REQ-ERROR", "description": "Failed to parse", "type": "N/A", "priority": "N/A"}]
