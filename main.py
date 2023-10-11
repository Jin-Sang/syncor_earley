from transformers import pipeline
import string
import json
import parso

# Load the grammar
grammar = parso.load_grammar()

mbpp = []
with open("sanitized-mbpp.json", "r") as dataset:
    mbpp = json.load(dataset)


autocompletion_pipeline = pipeline(task="text-generation", model="microsoft/CodeGPT-small-py-adaptedGPT2", \
    num_beams=5, pad_token_id = 50256, no_repeat_ngram_size=3, early_stopping=True)

prompt_no_code = string.Template(r'''Q : Write a python function that sums two integers.<EOL>A : <s>def sum(i1,i2):<EOL>    return i1 + i2 </s><EOL>Q : Write a function that split a string at spaces.<EOL>A : <s>def split(s):<EOL>    return s.split() </s><EOL>Q : $question<EOL>A : ''')


prompt = string.Template(r'''Q : Write a python function that sums two integers.<EOL>A : <s>def sum(i1,i2):<EOL>    return i1 + i2 </s><EOL>Q : Write a function that split a string at spaces.<EOL>A : <s>def split(s):<EOL>    return s.split() </s><EOL>Q : $question<EOL>A : <s>$init_code''')

for task in mbpp[1:2]:
    prompt_no_code = prompt_no_code.substitute(question=task['prompt'])
    len_prompt = len(prompt_no_code)

    init_code = "<s>"
    for line in task['code'].split('\n'):
        if "def" in line:
            init_code += line + "<EOL>"
            break
        init_code += line + "<EOL>"

    prompt = prompt.substitute(question=task['prompt'], init_code=init_code)

    # Generate autocompletions
    autocompletions = autocompletion_pipeline(init_code, max_new_tokens=15, num_return_sequences=2)

    print(f"Prompt: {prompt}")
    
    # Print the autocompletions
    for idx, completion in enumerate(autocompletions):
        target_code = completion['generated_text'][len_prompt:]
        print(f"Target code: {target_code}")
        print(f"Autocompletion {idx + 1}: {completion['generated_text']}")
        module = grammar.parse(target_code)
        elist = grammar.iter_errors(module)
        for e in elist:
            print(e.start_pos)