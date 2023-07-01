import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from nltk.stem.snowball import SnowballStemmer
from ast import literal_eval

# 자료 읽어오기
md2 = pd.read_csv('tmdb_5000_credits.csv')
md = pd.read_csv('tmdb_5000_movies.csv')
md2.columns = ['id', 'tittle', 'cast', 'crew']  # 4가지의 열만 지정
md = md.merge(md2, on='id')  # md2의 id 기준으로 두 자료를 병합한다.

id_not_null_df = pd.read_csv('tmdb_5000_movies.csv')
con_id_not_null = id_not_null_df['id'].notnull()  # 조건 생성(id가 null값이면 안 됨)
id_not_null_df = id_not_null_df[con_id_not_null]['id'].astype('int')
# print(id_not_null_df)

md['id'] = md['id'].astype('int')  # str값인 id를 int값으로 변경해주기
smd = md[md['id'].isin(id_not_null_df)]  # 그리고 빈값이 포함되지 않는 데이터를 smd데이터로 담아둠

# print(smd.shape) # 컬럼 열 출력하기

# 태그라인, 개요의 결측값을 ''로 채워줌
smd['tagline'] = smd['tagline'].fillna('')  # 결측값을 ''로 채워줌
smd['overview'] = smd['overview'] + smd['tagline']  # 개요 열에 태그라인 열까지 합해주고
smd['overview'] = smd['overview'].fillna('')  # 결측값을 ''로 채워줌
# print(smd['overview'])


#=============================================================================================

# # 등장인물과 배우들의 키워드를 뽑아서 비교한다.
# smd['cast'] = smd['cast'].apply(literal_eval)  # 배우들 - 여기서 메인 캐릭터들만 추출 / literal_eval을 사용해서 리스트화
# smd['crew'] = smd['crew'].apply(literal_eval)  # 영화제작자들 - 여기서 감독만 추출 / literal_eval을 사용해서 리스트화
# smd['keywords'] = smd['keywords'].apply(literal_eval)  # 키워드 / literal_eval을 사용해서 리스트화
# smd['cast_size'] = smd['cast'].apply(lambda x: len(x))  # 배우들의 수를 세서 cast_size라는 새 열을 생성함
# smd['crew_size'] = smd['crew'].apply(lambda x: len(x))  # 제작자들의 수를 세서 crew_size라는 새 열을 생성함
#
#
# # 제작자에서 감독 이름만 추출하는 부분
# def get_director(x):
#     """특정 영화에서 감독 이름만 반환함"""
#     for i in x:  # json 형식이기 때문에 딕셔너리 형식으로 값들이 들어 있음
#         if i['job'] == 'Director':  # 만약 감독이 있다면
#             return i['name']  # 이름 반환
#     return np.nan  # 만약 감독이 없다면 none값 반환함
#
#
# smd['director'] = smd['crew'].apply(get_director)  # 위에서 제작한 함수를 사용해 감독만 추출해서 director열을 생성하여 그 값을 넣음
#
# # cast 열에서 list 자료형임을 확인하고 이름만 담아줌
# for i, x in smd['cast'].items():  # cast Series에서 자료 확인
#     if isinstance(x, list):  # 만약 type이 list이면
#         cast_list = []  # cast_list 라는 빈 리스트 생성하고
#         for j in x:  # 들어있는 자료들을 for문 돌려서(json형식이라 딕셔너리 안에 딕셔너리 들어있는 구조)
#             cast_list.append(j['name'])  # 빈 리스트에 이름만 추가해 준다.
#         smd.at[i, 'cast'] = cast_list  # at- 패스트 인덱싱. loc와 유사하며 1개의 값만 가진 자료구조에 접근하려 할 때 사용한다. loc보다 조금 더 빠른 속도가 나옴
#     else:
#         smd.at[i, 'cast'] = []
# # smd['cast'] = smd['cast'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else []) #이렇게도 사용할 수 있음. 위의 for문과 속도는 비슷한 것 같음
# smd['cast'] = smd['cast'].apply(lambda x: x[:3] if len(x) >= 3 else x)  # 배우들의 수를 세서 3명까지만 이름을 잘라줌.
#
# # cast 열에서 list 자료형임을 확인하고 내용 소문자로 변경해줌
# for i, x in smd['cast'].items():
#     if isinstance(x, list):  # 자료들이 리스트에 담겨있으면
#         cast_list = []  # 빈 리스트를 만들고
#         for j in x:  # 소문자로 변경시켜서 이름들을 넣는다
#             cast_list.append(str.lower(j.replace(", ", "")))
#         smd.at[i, 'cast'] = cast_list  # 그리고 smd 테이블 cast 열에 추가해 준다.
#     else:
#         smd.at[i, 'cast'] = []
#
# # keyword 열에서 list 자료형임을 확인하고 이름만 담아줌
# # print(smd.keywords)
# for i, x in smd['keywords'].items():
#     if isinstance(x, list):  # 자료가 리스트형이면
#         keyword_list = []  # 빈 리스트를 생성하고
#         for j in x:  # 그 자료들 안에 있는 값들을 for문 돌려서
#             keyword_list.append(j['name'])  # 빈 리스트에 이름들을
#         smd.at[i, 'keywords'] = keyword_list
#     else:
#         smd.at[i, 'keywords'] = []
#
# # 자료 중 감독의 열을 모두 str 타입으로 형변환 해주고 apply 함수를 사용하여 열값이 빈값이라면 없애준다.
# smd['director'] = smd['director'].astype('str').apply(lambda x: str.lower(x.replace(" ", "")))
# smd['director'] = smd['director'].apply(lambda x: [x, x, x])  # 감독의 값을 3개 넣어주어서 리스트에 담아준다.
# # print(smd['director']) # 감독이 3번씩 나옴
#
# '''
# 'smd'에서 'keywords' 컬럼에 있는 모든 값을 하나의 시리즈로 변환하고, 이를 스택으로 쌓은 뒤 인덱스를 레벨1로 리셋하는 코드
# 즉, 모든 영화의 키워드를 하나의 열로 쌓아놓고, 이를 인덱스로 구분하여 사용하기 쉬운 형태로 만드는 것.
# '''
# s = pd.Series() # 시리즈 하나를 생성함
# for index, row in smd.iterrows(): #for문을 돌려 keywords 열 값만 시리즈에 넣어줌
#     s = s._append(pd.Series(row['keywords']), ignore_index=True)
# # print(s)
# s.name = 'keyword' # s의 이름을 keyword로 설정해줌
# s = s.value_counts() # 키워드 값 순으로 정렬해줌(가장 많이 나온 순위대로)
# s = s[s>1] # 1이 가장 많이 나오므로 1이 나오는 값은 생략해준다.
# # print(s)
#
# stemmer = SnowballStemmer('english') # 영어 어간을 잘라주는 변수 stemmer 생성 예) eaten -> eat
#
# # 키워드 하나의 리스트에 넣기
# def filter_keywords(x):
#     """제시된 모든 키워드를 리스트에 넣고 리스트 리턴함."""
#     words = []
#     for i in x:
#         if i in s:
#             words.append(i)
#     return words
#
# smd['keyword'] = smd['keywords'].apply(filter_keywords) # 키워드 열을 모두 적용한다.
# for i in range(len(smd['keywords'])):
#     keywords = smd['keywords'][i] #키워드 열의 i번째 값들을 가져와서
#     stemmed_keywords = [stemmer.stem(keyword) for keyword in keywords] #어간 잘라주는 stemmer 사용해서 키워드들을 모두 잘라서 리스트에 넣음
#     # smd['keyword'][i] = stemmed_keywords # 만든 리스트 값을 다시 키워드 열값에 저장함.
#     smd.loc[i, 'keyword'] = stemmed_keywords
#     '''SettingWithCopyWarning: A value is trying to be set on a copy of a slice from a DataFrame 오류'''
#
# ## 여기서부터 이해 시작 ====================
# smd['keyword'] = smd['keywords'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
# smd['genres'] = smd['genres'].apply(lambda  x: [str.lower(i.replace(", ","")) for i in x])
#
#
# # 새로운 열 soup를 제작한다. keyword, cast, director, genres 다 있는 행
# # smd['keyword'] + smd['cast'] + smd['director'] + smd['genres']
# # print(smd['keyword']) # -- 리스트화 완
# # print(smd['cast']) # -- 리스트화 완
# # print(smd['director']) # --리스트화 되어 있음
# # print(smd['genres']) # -- 이게 튜플 형식으로 되어 있었음! 리스트화 시킴

# ==================================================================================================

# 개요, 태그라인에서 단어들을 뽑아서 분석
# analyer: 학습단위 결정 - word(단어로 설정)
# ngram_range: 단어의 묶음 - (1,2) 1개부터 2개까지
# min_df: 정수 또는 [0.0, 1.0] 사이의 실수. 디폴트는 1, 단어장에 포함되기 위한 최소 빈도
# stop_words: 문자열 {‘english’}, 리스트 또는 None (디폴트)
tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
tfidf_matrix = tf.fit_transform(smd['overview'])  # 개요의 텍스트 벡터화
# 코사인 유사도 구하기 - 모든 영화의 데이터에서 코사인 유사도를 구한다.
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)  # fit_transform으로 구한 벡터 2가지의 유사성을 비교한다.

# 유사도를 기준으로 영화를 추천한다.
smd = smd.reset_index()  # 인덱스 리셋

titles = smd['title']  # smd의 title 열을 가져온다.
indices = pd.Series(smd.index, index=smd['title'])  # 인덱스값을 영화명으로 바꾸고, 내용을 인덱스 값으로 바꿔준다.


# print(indices)

def get_recommendations(title):
    """영화 제목에 따라 추천해주기"""
    idx = indices[title]  # 영화명에 따른 인덱스 값을 가져옴
    sim_scores = list(
        enumerate(cosine_sim[idx]))  # 숫자와 유사도를 튜플 형식으로 모은 후 이를 리스트에 담는다. -> [(0, 0.0), (1, 0.000223434323242)]
    sim_scores = sorted(sim_scores, key=lambda x: x[1],
                        reverse=True)  # 튜플 형식 중 1번째 값, 즉 유사도 높은 순으로 정렬해서 다시 sorted_score에 담는다.
    sim_scores = sim_scores[1:31]  # 이 자료들을 1부터 30위까지만 다시 sorted_score에 담는다.
    movie_indices = [i[0] for i in sim_scores]  # 유사도 기준으로 오름차순한 자료에서 인덱스 값만 다시 담는다 -> 이를 비교해서 영화 정보를 담기 위함
    results = []

    for idx, i in enumerate(movie_indices):
        condition = (smd['index'] == movie_indices[idx])
        result = smd.loc[condition, ['title', 'release_date', 'vote_average']]
        results.append(result)
    df = pd.concat(results, ignore_index=True)

    return df  # 영화 타이틀에서 인덱스 값을 기준으로 제목, 출시일자, 평균 투표 점수를 리턴함(데이터프레임으로 만들어서)
