from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import parso
import time
import os
import sys

# 몇번째 테싀크 케이스 인지 받아옴 
index = sys.argv[1]

# log를 기록할 파일 설정
# 디렉터리 경로
directory_path = "/home/jskim/syncor/log/parso_gen"
# 파일명 생성
file_name = f"log_{index}_case.txt"
# 파일 경로
file_path = os.path.join(directory_path, file_name)

# 로그 파일 생성
with open(file_path, "w") as file:
    file.write(f"<<<<<<<<<<<< {index} problem >>>>>>>>>>>\n\n\n\n\n")

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
        with open(file_path, "a") as file:
                    file.write(f"Next Token : {token}, Posbility: {token_probability:.4f}\n") 
    
    # 상위 5개 토큰에서 EOS 토큰이 나오면 종료
    if done:
        with open(file_path, "a") as file:
                    file.write(f"EOS token!!!\n") 
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
            # 해당 토큰을 선택
            with open(file_path, "a") as file:
                    file.write(f"Choose : {token}, Posbility: {token_probability:.4f}\n") 
            return text_token


        # Error 
        else:

            # 마지막 위치에 에러
            if(errors[0].end_pos[1] == len(text_token.split('\n')[-1])) and (errors[0].start_pos[0] == len(text_token.split('\n'))):
                # 해당 토큰을 선택
                with open(file_path, "a") as file:
                    file.write(f"Choose : {token}, Posbility: {token_probability:.4f}\n") 
                return text_token
            
            # 중간에 에러    
            else:
                
                with open(file_path, "a") as file:
                    file.write(f"syntax error : {token}\n") 
                    
                # 다음 토큰으로 넘어감               
                continue
                 
    # 상위 5개 모두에서 오류가 발생한 경우 
    with open(file_path, "a") as file:
        file.write("all top 5 token has syntax error. END\n")        
    return None


# 중간 에러가 발생할 때까지 계속 토큰을 반복해서 생성

def continue_generate(text):


    generating_code = generate(text)
    pre_gen = text
    with open(file_path, "a") as file:
                file.write(generating_code+"\n")

    #시작 시간 측정
    start_time = time.time()
    
    # 걸린 시간이 2분 미만일 때만 반복
    while True:
        
        with open(file_path, "a") as file:
                file.write("---------------------------\n")
        
        # generate 결과가 EOS이거나 상위 5개 모두에서 syntax error인 경우 멈춘다.
        if generating_code == None:
            current_time = time.time()
            with open(file_path, "a") as file:
                file.write("<<<<<<<<<<<<< FINISH >>>>>>>>>>>>\n\n\n\n")
                file.write(f"processing time : {current_time - start_time}\n\n\n\n")
                
                grammar = parso.load_grammar()

                module = grammar.parse(pre_gen)

                errors = grammar.iter_errors(module)
                
                if len(errors) == 0:
                    syn_err = False
                    file.write(f"----------No Syntax Error--------\n\n")  
                    file.write(pre_gen+"\n")
                    print(f"Success")
                    
                    # [index(text case number), process_time, syn_err, pre_gen] -> csv 
                    
                else:
                    syn_err = True
                    file.write(f"----------Syntax Error-----------\n\n")
                    file.write(pre_gen+"\n\n\n\n")
                    file.write(f"Error Start : {errors[0].start_pos}, Error End {errors[0].end_pos}")
                    print(f"Fail")
                    
                    # [index(text case number), process_time, syn_err, pre_gen] -> csv
                
           
            return pre_gen
            
        # 마지막 위치 error인 경우나 error가 없을 때
        else:
            
            with open(file_path, "a") as file:
                file.write(generating_code+"\n")
                file.write("---------------------------\n")
            # 그 다음 토큰을 생성  
            pre_gen = generating_code      
            generating_code = generate(generating_code)


# description을 받아옴                
text = sys.argv[2]

# 후보 리스트 
possible = []

# 테스트 실행
continue_generate(text)
                
                
