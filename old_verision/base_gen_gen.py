from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time
import os
import sys
import parso
import time

index = sys.argv[1]

# log를 기록할 파일 설정
# 디렉터리 경로
directory_path = "/home/jskim/syncor/log/base_gen_gen"
# 파일명 생성
file_name = f"{index}.txt"
# 파일 경로
file_path = os.path.join(directory_path, file_name)

# 로그 파일 생성
with open(file_path, "w") as file:
    file.write(f"<<<<<<<<<<<< {index} problem >>>>>>>>>>>\n\n")

# 사용할 모델과 토크나이저
tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")

# description을 받아옴        
text = sys.argv[2]

# 시간 측정
start_time = time.time()

# 한번에 (토큰단위로 말고) 코드 생성 
input_ids = tokenizer(text, return_tensors="pt").input_ids
generated_ids = model.generate(input_ids, max_length=128)
code = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

# 프로세싱 타임 측정
process_time = time.time() - start_time

# 신택스 에러 점검

grammar = parso.load_grammar()

module = grammar.parse(code)

errors = grammar.iter_errors(module)


    

with open(file_path, "a") as file:
                    file.write(f"Code:\n{code}\n")
                    file.write(f"Process Time : {process_time}\n")
                    if len(errors) == 0:  
                        file.write(f"Syntax : No Syntax Error")
                    else:
                        file.write(f"Syntax : Syntax Error")
                    
                      