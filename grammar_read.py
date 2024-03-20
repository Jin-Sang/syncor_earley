import token

# 파일을 읽기 모드로 엽니다.
# grammar dict 만들기
with open('python_grammar.txt', 'r') as file:
    # 파일의 모든 줄을 읽어들입니다.
    lines = file.read()
    divided_tokens = lines.split("★")
    
grammar = {}
tokens = []
divided_tokens.pop()

for devided_token in divided_tokens:

    a, b = devided_token.split(":", 1)
    key = a.strip()
    values = b.strip().split("\n")
    dic_value = []
    for value in values:
        each = value.strip()[2:]#.replace(" ","")
        cleaned_chars = [char for char in each if char != '\'' and char != '\"']
        cleaned_string = ''.join(cleaned_chars)
        cleaned_list = cleaned_string.split()
        dic_value.append(cleaned_list)
    grammar[key] = dic_value

# terminal 만들어주기 
terminal = []

for token_type, token_name in token.tok_name.items():
    terminal.append("<"+token_name+">")

# 터미널 설정해주기
grammar["<terminal>"] = terminal
        
operator = []


    
import tokenize
from io import BytesIO

# 주어진 수식
expression = """
def def():
    return 2+3*4"""

# 문자열을 바이트로 변환
expression_bytes = expression.encode('utf-8')

# tokenize.tokenize() 함수를 사용하여 토큰으로 분할
tokens = []
for tok in tokenize.tokenize(BytesIO(expression_bytes).readline):
    tokens.append(tok)

# 결과 출력
for token in tokens:
    print(token)
    

    
print(grammar["<func_type>"])
    

with open('OP.txt', 'r') as file:
    # 파일의 모든 줄을 읽어들입니다.
    lines = file.readlines()
    
    for line in lines:
        operator.append(line.split()[1].strip())
import parso
# parso 렉서 장착 ()
grammar_parso = parso.load_grammar()
token_info = grammar_parso._tokenize(expression)

for info in token_info:
     print(info)