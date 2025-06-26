from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('all-MiniLM-L6-v2')

def return_similarity_matches(req_json, func_json, top_n = 3, mode = "default"):

    if not req_json or not func_json:
        return []

    include_comment = False
    include_code = False

    if mode == "comment":
        include_comment = True
    elif mode == "code":
        include_comment = True
        include_code = True


    req_texts, req_labels = extract_text_from_requirements(req_json)
    func_texts, func_labels = extract_text_from_functions(func_json, include_code=include_code, include_comment=include_comment)

    req_embeds = get_embeddings(req_texts)
    func_embeds = get_embeddings(func_texts)

    similarities = cosine_similarity(req_embeds, func_embeds)

    matches = []
    for i, req_label in enumerate(req_labels):
        ranked = sorted(
            [(func_labels[j], similarities[i][j]) for j in range(len(func_labels))],
            key=lambda x: x[1], reverse=True
        )
        matches.append((req_label, ranked[:top_n]))
    
    with open("debug/debug_matches.txt", "w") as debug_file:
                    debug_file.write(str(matches))

    return matches

def extract_text_from_requirements(req_json):
    texts = []
    labels = []
    for req in req_json:
        description = req.get("description", "")
        req_id = req.get("id", "")
        texts.append(description)
        labels.append(req_id)
    return texts, labels

def extract_text_from_functions(func_json, include_code, include_comment):
    texts = []
    labels = []
    for func in func_json:
        if not func.get('name', ''):
            continue
        text = func.get('name', '')
        if include_comment:
            text  = text + func.get('comment', '')
        if include_code:
            text  = text + func.get('code', '')
        texts.append(text)
        labels.append(func.get('name', ''))
    return texts, labels

def get_embeddings(texts):
    if isinstance(texts, str):
        texts = [texts]
    return model.encode(texts)