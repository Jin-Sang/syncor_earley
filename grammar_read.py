s = ""

with open('grammar.txt', 'r') as file:
    for line in file:
        # '#'으로 시작하는 줄은 건너뜁니다.
        if not line.startswith('#'):
            s += line  # 줄 바꿈 문자 제거 후 출력
            
with open('grammar1.txt', 'w') as file:    
    
    file.write(s)          

# 입력 파일 경로 및 이름
input_file = 'grammar1.txt'

# 출력 파일 경로 및 이름
output_file = 'grammar2.txt'

# 입력 파일 열기
with open(input_file, 'r') as f:
    lines = f.readlines()

# 공백 줄 제거
non_empty_lines = [line for line in lines if line.strip()]

# 출력 파일에 쓰기
with open(output_file, 'w') as f:
    f.writelines(non_empty_lines)

print("공백 줄이 제거된 파일이 생성되었습니다.")
    



# 파일을 쓰기 모드로 열고 문자열 쓰기

    