import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# 모델과 토크나이저 로드
model_name = "microsoft/CodeGPT-small-py"  # 또는 다른 GPT-2 모델 이름
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# 예측할 문장
input_text = '''<s>import math<EOL>def is_not_prime(n):<EOL>    '''

# 토크나이징 및 모델 입력 준비
input_ids = tokenizer.encode(input_text, return_tensors="pt")

# 다음 토큰 예측
with torch.no_grad():
    logits = model(input_ids).logits

# 다음 토큰의 확률 분포 얻기
next_token_logits = logits[:, -1, :]

# 확률 분포를 확률로 변환
next_token_probabilities = torch.softmax(next_token_logits, dim=-1)

# 다음 토큰의 확률을 확인
top_k = 10  # 상위 K개의 확률을 확인하려면 K 값을 조정하세요.
top_k_tokens = torch.topk(next_token_probabilities, top_k, dim=-1)

for i in range(top_k):
    token_id = top_k_tokens.indices[0, i].item()
    token_probability = top_k_tokens.values[0, i].item()
    token = tokenizer.decode(token_id)
    print(f"다음 토큰: {token}, 확률: {token_probability:.4f}")
