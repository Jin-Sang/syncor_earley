import parso
import io
import token



sample = "2+3*4"

grammar = {}

terminal = []

# 모든 토큰 타입과 해당하는 이름을 출력합니다.
for token_type, token_name in token.tok_name.items():
    terminal.append(token_name)

print(terminal)

# 원래
# terminal = ["N"]

'''
grammar = {"γ" : ["S"],
           "S" : ["S+M", "M"],
           "M" : ["M*T", "T"],
           "T" : ["1","2","3","4"]}

operator = ["+", "*"]
'''

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
    idx = next.index("•") + 1
    
    if next[idx] in grammar["T"] or next[idx] in operator:
        return False
    else:
        return True
    
def predictor(state, k, grammar):
    
    next = list(state[0].values())[0]
    idx = next.index("•") + 1
    for i in grammar[next[idx]]:
        if not ({next[idx]: "•"+i}, k) in S[k]:
            S[k].append(({next[idx]: "•"+i}, k))

def scanner(state, k, words):

    next = list(state[0].values())[0]
    idx = next.index("•") + 1
 
    if state[1] < len(words) and k != len(words) and next[idx] == words[k]:
        t = list(next)
        tmp = t[idx]
        t[idx-1] = tmp
        t[idx] = "•"
        
        S[k+1].append(({(list(state[0].keys())[0]): "".join(t)}, state[1]))
    
def completer(state, k):
    s = []
    for st in S[state[1]]:
    
        next = list(st[0].values())[0]
        idx = next.index("•") + 1
        
        if "•"+list(state[0].keys())[0] in next: 
            t = list(next)
            tmp = t[idx]
            t[idx-1] = tmp
            t[idx] = "•"
            s.append(({(list(st[0].keys())[0]): "".join(t)}, st[1]))
             
            
    for i in s:
        S[k].append(i)
        
   
            





def earley_parser(words, grammar):
    
    # init
    for i in range(0, len(words)+1):
        S.append([])
    
    S[0].append(({"γ": "•S"}, 0))
    
    for k in range(0, len(words)+1):
        print(k)
        for state in S[k]:
            
            if not finish_check(state):
                if next_nonterminal_check(state):
                    predictor(state, k, grammar)
                    
                else:
                    scanner(state, k, words)
                    
            else:
                completer(state, k)
                
        print(S[k])



#predictor(({"γ": "•S"}, 0), 0, grammar)

# earley_parser(sample, grammar)


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
    



    
