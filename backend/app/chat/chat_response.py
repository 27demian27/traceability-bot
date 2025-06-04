import requests
import json
import time 

from .func_parser import preprocess_functions
from .similarity_computer import return_similarity_matches
from .graph_builder import build_similarity_graph, draw_graph

def build_prompt(text, requirements_json, code_json):

    missing_json = 0
    similarity_matches = ["NO SIMILARITY MATCHES YET"]
    top_n_matches = 3

    if len(requirements_json) == 0:
        requirements_json = ["USER HASNT UPLOADED REQUIRMENTS YET"]
        missing_json = 1
    if len(code_json) == 0:
        code_json = ["USER HASNT UPLOADED CODE YET"]
        missing_json = 1

    if not missing_json:
        similarity_matches = return_similarity_matches(requirements_json, code_json, top_n_matches, False)
        graph = build_similarity_graph(requirements_json, code_json, similarity_matches)
    #   draw_graph(graph)

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

    DO NOT RETURN ANY REASONING OR THINKING IN YOUR RESPONSE.

    ### User message [MAKE SURE TO JUST ANSWER THIS AND NOT PROVIDE ADDITIONAL INFO]:
    \"\"\"{text}\"\"\"

    ### User project related info:

    Requirements:
    \"\"\"{requirements_json}\"\"\"

    Extracted Functions:
    \"\"\"{code_json}\"\"\"

    ---

    ## Answer
    """

    # Debug
    with open("debug_prompt.txt", "w") as debug_file:
                    debug_file.write(prompt)


    return prompt