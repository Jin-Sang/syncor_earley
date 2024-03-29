import parso
import io
import token
import tokenize
import copy
from io import BytesIO

# Grammar 사전
# 파이썬 파싱 grammar를 dict 자료형으로 만들기
with open('python_grammar.txt', 'r') as file:
    lines = file.read()
    divided_tokens = lines.split("★")
    
grammar = {}
tokens = []
divided_tokens.pop()

# 토큰을 사전형에 맞게 분리함 
# value값은 리스트형으로 토큰단위로 분리함
for devided_token in divided_tokens:

    a, b = devided_token.split(":", 1)
    key = a.strip()
    values = b.strip().split("\n")
    dic_value = []
    
    for value in values:
        each = value.strip()[2:] # .replace(" ","")
        cleaned_chars = [char for char in each if char != '\'' and char != '\"']
        cleaned_string = ''.join(cleaned_chars)
        cleaned_list = cleaned_string.split()
        dic_value.append(cleaned_list)
    grammar[key] = dic_value

# 터미널     
terminal = []

with open('OP.txt', 'r') as file:
    # 파일의 모든 줄을 읽어들입니다.
    lines = file.readlines()
    
    for line in lines:
        terminal.append("<"+line.split()[0].strip()+">")
    

# 키워드
# python grammar에서 ''로 묶인 키워드를 찾는 함수
def find_enclosed_texts(file_path, sep):
    enclosed_texts = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            start_index = 0
            while True:
                start_index = line.find(sep, start_index)
                if start_index == -1:
                    break
                end_index = line.find(sep, start_index + 1)
                if end_index == -1:
                    break
                enclosed_texts.append(line[start_index + 1:end_index])
                start_index = end_index + 1
    return enclosed_texts

# 파일 경로
file_path = 'python_grammar.txt'

# 키워드를 저장하는 리스트
keyword_list = list(set(find_enclosed_texts(file_path, "'"))) + list(set(find_enclosed_texts(file_path, "\"")))



sample = """
def plus(a):
    return a+b"""

# 문자열을 바이트로 변환
sample_bytes = sample.strip().encode('utf-8')

# tokenize.tokenize() 함수를 사용하여 토큰으로 분할
sample_tokens = []
for tok in tokenize.tokenize(BytesIO(sample_bytes).readline):
    sample_tokens.append(tok)

# 맨 앞 ENCODING 빼주기
sample_tokens.pop(0)


S = []


# 현재 포지션 오른쪽에 아무것도 없는지 즉, 끝인지 확인
def finish_check(state):
    
    next = list(state[0].values())[0]
    if next.index("•") != (len(next)-1):
        return False

    else:
        return True
        
def next_nonterminal_check(state):
   
    next = list(state[0].values())[0]
    #next = next.split()
    idx = next.index("•") + 1

    #if next[idx] in grammar["terminal"] or next[idx] in operator:
    if next[idx] in terminal or next[idx] in keyword_list:
        return False
    else:
        return True

# 다음에 올수 있는것을 예측하는것 
def predictor(state, k, grammar):
    
    next = list(state[0].values())[0]
    idx = next.index("•") + 1
    
    for i in grammar[next[idx]]:
        if not ({next[idx]: ["•"]+i}, k) in S[k]:
            S[k].append(({next[idx]: ["•"]+i}, k))

# 실제로 확인하고 다음으로 넘어가는것
def scanner(state, k, words):

    next = list(state[0].values())[0]
    idx = next.index("•") + 1

    if state[1] < len(words) and k != len(words) and (next[idx] == "<"+token.tok_name[words[k].type]+">" or next[idx] == words[k].string) :

        t = copy.deepcopy(next)
        tmp =  t[idx]
        t[idx-1] = tmp
        t[idx] = "•"
        
        S[k+1].append(({(list(state[0].keys())[0]): t}, state[1]))
        
    
def completer(state, k):
    
    #s = []
    for st in S[state[1]]:
    
        next = list(st[0].values())[0]
        idx = next.index("•") + 1
        
        if "•"+list(state[0].keys())[0] in "".join(next): 
            t = copy.deepcopy(next)
            tmp = t[idx]
            t[idx-1] = tmp
            t[idx] = "•"
            #s.append(({(list(st[0].keys())[0]): t}, st[1]))
            S[k].append(({(list(st[0].keys())[0]): t}, st[1]))
             
            
    #for i in s:
    #    S[k].append(i)
        


def earley_parser(words, grammar):
    
    # init
    for i in range(0, len(words)+1):
        S.append([])
    
    S[0].append(({"γ": ["•","<file>"]}, 0))
    # S[0].append(({"γ": ["•","<interactive>"]}, 0))
    # S[0].append(({"γ": ["•","<eval>"]}, 0))
    # S[0].append(({"γ": ["•","<func_type>"]}, 0))
    
    for k in range(0, len(words)+1):
        print(k)
        
        for state in S[k]:
            # print(1)
            if not finish_check(state):
                # print(2)
                if next_nonterminal_check(state):
                    # print(3)
       
                    predictor(state, k, grammar)
                    # print(4)
                else:
                    # print(5)

                    scanner(state, k, words)
                    # print(6)
                    
            else:
                # print(7)

                completer(state, k)
                # print(8)
    
        for i in S[k]:
           print(i, k) 
                


earley_parser(sample_tokens, grammar)

# predictor(({'<function_def_raw>': ['def', '<NAME>', '(', '•', '<params>', ')', ':', '<block>']}, 0),3,grammar)

# k = 6
# print(f"•{sample_tokens[k].string}")
# print(f'S[{k}]')
# for i in S[k]:
    
    #if ''.join((i[0].keys())) == '<function_def_raw>':
    # print(i)
 

    

# S[3] (•
# S[6] params•)
    

# k인 경우 문자열 k번째 앞에 ㅇ 있는 경우


    
