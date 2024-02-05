from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import parso
import time
import os
import sys
import math
from parso.python.token import PythonTokenTypes

## update path to real one
path = "codegpt-small_codecompletion-py150"


##### Load Tokenizer, Model #####
from transformers import GPT2Tokenizer, GPT2LMHeadModel

tokenizer = GPT2Tokenizer.from_pretrained(path)
model = GPT2LMHeadModel.from_pretrained(path)

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


# 몇번째 테스트 케이스 인지 받아옴 
index = sys.argv[1]

# description을 받아옴                
text = sys.argv[2]

# log를 기록할 파일 설정
# 디렉터리 경로
directory_path = "/home/jskim/syncor/log/parso_gen_ryumodel"

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
EOS_token = "</s>"
EOS_def = " def"

# 상위 몇개를 볼건지
top_k = 10


def next_tokens(text):
    
    answers = []
    
    input_ids = encode(text, None)
    
    # 다음 토큰의 logit 확률 계산
    with torch.no_grad():
        logits = model(input_ids["input_ids"]).logits

    # logits에서 다음 토큰에 대한 확률 분포 얻기
    next_token_logits = logits[:, -1, :]

    # 확률 분포를 확률로 변환
    next_token_probabilities = torch.softmax(next_token_logits, dim=-1)

    # 상위 K개의 확률과 해당 토큰 얻기 (예: 상위 5개)
    top_k_probabilities, top_k_indices = torch.topk(next_token_probabilities, top_k, dim=-1)
    
    # 상위 K개의 토큰 및 확률 출력
    for i in range(top_k):
        token_id = top_k_indices[0, i].item()
        token_probability = top_k_probabilities[0, i].item()
        token = tokenizer.decode(token_id)
        with open(file_path, "a") as file:
                    file.write(f"Next Token: [{token}, {token_id}], Possibility: {token_probability:.4f}\n")
                 

        if token == EOS_token or token == EOS_def:
            text_token = encode(text, None)
            EOS = True
        
        elif token_id == 220:
            continue 
            
        else:
            text_token = encode(text + token, None)
            EOS = False

        answers.append([decode(text_token["input_ids"][0]), EOS])
        
    answers.reverse()
    return answers

def lexing_check(text):
    
    # parso 렉싱 ( 공식 python과 같음 )
    token_info = grammar._tokenize(text)

    # 렉싱 오류 여부 체크하는 변수
    lex_err = False
    
    # 렉싱에러가 있다면
    for info in token_info:
        if info.type == PythonTokenTypes.ERRORTOKEN:
            lex_err = True
            break
            
    return lex_err

def parsing_check(text):
    
    # parso 파싱
    module = grammar.parse(text)
    errors = grammar.iter_errors(module) 
    
    # No error
    if len(errors) == 0 :
        return 0   # 0 : No Error
    
    # Error 
    else:
        # 마지막 위치에 에러
        if(errors[0].end_pos[1] == len(text.split('\n')[-1])) and (errors[0].start_pos[0] == len(text.split('\n'))):
            return 1 # 1 : Last Position Error
        # 중간에 에러    
        else:
            return 2 # 2 : No Last Position Error
    



def generate(candi):
    
    # description과 score의 리스트로 들어오는 입력값을 분리해준다.
    text = candi[0]
    EOS_check = candi[1]

    # 마지막이 EOS였다면
    if EOS_check:
        # lexing, parsing 문제 없으면 답으로 제출
        if (not lexing_check(text)) and (not parsing_check(text)):   
            return text
        else:
            return None
    # EOS가 아니었다면 
    
    # 렉싱에러가 있다면 다시 후보리스트에 넣고 다음으로 넘어감
    lexing_err = lexing_check(text)
    if lexing_err:
        possible.extend(next_tokens(text))
        with open(file_path, "a") as file:
            file.write(f"\n< Lexing Error : Predict Next Tokens -> List > \n")
            file.write(f"--------------------------------------------------------------------\n")
        return None
            
        
    # 렉싱 에러가 없다면 parso로 파싱
        
    # parso 파싱
    parsing_err = parsing_check(text)
    
    # parsing err 없을 때
    if parsing_err == 0:
        # 다음 토큰들 예측하고 다 후보 리스트에 넣음        
        possible.extend(next_tokens(text))
        
        with open(file_path, "a") as file:
            file.write(f"\n< No Error : Predict Next Tokens -> List > \n")
            file.write(f"--------------------------------------------------------------------\n")
        
        return None
    
    # parsing err가 마지막 위치에 있을 때
    elif parsing_err == 1:
        # 다음 토큰들 예측하고 다 후보 리스트에 넣음
        possible.extend(next_tokens(text))
        
        with open(file_path, "a") as file:
            
            file.write(f"\n< Last Parsing Error : Predict Next Tokens -> List > \n") 
            file.write(f"--------------------------------------------------------------------\n")
        
        return None
    
    # parsing err가 중간 위치에 있을 때 
    else:
    
        with open(file_path, "a") as file:
            file.write(f"\n< No Last parsing Error > \n")
            file.write(f"--------------------------------------------------------------------\n")
        
        # 그냥 넘어가기
        return None    
        
    

    



# 후보 리스트 [description, score] 형태의 리스트이다.
possible = [[text, False]]


start_time = time.time()

# 우리가 내는 정답의 Syntax Error 여부
syncor = False

# 후보 리스트가 비어있을 때까지 반복
while possible:

    with open(file_path, "a") as file:
        file.write(f"< Get from List >\n")
        file.write(f"List Length : {len(possible)}\n")
    
    text = possible.pop(-1)
    
    with open(file_path, "a") as file:
        file.write(f"given description :{text[0]}\n\n[ EOS_check : {text[1]} ]\n")
    
    answer = generate(text)
    
    # 아직 정답을 안 낸 경우
    if answer == None:
        continue
    
    # 정답을 낸 경우
    else:
        
        # 이미 체크를 했기 떄문에 syntax error가 없다.
        syncor = True
        
               
        with open(file_path, "a") as file:
            
            file.write("code:\n" + str(answer) + "\n")
            
        

        break
    
    
# 프로세싱 타임 기록    
processing_time = time.time()-start_time    

with open(file_path, "a") as file:
            file.write(f"processing time : {processing_time} \n")

# 신택스 오류 여부 표시
if syncor:
    with open(file_path, "a") as file:
            file.write(f"Syntax : Correct ")
else:
    with open(file_path, "a") as file:
            file.write(f"Syntax : Error ")
    