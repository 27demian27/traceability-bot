import requests
import json
import time 

from .func_parser import preprocess_functions
from .similarity_computer import return_similarity_matches
from .graph_builder import build_similarity_graph, draw_graph

def build_prompt(text, requirements_json, code_functions, testing_doc, similarities):

    if not requirements_json:
        requirements_json = "USER HASN'T UPLOADED REQUIREMENTS YET"
    if not similarities:
        similarities = "NO SIMILARITY MATCHES YET"

    code_json = []
    code_json.append(preprocess_functions(code_functions, text))

    if not code_functions:
        code_json = "USER HASN'T UPLOADED CODE YET"

    formatted_similarities = format_similarities(similarities)

    prompt = f"""
    Keep your answers short and concise unless asked otherwise.

    The user has the ability to upload requirements and testing documents, 
    as well as source code.

    Do your utmost best to answer the users question with the info at your disposal.
    
    When receiving a request to locate functionality/test coverage, be concise and mention file names. Dont explain the logic, or tests unless asked. 

    Clearly space out different requirements using markdown format.

    Always back your answers by providing code files and function names.

    Make sure to ONLY answer the lastest user message and not provide additional info.
    ### User messages:
    \"\"\"{text}\"\"\"

    ### User project related info:

    Requirements:
    \"\"\"{requirements_json}\"\"\"
    """
    if testing_doc:
        prompt += f"""
        \n
        Testing document:
        \"\"\"{testing_doc}\"\"\"
        """

    prompt += f"""\n
    Extracted Functions:
    \"\"\"{code_json}\"\"\"

    Best similarity matches for each requirement:
    \"\"\"{formatted_similarities}\"\"\"

    ---

    ## Answer
    """

    # Debug
    with open("debug/debug_prompt.txt", "w") as debug_file:
                    debug_file.write(prompt)


    return prompt

def format_similarities(similarities):
    if isinstance(similarities, str):
        return similarities

    formatted = []
    for req_label, matches in similarities:
        match_str = ", ".join([f"({label}, {score:.2f})" for label, score in matches])
        formatted.append(f"{req_label}: {match_str}")
    return "\n".join(formatted)