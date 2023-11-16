from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time
import os
import sys
import parso

index = sys.argv[1]

# log를 기록할 파일 설정
# 디렉터리 경로
directory_path = "/home/jskim/syncor/log/base_gen_new"
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
    
    input_ids = tokenizer(text, return_tensors="pt").input_ids
    
    # EOS 감지 변수
    done = False
    
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
        # 최상위 토큰이 def이면 멈추기 위해 done을 True로
        if i == 0 and token == "def":
            done = True
        with open(file_path, "a") as file:
                    file.write(f"Next Token : {token}, Posbility: {token_probability:.4f}\n") 
    
    # 상위 5개 토큰에서 EOS 토큰이 나오면 종료
    if done:
        with open(file_path, "a") as file:
                    file.write(f"def token!!!\n") 
        return None
    # 아닌 경우 가장 높은 확률의 토큰을 선택한다.
    else: 
        token_id = top_k_indices[0, 0].item()
        token_probability = top_k_probabilities[0, 0].item()
        token = tokenizer.decode(token_id)
        with open(file_path, "a") as file:
            file.write(f"Choose : {token},  Posbility: {token_probability:.4f}\n")
    
    return text + token


# EOS를 만나기 전까지 계속 생성

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
        
        # generate 결과가 EOS
        if generating_code == None:
            current_time = time.time()
            process_time = current_time - start_time
            with open(file_path, "a") as file:
                file.write("<<<<<<<<<<<<< FINISH >>>>>>>>>>>>\n\n\n\n")
                file.write(f"processing time : {process_time}\n\n\n\n")
                
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


# 테스트 실행
continue_generate(text)


