from transformers import AutoTokenizer, AutoModel
import torch

# Load tokenizer and model
model_dir = "./output_proto/siamese2_random_04-24 23-53-59_/final_model"
tokenizer = AutoTokenizer.from_pretrained(model_dir)
model = AutoModel.from_pretrained(model_dir)
model.eval()
