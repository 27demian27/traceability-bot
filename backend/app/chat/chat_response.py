import requests
import json
import time 

from .func_parser import preprocess_functions
from .similarity_computer import return_similarity_matches
from .graph_builder import build_similarity_graph, draw_graph

def build_prompt(text, requirements_json, code_json, similarities):

    if not requirements_json:
        requirements_json = ["USER HASNT UPLOADED REQUIRMENTS YET"]
    if not code_json:
        code_json = ["USER HASNT UPLOADED CODE YET"]
    if not similarities:
        similarities = ["NO SIMILARITY MATCHES YET"]

    code_json = preprocess_functions(code_json, text)

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

    When receiving a request to locate functionality/test coverage, be concise and mention file names. Dont explain the logic, or tests. 

    When the user asks a question your main goal is to trace what and where.

    Clearly space out different requirements using markdown.

    ### User message [MAKE SURE TO JUST ANSWER THIS AND NOT PROVIDE ADDITIONAL INFO]:
    \"\"\"{text}\"\"\"

    ### User project related info:

    Requirements:
    \"\"\"{requirements_json}\"\"\"

    Extracted Functions:
    \"\"\"{code_json}\"\"\"

    Best similarity matches for each requirement:
    \"\"\"{similarities}\"\"\"

    ---

    ## Answer
    """

    # Debug
    with open("debug/debug_prompt.txt", "w") as debug_file:
                    debug_file.write(prompt)


    return prompt