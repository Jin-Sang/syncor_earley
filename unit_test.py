import pandas as pd
import ast
import subprocess


# 함수 이름 찾기

def extract_function_name(code_string):
    # 문자열을 파싱하여 AST 생성
    tree = ast.parse(code_string)
    
    # AST 노드를 순회하며 함수 이름 찾기
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
    
    return function_name

# mbpp에서 입출력, 정답 코드 함수 이름 가져오기
def make_unit_test(file):
    
    json_data = pd.read_json(file)
    
    test_set = []
      
    for index, row in json_data.iterrows():
    
        # assert문
        test_assert = row["test_list"]
        # 정답 code
        answer_code = row["code"]
        # 정답 code의 def 이름
        original_def_name = extract_function_name(answer_code)
        
        test_set.append((index, test_assert, original_def_name))
        
    return test_set

# unit 테스트 입출력 (assert문)
test_units = make_unit_test('/home/jskim/syncor/sanitized-mbpp.json')

# llm과 Parso로 만든 코드 
#df = pd.read_csv('/home/jskim/syncor/csv/parso_gen_revision.csv')
# base
df = pd.read_csv('/home/jskim/syncor/csv/base_gen_1.csv')


# 총 테스트 유닛의 갯수 (총점)
total_score = 0

for unit in test_units:
    for _ in unit[1]:   
        total_score += 1

# 몇개를 통과하는지 체크하는 변수
pass_score = 0

# 각 문제별로 정오표 
each_scores = []

Assertion_Error = 0
Type_Error = 0
Typesignature_Error = 0
ZeroDivision_Error = 0
Name_Error = 0
Index_Error = 0
Other_Error = 0
FileNotFound_Error = 0
Attribute_Error = 0 
Recursion_Error = 0 
Value_Error = 0 

# llm이 만든 문제 코드 행을 반복
for index, row in df.iterrows():
    #if index in [184, 357, 400]:
    #    continue
    # No Syntax Error인 경우
    if row['Syntax_Error'] == 'No Syntax Error':
        # llm이 만든 코드
        code = row['Code']
        
        # llm이 만든 코드의 함수이름
        def_name = extract_function_name(code)
       
        # 개별 문제의 테스트 갯수
        each_problem=len(test_units[index][1])
        # 개별 문제의 통과 갯수
        each_pass = 0
        for unit in test_units[index][1]:
            # 정답 함수의 이름을 우리가 만든 함수 이름으로 바꿔준다.
            change_assert = unit.replace(test_units[index][2], def_name)
            test_code = code+"\n"+change_assert
            try:
                exec(test_code)
                print(f"{index} {change_assert} -> pass")
                each_pass += 1
                pass_score += 1
            except TypeError as e:
                print(f"{index} {change_assert} -> Type Error")
                Type_Error += 1
                with open("typetest.py","w") as file:
                    file.write(test_code)
                result = subprocess.run(['mypy', 'typetest.py'], capture_output=True, text=True)
                if result.returncode != 0 :
                    Typesignature_Error += 1 
                    with open('typetest_log.txt', "a") as file:
                        file.write(f"{index} {change_assert} \n") 
                        file.write(result.stdout+"\n")   
                continue
            except AssertionError as e:
                print(f"{index} {change_assert} -> Assertion Error")
                Assertion_Error += 1 
                continue
            
            except ZeroDivisionError as e:
                print(f"{index} {change_assert} -> ZeroDivision Error")
                ZeroDivision_Error += 1 
                continue
            
            except NameError as e:
                print(f"{index} {change_assert} -> Name Error")
                Name_Error += 1 
                continue
            
            except IndexError as e:
                print(f"{index} {change_assert} -> Index Error")
                Index_Error += 1 
                continue
            
            except FileNotFoundError as e:
                print(f"{index} {change_assert} -> FileNotFound Error")
                FileNotFound_Error += 1 
                continue
            except AttributeError as e:
                print(f"{index} {change_assert} -> Attribute Error")
                Attribute_Error += 1 
                continue
            except RecursionError as e:
                print(f"{index} {change_assert} -> Recursion Error")
                Recursion_Error += 1 
                continue
            except ValueError as e:
                print(f"{index} {change_assert} -> Value Error")
                Value_Error += 1 
                continue
            except:
                print(f"{index} {change_assert} -> Other Error")
                Other_Error += 1
                with open('other_error.txt', 'a') as file:
                    file.write(f"{index} {change_assert} \n") 
        each_scores.append((index, f"{each_pass}/{each_problem}"))
        # print(f"{index} : {each_pass}/{each_problem}")    

for i in each_scores:
          
    print(i)

print(f"total score : {total_score}")
print(f"pass score : {pass_score}")


print(f"Assertion Error : {Assertion_Error}")
print(f"Type Error : {Type_Error}")
print(f"->Typesignature Error : {Typesignature_Error}")
print(f"Name Error : {Name_Error}")
print(f"Index Error : {Index_Error}")
print(f"Zerodivision Error : {ZeroDivision_Error}")
print(f"FileNotFound_Error : {FileNotFound_Error}")
print(f"Attribute_Error : {Attribute_Error}")
print(f"Recursion_Error : {Recursion_Error}")
print(f"Value_Error : {Value_Error}")
print(f"Other Error : {Other_Error}")
