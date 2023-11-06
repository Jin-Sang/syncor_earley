import pandas as pd

# mbpp 벤치마크를 DataFrame으로 가져오기

def make_data_set(file):
    
    json_data = pd.read_json(file)
    
    data_set = []
    
    for index, row in json_data.iterrows():
        
        text = f"\'\'\'%s\'\'\'\ndef" % row["prompt"]
        
        data_set.append(text)
        
    return data_set
