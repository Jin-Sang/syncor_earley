import parso

code = '''Math.sqrt(4'''
'''

grammar = parso.load_grammar()

module = grammar.parse(text_token)

errors = grammar.iter_errors(module) 

tree = parso.parse(text_token)

print(len(errors))
    
print(len(text_token.split('\n')))
print(len(text_token.split('\n')[-1]))

print(errors[0].end_pos)

print("----")
print(text_token.split('\n')[-1][25])
'''
try:
    tree = parso.parse(code)
except parso.parser.ParserSyntaxError as e:
    print("Parsing Error:", e)

try:
    rexing_errors = dir(parso.python.tokenize.PythonToken(code))
    print(rexing_errors)
    for error in rexing_errors:
        if error.type == 'error':
            print("Rexing Error at line {0}, column {1}: {2}".format(error.start[0], error.start[1], error.value))
except parso.parser.ParserSyntaxError as e:
    print("Parsing Error:", e)


