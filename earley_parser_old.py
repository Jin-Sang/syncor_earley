import parso
import io
import token
import tokenize
import copy


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



sample = "2+3*4"

grammar = {}

terminal = []

# 터미널에 해당하는 토큰 
for token_type, token_name in token.tok_name.items():
    terminal.append(token_name)




# 나무위키 예제 grammar

grammar = {"γ" : [["S"]],
           "S" : [["S","+","M"], ["M"]],
           "M" : [["M","*","T"], ["T"]],
           "T" : [["1"],["2"],["3"],["4"]]}

operator = [["+"], ["*"]]

S = []

code_token = []

# parso 렉서 장착 ()
grammar_parso = parso.load_grammar()
token_info = grammar_parso._tokenize(sample)

for info in token_info:
     code_token.append(info)


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
    if [next[idx]] in grammar["T"] or [next[idx]] in operator:
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
    
    if state[1] < len(words) and k != len(words) and next[idx] == words[k]:
        
        t = copy.deepcopy(next)
        tmp =  t[idx]
        t[idx-1] = tmp
        t[idx] = "•"
        
        S[k+1].append(({(list(state[0].keys())[0]): t}, state[1]))
    
def completer(state, k):
    
    s = []
    for st in S[state[1]]:
    
        next = list(st[0].values())[0]
        idx = next.index("•") + 1
        
        if "•"+list(state[0].keys())[0] in "".join(next): 
            t = copy.deepcopy(next)
            tmp = t[idx]
            t[idx-1] = tmp
            t[idx] = "•"
            s.append(({(list(st[0].keys())[0]): t}, st[1]))
             
            
    for i in s:
        S[k].append(i)
        
   
            





def earley_parser(words, grammar):
    
    # init
    for i in range(0, len(words)+1):
        S.append([])
    
    S[0].append(({"γ": ["•","S"]}, 0))
    
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
            print(i)        
        #print(S[k])



#predictor(({"γ": "•S"}, 0), 0, grammar)

earley_parser(sample, grammar)


import tokenize
from io import BytesIO

code = '''
def greet(name):
    print("Hello, " + name + "!")
'''

# 문자열을 토큰으로 분할하여 표시합니다.

#tokens = tokenize.tokenize(BytesIO(code.encode('utf-8')).readline)
#for token in tokens:
#    print(token)
#    print(tokenize.tok_name[token.type], token.string)
    



    
