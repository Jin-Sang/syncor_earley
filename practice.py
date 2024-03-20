


import tokenize
from io import BytesIO
import token

# 주어진 수식
expression = """
def plus(a,b):
    return a+b"""

# 문자열을 바이트로 변환
expression_bytes = expression.encode('utf-8')

# tokenize.tokenize() 함수를 사용하여 토큰으로 분할
tokens = []
for tok in tokenize.tokenize(BytesIO(expression_bytes).readline):
    tokens.append(tok)

# 결과 출력
for tok in tokens:
    print(tok)
    print(tok.string)
    print(token.tok_name[tok.type])