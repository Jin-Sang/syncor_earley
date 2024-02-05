import make_data_set
import subprocess
import os
import sys
import csv

# parso로 generate 할것인지 선택
parso_on = sys.argv[1]

# True라면 parso_gen.py 파일 선택
if parso_on == "base":
    gen = "base_gen.py"
# False라면 base_gen.py 파일 선택
elif parso_on == "parso":
    gen = "parso_gen_codegpt.py"
# tmux : 몇 번째 도는지, subprocess, sys.arg

file = "/home/jskim/syncor/sanitized-mbpp.json"

data_set = make_data_set.make_data_set(file)

# time out 난 케이스만 돌릴 때 지정할 파일 

# timeout_file = "/home/jskim/syncor/timeout.csv"

# t_f = open(timeout_file)
# t_rdr = csv.reader(t_f)

# timeout = []

# for line in t_rdr:
#    timeout.append(int(line[0]))
    
    
    

for index, data in data_set:
    
    # time out 난 케이스만 돌리고 싶을 때 
    # 그냥 모두 돌리고 싶으면 주석 처리 
    #if not(index in timeout):
    #    continue
        
    
    # 종료 상태를 기록하기 위해 파일 경로를 파악한다.
    # 디렉터리 경로
    if parso_on == "base":
        directory_path = f"/home/jskim/syncor/log/"
    elif parso_on == "parso":
        directory_path = f"/home/jskim/syncor/log/parso_gen_ryumodel"
        
    # 파일명 생성
    file_name = f"{index}.txt"
    # 파일 경로
    file_path = os.path.join(directory_path, file_name)

    
    print(f"{index} case test!")
    
    
    # 정상 종료된 경우
    try:
        
        result = subprocess.run(["python", gen, f"{index}", f"{data}"], timeout=600, stdout=subprocess.PIPE, text=True, check=True)
        
        with open(file_path, "a") as file:
                file.write("\n\nEnd : In Time")
                
        print(result.stdout)
        
        
    # 타임 아웃으로 종료된 경우
    except subprocess.TimeoutExpired as e:
        with open(file_path, "a") as file:
                file.write("\n\nEnd : Timeout")
    
        print("time-out")
    # 에러로 종료된 경우    
    except subprocess.CalledProcessError as e:
        with open(file_path, "a") as file:
                file.write("\n\nEnd : Other Error")
    
