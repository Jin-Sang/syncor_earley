import pandas as pd

# mbpp 벤치마크를 DataFrame으로 가져오기

# Time out만 돌릴때
'''
with open ("timeout.txt", "r") as file:
    
    content = file.read()

t = list(map(int, content.split("\n")))    
'''
  


def make_data_set(file):
    
    json_data = pd.read_json(file)
    
    data_set = []
      
    for index, row in json_data.iterrows():
        
    
        text = f"\'\'\'%s\'\'\'\ndef" % row["prompt"]
        
        data_set.append((index, text))
    return data_set
