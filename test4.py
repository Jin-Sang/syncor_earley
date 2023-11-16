import parso


text_token = """if True:
print()"""



grammar = parso.load_grammar()

module = grammar.parse(text_token)

errors = grammar.iter_errors(module) 

e = grammar._tokenize(text_token)

'''
for m in module.children:
    print(m)
'''
for i in e:
    if str(i.type) == "PythonTokenTypes.NAME":
        print("yes")

#print(module.children[0].children)
'''
for i in errors:
    print(i.start_pos)
    print(i.end_pos)
print(module.children[-1])

'''