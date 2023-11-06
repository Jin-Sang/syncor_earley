from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import parso
import json
import pandas as pd
import time

# mbpp 벤치마크를 DataFrame으로 가져오기

def make_data_set(file):
    
    json_data = pd.read_json(file)
    
    data_set = []
    
    for index, row in json_data.iterrows():
        
        text = f"\'\'\'%s\'\'\'\ndef " % row["prompt"]
        
        data_set.append(text)
        
    return data_set

# 사용할 모델과 토크나이저
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")


# 다음 토큰의 상위 5개 확률표와 다음 토큰을 생성하고 결정
def generate(text):
    
    # EOS 토큰일때 멈추기 위한 변수
    done = False
    
        
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

    for i in range(top_k):
        token_id = top_k_indices[0, i].item()
        token_probability = top_k_probabilities[0, i].item()
        token = tokenizer.decode(token_id)
        # 상위 5개중 하나라도 EOS이면 멈추기 위해 done을 True로
        if token == "<|endoftext|>":
            done = True
        print(f"다음 토큰: {token}, 확률: {token_probability:.4f}")
    
    # 상위 5개 토큰에서 EOS 토큰이 나오면 종료
    if done:
        print("EOS 토큰을 생성했습니다.")
        return None
    
    
    # 상위 K개의 토큰 및 확률 출력
    for i in range(top_k):
        token_id = top_k_indices[0, i].item()
        token_probability = top_k_probabilities[0, i].item()
        token = tokenizer.decode(token_id)
        #print(f"다음 토큰: {token}, 확률: {token_probability:.4f}")

        # 기존 코드와 토큰 합치기
        text_token = text + token
        
        # parso로 파싱
        grammar = parso.load_grammar()

        module = grammar.parse(text_token)
        
        errors = grammar.iter_errors(module) 
        
        # 코드의 끝부분과 오류의 시작과 끝 위치 알려주는 부분
        '''
        code_end_position = (module.end_pos[0], module.end_pos[1])        
        print("Code End Position:", code_end_position)
        
        for error in errors:
            error_start_position = (error.start_pos[0], error.start_pos[1])
            error_end_position = (error.end_pos[0], error.end_pos[1])
            print("Error Start Position:", error_start_position)
            print("Error End Position:", error_end_position)
        ''' 
           
        # No error
        if len(errors) == 0:
            #print("choose : %s" % token)
            print(f"선택한 토큰: {token}, 확률: {token_probability:.4f}")
            return text_token


        # Error 
        else:

            # 마지막 위치에 에러
            if(errors[0].end_pos[1] == len(text_token.split('\n')[-1])) and (errors[0].start_pos[0] == len(text_token.split('\n'))):
                #print("choose : %s" % token)
                print(f"선택한 토큰: {token}, 확률: {token_probability:.4f}")
                return text_token
            
            # 중간에 에러    
            else:
                # 다음 토큰으로 넘어감
                print(f"syntax error 발생 : {token}")
                continue
                 
    # 상위 5개 모두에서 오류가 발생한 경우 
    print("상위 5개 모두 syntax error가 발생하여 종료합니다.")           
    return None


# 중간 에러가 발생할 때까지 계속 토큰을 반복해서 생성

def continue_generate(text):

    generating_code = generate(text)
    print(generating_code)

    #시작 시간 측정
    start_time = time.time()
    current_time = time.time()
    
    # 걸린 시간이 2분 미만일 때만 반복
    while current_time - start_time < 120:
        print("---------------------------")
        
        # generate 결과가 EOS이거나 상위 5개 모두에서 syntax error인 경우 멈춘다.
        if generating_code == None:
            return None
        # 마지막 위치 error인 경우나 error가 없을 때
        else:
            generating_code = generate(generating_code)
            print(generating_code)
            print("---------------------------")
            # 한 토큰을 만든 후 시간 측정
            current_time = time.time()
    
    # 시간 초과       
    print("시간을 초과해서 멈추었습니다.")


# 중앙 관리            
# sanitized-mbpp데이터를 DataFrame으로 읽어오고 
file = "/home/jskim/syncor/sanitized-mbpp.json"

data_set = make_data_set(file)

# 모든 데이터에 대해 실행 
for index, data in enumerate(data_set):
    
    print(f'인덱스 : {index} problem')
    
    continue_generate(data)
    