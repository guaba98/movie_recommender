# from ast import literal_eval
#
# test_string = '[1, 2, 3]' # str타입
# print(test_string, type(test_string)) # [1, 2, 3] <class 'str'>
# res = literal_eval(test_string)
# print(res, type(res)) # [1, 2, 3] <class 'list'>
#


import pandas as pd
from ast import literal_eval

## 데이터프레임 생성
df = pd.DataFrame()
df['LIST'] = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
df['TUPLE'] = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
df['DICT'] = [{'a': 'b'}, {'c': 'd'}, {'e': 'f'}]

# print(df)

## 데이터 본래 타입으로 변환
for col in df.columns:
    df[col] = df[col].map(lambda x:literal_eval(x))

print(df)

print(type(df['LIST'].iloc[0]))
print(type(df['TUPLE'].iloc[0]))
print(type(df['DICT'].iloc[0]))