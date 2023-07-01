import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from nltk.stem.snowball import SnowballStemmer

# 영화 추천 시스템 만들기(단순버전, 평점기준 - 알고리즘이 들어가지 않는)

# 자료 읽어오기
md2 = pd.read_csv('tmdb_5000_credits.csv')
md = pd.read_csv('tmdb_5000_movies.csv')
md2.columns = ['id','tittle','cast','crew']
md= md.merge(md2,on='id')
print(md2.columns)
print(md.columns)
# print(md.head())
# print(md.shape)

# 장르의 결측지를 제거하고 다시 md의 값으로 넣어줌
md['genres'] = md['genres'].fillna('[]').apply(literal_eval).apply(
    lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

# 전체 정보의 투표 평균을 재 준다. 투표 갯수와 투표 평균에서 빈 값이 없는 자료만 가져와 준다.
vote_counts = md[md['vote_count'].notnull()]['vote_count'].astype('int')
vote_averages = md[md['vote_average'].notnull()]['vote_average'].astype('int')

C = vote_averages.mean()  # 투표 평균값을 만들어 주고
# print(C)  # 평균값: 5.xxx

m = vote_counts.quantile(0.80)  # m은 차트에 들어갈 최소 투표수, 백분율 95까지 넣어준다. (상위 5프로의 값)
# print(m)  # 상위 갯수는 3040.xxx

# datetime 값에서 year 값을 분리하여 md 데이터프레임의 year 열에 저장
md['year'] = pd.to_datetime(md['release_date'], errors='coerce').apply(
    lambda x: str(x).split('-')[0] if x != np.nan else np.nan)  # 변환중에 발생한 오류가 모두 NaT 값으로 변경됨

# 제목, 년도, 투표수, 평점, 인기도, 장르 열을 선택 / 조건: 투표수와 평점 열이 null이 아니고, 최소 투표 수 이상의 값을 가진 영화만 필터링
qualified = md[(md['vote_count'] >= m) & (md['vote_count'].notnull()) & (md['vote_average'].notnull())][
    ['title', 'year', 'vote_count', 'vote_average', 'popularity', 'genres']]

qualified['vote_count'] = qualified['vote_count'].astype('int')  # 투표수를 데이터 타입을 정수형으로 변환
qualified['vote_average'] = qualified['vote_average'].astype('int')  # 투표 평균을 정수형으로 변환. 위와 같음.
# print(qualified.shape)  # 데이터프레임의 쉐입을 반환한다. (241, 6) ->


# 차트에 들어갈 데이터를 함수화 해서 구한다.
def weighted_rating(x):
    """평점 구하기(상대적)"""
    v = x['vote_count']
    R = x['vote_average']
    return (v / (v + m) * R) + (m / (m + v) * C)


qualified['wr'] = qualified.apply(weighted_rating,
                                  axis=1)  # weighted_rating 을 wr이라는 열로 새로 생성해서 만든다. axis = 1값은 행값만 반환한다.
qualified = qualified.sort_values('wr', ascending=False).head(250)  # wr을 값 기준으로 오름차순 정렬을 하고 250행만 출력한다.
# print(qualified.head(10))  # 영화의 평점순위대로 값이 출력된다.

s = md.apply(lambda x: pd.Series(x['genres']), axis=1).stack().reset_index(level=1, drop=True)  # genres열에서 새로운 시리즈를 생성함
s.name = 'genre'
gen_md = md.drop('genres', axis=1).join(s)  # md의 genres열을 분리해서 새 gen_md 열을 생성함.
# print(gen_md)

print(qualified.sort_values('wr'))

# stack 메서드를 사용해 새로운 시리즈를 하나의 열로 쌓음.
# reset_index 메소드를 사용해 새로운 데이터프레임의 인덱스를 레벨 1로 재설정하고 원래 genres 열 삭제


# 위에서 했던 자료들을 바탕으로 장르를 입력하면 순위 데이터프레임을 반환하는 함수 제작
def build_chart(genre, percentile=0.85):
    """각 장르별 차트 생성기"""
    df = gen_md[gen_md['genre'] == genre]
    vote_counts = df[df['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = df[df['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(percentile)

    qualified = df[(df['vote_count'] >= m) & (df['vote_count'].notnull()) & (df['vote_average'].notnull())][
        ['title', 'year', 'vote_count', 'vote_average', 'popularity']]
    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')

    qualified['wr'] = qualified.apply(
        lambda x: (x['vote_count'] / (x['vote_count'] + m) * x['vote_average']) + (m / (m + x['vote_count']) * C),
        axis=1)
    qualified = qualified.sort_values('wr', ascending=False).head(250)

    return qualified


# 로맨스 영화 순위 반환
# print(build_chart('Romance').head(15))

# 장르들의 중복 없는 값들 추출
md['genres'] = md['genres'].apply(tuple)  # 리스트 형식의 데이터를 해시 가능한 형식으로 벼환 리스트 -> 튜플
unique_values = md['genres'].unique()

# g_list = []
# for gs in unique_values:
#     for g in gs:
#         if g not in g_list:
#             g_list.append(g) # 장르 추출
#
# print(g_list)

'''
영화 장르들
['Action', 'Adventure', 'Fantasy', 'Science Fiction', 'Crime', 'Drama', 'Thriller', 
'Animation', 'Family', 'Western', 'Comedy', 'Romance', 'Horror', 'Mystery', 'History', 
'War', 'Music', 'Documentary', 'Foreign', 'TV Movie']
'''
#
# # 호러 영화 순위 반환
# print(build_chart('Horror').head(15))
# ===================여기서부터 ======================================

# 내용 기반으로 영화 추천하기 - 영화의 속성값 저장
# TF-IDF를 연산할 때 데이터에 Null 값이 들어가면 에러가 발생한다. 결측값에 해당하는 Null 값 확인하고 지워줌
id_not_null_df = pd.read_csv('tmdb_5000_movies.csv')
con_id_not_null = id_not_null_df['id'].notnull()
id_not_null_df = id_not_null_df[con_id_not_null]['id'].astype('int')
# md = md.drop([[19730, 19530, 35587]])
md['id'] = md['id'].astype('int')
smd = md[md['id'].isin(id_not_null_df)]
# print(smd.shape)
# print(smd.columns) # 컬럼 열 출력하기
smd['tagline'] = smd['tagline'].fillna('')
smd['overview'] = smd['overview'] + smd['tagline']
smd['overview'] = smd['overview'].fillna('')

tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
tfidf_matrix = tf.fit_transform(smd['overview'])
# (4803, 149317) 4800 행을 가지고 149317의 열을 가지는 행렬이다.
# print(tfidf_matrix.shape)

# 코사인 유사도 구하기 - 모든 영화의 데이터에서 코사인 유사도를 구한다.
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
# print(cosine_sim[0])

# 유사도를 기준으로 영화를 추천한다.
smd = smd.reset_index()
titles = smd['title']
indices = pd.Series(smd.index, index=smd['title'])


def get_recommendations(title):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:31]
    movie_indices = [i[0] for i in sim_scores]
    return titles.iloc[movie_indices]


# print(get_recommendations('The Godfather').head(10))


# 등장인물과 배우들의 키워드를 뽑아서 비교한다.
# 배우는 3명 선택 예정
smd['cast'] = smd['cast'].apply(literal_eval)
smd['crew'] = smd['crew'].apply(literal_eval)
smd['keywords'] = smd['keywords'].apply(literal_eval)
smd['cast_size'] = smd['cast'].apply(lambda x: len(x))
smd['crew_size'] = smd['crew'].apply(lambda x: len(x))


def get_director(x):
    for i in x:
        if i['job'] == 'Director':
            return i['name']
    return np.nan


smd['director'] = smd['crew'].apply(get_director)
smd['cast'] = smd['cast'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
smd['cast'] = smd['cast'].apply(lambda x: x[:3] if len(x) >= 3 else x)
smd['keywords'] = smd['keywords'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])


smd['cast'] = smd['cast'].apply(lambda x: [str.lower(i.replace(", ",""))for i in x])
smd['director'] = smd['director'].astype('str').apply(lambda x: str.lower(x.replace(" ", "")))
smd['director'] = smd['director'].apply(lambda x: [x,x, x])

s = smd.apply(lambda x: pd.Series(x['keywords']), axis=1).stack().reset_index(level=1, drop=True)
s.name = 'keyword'
s = s.value_counts()
# print(s[:5])

s = s[s>1]
stemmer = SnowballStemmer('english') #영어 어간을 잘라줌

# 키워드 필터링 해주는 함수 만들기
def filter_keywords(x):
    words = []
    for i in x:
        if i in s:
            words.append(i)
    return words

smd['keyword'] = smd['keywords'].apply(filter_keywords)
smd['keyword'] = smd['keywords'].apply(lambda x: [stemmer.stem(i) for i in x])
smd['keyword'] = smd['keywords'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
smd['genres'] = smd['genres'].apply(lambda  x: [str.lower(i.replace(", ","")) for i in x])

# 새로운 열 soup를 제작한다. keyword, cast, director, genres 다 있는 행
# smd['keyword'] + smd['cast'] + smd['director'] + smd['genres']
# print(smd['keyword']) # -- 리스트화 완
# print(smd['cast']) # -- 리스트화 완
# print(smd['director']) # --리스트화 되어 있음
# print(smd['genres']) # -- 이게 튜플 형식으로 되어 있었음! 리스트화 시킴
smd['soup'] = smd['keyword'] + smd['cast'] + smd['director'] + smd['genres']

smd['soup'] = smd['soup'].apply(lambda x: ' '.join(x))

count = CountVectorizer(analyzer='word', ngram_range=(1, 2), min_df=0, stop_words='english')
count_matrix = count.fit_transform(smd['soup'])

consine_sim = cosine_similarity(count_matrix, count_matrix)
smd = smd.reset_index()
titles = smd['title']
indices = pd.Series(smd.index, index = smd['title'])

# print(get_recommendations('Eternal Sunshine of the Spotless Mind').head(10))


def improved_recommendations(title):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:26]
    movie_indices = [i[0] for i in sim_scores]

    movies = smd.iloc[movie_indices][['title', 'vote_count', 'vote_average', 'year']]
    vote_counts = movies[movies['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = movies[movies['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(0.60)

    qualified = movies[
        (movies['vote_count'] >= m) & (movies['vote_count'].notnull()) & (movies['vote_average'].notnull())]
    qualified.loc[:, 'vote_count'] = qualified['vote_count'].astype('int')
    qualified.loc[:, 'vote_average'] = qualified['vote_average'].astype('int')
    qualified = qualified.copy()
    # A value is trying to be set on a copy of a slice from a DataFrame. Try using .loc[row_indexer,col_indexer] = value instead 오류 해결하기 위해 copy() 사용
    qualified['wr'] = qualified.apply(weighted_rating, axis=1)
    qualified = qualified.sort_values('wr', ascending=False).head(10)
    return qualified


