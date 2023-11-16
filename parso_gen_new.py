from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import parso
import time
import os
import sys
import math


# 사용할 모델과 토크나이저
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")

text = "\'\'\'Write a function to find the shared elements from the given two lists.\'\'\'\ndef"

# 후보 리스트 [description, score] 형태의 리스트이다.
possible = [[text, 0]]



def generate(candi):
    
    # description과 score의 리스트로 들어오는 입력값을 분리해준다.
    text = candi[0]
    score = candi[1]

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

        # score를 계산하는 부분
        score += (-math.log2(token_probability))
    

        
        
        # 기존 코드와 토큰 합치기
        if token == "<|endoftext|>":
            text_token = text
        else:
            text_token = text + token
        
        # parso grammar 장착
        grammar = parso.load_grammar()
        
        # parso 렉싱 ( 공식 python과 같음 )
        token_info = grammar._tokenize(text_token)

        
        # 렉싱에러가 있다면 다시 후보리스트에 넣고 다음으로 넘어감
        for info in token_info:
            if str(info.type) == "PythonTokenTypes.ERRORTOKEN":

                possible.append([text_token, score])
                print(f"<다시 후보 리스트에 넣기> \n{text_token}\n\n\n\nscore : {score}\n\n")
                possible.sort(key=lambda x: x[1])
                
                continue
                
            
        # 렉싱 에러가 없다면 parso로 파싱
            
        # parso 파싱
        module = grammar.parse(text_token)
        
        errors = grammar.iter_errors(module) 
        
    
        # No error
        if len(errors) == 0:
            # 해당 토큰을 선택
            if token == "<|endoftext|>":
                print(f"\n\n\n정답입니다.\n")
                return [text, score]
            print(f"<다시 후보 리스트에 넣기> \n{text_token}\n\n\n\nscore : {score}\n\n")
            possible.append([text_token, score])
            possible.sort(key=lambda x: x[1])


        # Error 
        else:

            # 마지막 위치에 에러
            if(errors[0].end_pos[1] == len(text_token.split('\n')[-1])) and (errors[0].start_pos[0] == len(text_token.split('\n'))):
                if token == "<|endoftext|>":
                    continue 
                possible.append([text_token, score])
                print(f"<다시 후보 리스트에 넣기> \n{text_token}\n\n\n\nscore : {score}\n\n")
                possible.sort(key=lambda x: x[1])
            # 중간에 에러    
            else:
                # 파싱 에러인 경우
                no_pos = text + token[0]
                print(f"------싹수없음-----\n\n") 
                print(f"{no_pos}를 후보 리스트에서 삭제합니다.")
                for each in possible:
                    # 원래 주어진 문자열에 오류가 있으므로 주어진 문자열과 같은 부분을 삭제함
                    if each[0].find(no_pos) >= 0 :
                        possible.remove(each)
                    else:
                        continue           
                continue





while possible:

    print(f"++++++++++{len(possible)}+++++++++")
    text = possible.pop(0)
    print(f"<<<<생성할 description>>>>> :\n{text[0]}\n<<score : {text[1]}>>")
    answer = generate(text)
    
    if answer == None:
        continue
    
    else:    
        print(answer[0] + "\n")
        print(answer[1])
        break
    
    
    
    