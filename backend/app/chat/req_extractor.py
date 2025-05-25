import requests
import json
import re

def extract_requirement_candidates(text: str, k: int = 2) -> list:
    lines = text.splitlines()
    candidates = []
    requirement_keywords = {"shall", "must", "should", "can", "may", "will"}

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        if len(stripped_line) < 20:
            continue  
        if any(kword in stripped_line.lower() for kword in requirement_keywords):
            if not re.search(r'(author|date|log|version|page|table of contents)', stripped_line.lower()):
                # Get k lines before and after
                start = max(0, i - k)
                end = min(len(lines), i + k + 1)
                context_block = lines[start:end]
                candidates.append("\n".join(context_block).strip())

    return candidates

def extract_requirements(text):
    prompt = f"""
    You are a strict JSON API.

    You will return only valid JSON arrays. Do not return any explanations, markdown, or formatting.

    ### Instructions:
    - Extract only **concrete, testable** software requirements
    - Classify each as "Functional" or "Non-functional"
    - Assign priority as "High", "Medium", or "Low"
    - MAKE SURE TO ONLY EXTRACT ID, DESCRIPTION, TYPE, PRIORITY
    - OUTPUT MUST BE IN JSON STRUCTURE WITH SAME KEYS EXACTLY AS EXAMPLE BELOW:
    [
    {{
        "id": "REQ-001",
        "description": "...",
        "type": "Functional",
        "priority": "High"
    }},
    ...
    ]

    ### Input:
    \"\"\"{text}\"\"\"

    ### JSON Output:
    """


    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )

    # Extract response string
    raw_output = response.json().get("response", "")
    
    print(raw_output)

    # Check for valid JSON
    match = re.search(r"\[\s*{[\s\S]*?}\s*]", raw_output)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print("⚠️ JSON decoding failed:", e)
    
    return [{"id": "REQ-ERROR", "description": "Failed to parse", "type": "N/A", "priority": "N/A"}]
