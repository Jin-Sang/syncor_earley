import os
import glob
import re
import csv

# CSV 파일명
#csv_file = "base_gen.csv"
csv_file = "parso_gen.csv"
# 디렉토리 경로 설정
#directory_path = '/home/jskim/syncor/log/base_gen'
directory_path = '/home/jskim/syncor/log/parso_gen'
# 디렉토리 내의 .txt 파일 가져오기
txt_files = glob.glob(os.path.join(directory_path, 'log_*_case.txt'))

# 파일 이름에서 숫자 부분 추출하여 정렬
def extract_number(file_name):
    match = re.search(r'log_(\d+)_case', file_name)
    if match:
        return int(match.group(1))
    return 0  # 매칭되는 숫자가 없을 경우 0 반환



# csv에 들어갈 데이터 (파일이름, 걸린 시간(타임 아웃 여부), 신택스 에러 여부)
log_list = [["Case_Number", "Processing_Time", "Syntax_Error" ]
            ]



# 각 .txt 파일에 대한 순회  

for txt_file in sorted(txt_files, key=extract_number):

    with open(txt_file, 'r') as file:
        
        # 파일 이름 
        name = extract_number(txt_file.split("/")[-1])
        
        # 파일 내용 읽어오기
        content = file.readlines()
        
        # Time Out 여부 확인
        time_out = content[-1].split(': ')[1].split(" >")[0]
        
        # 시간 안에 생성이 끝난 경우
        if time_out == "In Time":
            
            # 파일 내용을 읽어오기
            with open(txt_file, 'r') as file:
                
                content = file.read()
                
                # processing time 
                time = content.split("processing time : ")[-1].split("\n")[0]
            
                # syntax error check
                syn_err = content.split(f"processing time")[1].split("\n\n\n\n")[1].split("\n")[0].strip("-")
                
                # code
                # syntax error가 없을 때
                if syn_err == "No Syntax Error" :
                    code = content.split(f"{syn_err}--------\n\n")[1].split(f"\n\n\n<<<<<<<<<<<<< End : {time_out} >>>>>>>>>>>>")[0]
                    
                # syntax error가 있을 때
                else:
                    code = content.split(f"{syn_err}-----------\n\n")[1].split(f"\n\n\n\nError Start :")[0]
                    
            
        # Time Out 즉, 시간 초과 난 경우    
        elif time_out == "Timeout":
            
            # 시간 초과인 경우 이므로 다른 표시 없다.
            time = "Over"
            syn_err = "Pause"
            code = "Pause"
        
        # Other Error 인 경우
        elif time_out == "Other Error":
            time = "0"
            syn_err = "EMPTY"
            code = "EMPTY"
            
        # 파일이름, 걸린 시간(타임 아웃 여부), 신택스 에러 여부 추가
        log_list.append([name, time, syn_err])
        
        


with open(csv_file, mode='w', newline='') as file:
    
    # CSV 작성기 객체 생성
    writer = csv.writer(file)  

    # 데이터를 CSV 파일에 쓰기
    for row in log_list:
        writer.writerow(row)

print(f"{csv_file} 파일이 생성되었습니다.")
                 
        
    
    
    
    
    
