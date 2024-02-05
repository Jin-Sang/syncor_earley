import parso

sample = "2+3*4"


# parso 렉서 장착 ()
grammar = parso.load_grammar()
token_info = grammar._tokenize(sample)

# 현재 포지션 오른쪽에 아무것도 없는지 즉, 끝인지 확인
def finish_check(state):
    next = list(state[0].values())[0]
    if next.find("•") != len(state):
        print(False)
    else:
        print(True)

def earley_parser(word, grammar):
    
    # init
    S = []
    for i in range(0, len(word)+1):
        S.append([])
    
    S[0].append(({"γ": "•S"}, 0))
    print(S[0])
    
    for k in range(0, len(word)+1):
        for state in S[k]:
            if not finish_check(state):
                
            
