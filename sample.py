import os
import torch


## update path to real one
path = "codegpt-small_codecompletion-py150"


##### Load Tokenizer, Model #####
from transformers import GPT2Tokenizer, GPT2LMHeadModel

tokenizer = GPT2Tokenizer.from_pretrained(path)
model = GPT2LMHeadModel.from_pretrained(path)
# model.eval()

# sep_token_ids = { tokenizer.sep_token_id: 1 }


##### Tokenize #####
from preprocess import preprocess
from restore import restore

def encode(text, max_length):
    code = preprocess(text)
    endofline = code.splitlines(keepends=True)[0][-1]
    if not code.endswith(endofline):
        code += endofline
    return tokenizer(code, padding=False, truncation=True, max_length=max_length,
                     add_special_tokens=True, return_tensors="pt")

def decode(token_ids):
    return restore(tokenizer.decode(token_ids))


code = """
'''Write a function to find the n largest integers from a given list of numbers, returned in descending order.'''
def 
""".strip()
print("target code:")
print(code)

tokenized_inputs = encode(code, None)
print("input tokens:")
print(tokenizer.decode(tokenized_inputs["input_ids"][0]))

logits = model(tokenized_inputs["input_ids"]).logits
next_token_logits = logits[:, -1, :]
next_token_probabilities = torch.softmax(next_token_logits, dim=-1)

# 상위 K개의 확률과 해당 토큰 얻기 (예: 상위 5개)
top_k_probabilities, top_k_indices = torch.topk(next_token_probabilities, 5, dim=-1)

# 상위 K개의 토큰 및 확률 출력
for i in range(5):
    token_id = top_k_indices[0, i].item()
    token_probability = top_k_probabilities[0, i].item()
    token = tokenizer.decode(token_id)
    print(f"Next Token: [{token}], Possibility: {token_probability:.4f}\n")

##### Inference #####
prediction = model.generate(**tokenized_inputs, max_new_tokens=10)
print("output tokens:")
print(tokenizer.decode(prediction[0]))
print("restored output:")
print(decode(prediction[0]))
