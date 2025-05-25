import torch.nn.functional as F

query = "sort a list"
code_snippet = "def sort_list(lst): return sorted(lst)"

query_emb = get_embedding(query)
code_emb = get_embedding(code_snippet)

similarity = F.cosine_similarity(query_emb, code_emb)
print(f"Similarity: {similarity.item()}")
