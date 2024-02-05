from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import parso
import time
import os
import sys
import math
from parso.python.token import PythonTokenTypes

# 사용할 모델과 토크나이저
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")


# 몇번째 테스트 케이스 인지 받아옴 
index = sys.argv[1]

# description을 받아옴                
text = sys.argv[2]

# log를 기록할 파일 설정
# 디렉터리 경로
directory_path = "/home/jskim/syncor/log/parso_gen_0_timeout"

# 파일명 생성
file_name = f"{index}.txt"
# 파일 경로
file_path = os.path.join(directory_path, file_name)

# 로그 파일 생성
with open(file_path, "w") as file:
    file.write(f"<<<<<<<<<<<< {index} problem >>>>>>>>>>>\n\n")


# parso grammar 장착
    grammar = parso.load_grammar()

# end token 설정    
EOS_token = "<|endoftext|>"

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
        with open(file_path, "a") as file:
                    file.write(f"\n->Next Token: {token}, Possibility: {token_probability:.4f}\n")
                 

        # score를 계산하는 부분
        # 유포니 :
        score += (-math.log2(token_probability))
    

        
        
        # 기존 코드와 토큰 합치기 (EOS면 합치지 않음)
        if token == EOS_token:
            text_token = text
        else:
            text_token = text + token
        
        
        # parso 렉싱 ( 공식 python과 같음 )
        token_info = grammar._tokenize(text_token)

        # 렉싱 오류 여부 체크하는 변수
        lex_err = False
        
        # 렉싱에러가 있다면 다시 후보리스트에 넣고 다음으로 넘어감
        for info in token_info:
            if info.type == PythonTokenTypes.ERRORTOKEN:

                possible.append([text_token, score])
                with open(file_path, "a") as file:
                    file.write(f"\n< Lexing Error : Add to List > \n{text_token}\n\nscore : {score}\n")
                    file.write(f"--------------------------------------------------------------------\n")
                    
                possible.sort(key=lambda x: x[1])
                
                lex_err = True
                break
        
        # 렉싱 에러인 경우는 다음 토큰들 중 다른 것을 탐색한다.   
        if lex_err:
            continue
                
            
        # 렉싱 에러가 없다면 parso로 파싱
            
        # parso 파싱
        module = grammar.parse(text_token)
        
        errors = grammar.iter_errors(module) 
        
    
        # No error
        if len(errors) == 0:
            # 해당 토큰이 EOS였다면 정답으로 반환 
            if token == EOS_token:
                with open(file_path, "a") as file:
                    file.write(f"\n\n\nResult:\n\n")
                
                
                return [text, score]
            
            # 후보리스트에 추가 후 리스트 정렬
            with open(file_path, "a") as file:
                    file.write(f"\n< No Error : Add to List > \n{text_token}\n\nscore : {score}\n")
                    file.write(f"--------------------------------------------------------------------\n")
            possible.append([text_token, score])
            possible.sort(key=lambda x: x[1])


        # Error 
        else:

            # 마지막 위치에 에러
            if(errors[0].end_pos[1] == len(text_token.split('\n')[-1])) and (errors[0].start_pos[0] == len(text_token.split('\n'))):
                # 마지막 토큰이 EOS면 넘어간다.
                if token == EOS_token:
                    continue 
                
                # 아니라면 후보 리스트에 추가해준다.
                possible.append([text_token, score])
                with open(file_path, "a") as file:
                    file.write(f"\n< Parsing Error : Add to List > \n{text_token}\n\nscore : {score}\n")
                    file.write(f"--------------------------------------------------------------------\n")
                possible.sort(key=lambda x: x[1])
            # 중간에 에러    
            else:
                # 파싱 에러인 경우
                no_pos = text + token[0]
                with open(file_path, "a") as file:
                    file.write(f"------Impossible case-----\n")
                    # file.write(f"{no_pos} Delete in List. delete_token!\n") 보류
                    file.write(f"--------------------------------------------------------------------\n")
                # 삭제 하는거 일단 보류
                '''
                for each in possible:
                    # 원래 주어진 문자열에 오류가 있으므로 주어진 문자열과 같은 부분을 삭제함
                    if each[0].find(no_pos) >= 0 :
                        possible.remove(each)
                    else:
                        continue           
                '''
                continue


    



# 후보 리스트 [description, score] 형태의 리스트이다.
possible = [[text, 0]]


start_time = time.time()

# 우리가 내는 정답의 Syntax Error 여부
syncor = False

# 후보 리스트가 비어있을 때까지 반복
while possible:

    with open(file_path, "a") as file:
        file.write(f"\n< Get from List >\n")
        file.write(f"List Length : {len(possible)}\n")
    
    text = possible.pop(0)
    
    with open(file_path, "a") as file:
        file.write(f"given description :\n\n{text[0]}\n\n[ given score : {text[1]} ]\n")
    
    answer = generate(text)
    
    if answer == None:
        continue
    
    else:
        
        module = grammar.parse(answer[0])
        
        errors = grammar.iter_errors(module)
        
        if len(errors) == 0:
            syncor = True
        
        with open(file_path, "a") as file:
            
            file.write("\n\n" + str(answer[0]) + "\n")
            file.write("\n\n" + str(answer[1]) + "\n")
        

        break
    
    
# 프로세싱 타임 기록    
processing_time = time.time()-start_time    

with open(file_path, "a") as file:
            file.write(f"\n\n\nprocessing time : {processing_time} \n")

# 신택스 오류 여부 표시
if syncor:
    with open(file_path, "a") as file:
            file.write(f"Syntax : Correct ")
else:
    with open(file_path, "a") as file:
            file.write(f"Syntax : Error ")
    