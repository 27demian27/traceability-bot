import requests

def chat_response(text, requirements_json, code_json):
    if len(requirements_json) == 0:
        requirements_json = ["USER HASNT UPLOADED REQUIRMENTS YET"]
    if len(code_json) == 0:
        code_json = ["USER HASNT UPLOADED CODE YET"]

    prompt = f"""
    You are a Chatbot.

    Respond in natural language.
    The user may ask requirements to code questions.
    The user may ask requirements to testing questions.
    The user may ask requirements to architectual design questions.

    Keep your answers short and concise unless asked otherwise.

    The user has the ability to upload requirements and architectual design documents, 
    as well as code files.

    If you havent received this yet from the user please ask them to do so.

    ### User message:
    \"\"\"{text}\"\"\"

    ### User uploads:

    Requirements:
    \"\"\"{requirements_json}\"\"\"

    Parsed Code:
    \"\"\"{code_json}\"\"\"

    """


    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    
    raw_output = response.json().get("response", "")
    
    return raw_output