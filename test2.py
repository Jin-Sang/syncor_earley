from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")

text = '''# Write a python function to identify non-prime numbers.
import math
def is_not_prime(n):
    if n == 1:
        '''
input_ids = tokenizer(text, return_tensors="pt").input_ids

# 다음 토큰의 logit 확률 계산
with torch.no_grad():
    logits = model(input_ids).logits

# logits에서 다음 토큰에 대한 확률 분포 얻기
next_token_logits = logits[:, -1, :]

# 확률 분포를 확률로 변환
next_token_probabilities = torch.softmax(next_token_logits, dim=-1)

# 상위 K개의 확률과 해당 토큰 얻기 (예: 상위 5개)
top_k = 5
top_k_probabilities, top_k_indices = torch.topk(next_token_probabilities, top_k, dim=-1)

# 상위 K개의 토큰 및 확률 출력
for i in range(top_k):
    token_id = top_k_indices[0, i].item()
    token_probability = top_k_probabilities[0, i].item()
    token = tokenizer.decode(token_id)
    print(f"다음 토큰: {token}, 확률: {token_probability:.4f}")
