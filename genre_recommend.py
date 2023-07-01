import pandas as pd
import numpy as np
from ast import literal_eval
from googletrans import Translator

# 영화 추천 시스템 만들기(단순버전, 평점기준 - 알고리즘이 들어가지 않는)
# 장르 추천하는 코드


# 자료 읽어오기
md2 = pd.read_csv('data/tmdb_5000_credits.csv')
md = pd.read_csv('data/tmdb_5000_movies.csv')
md2.columns = ['id','tittle','cast','crew']
md= md.merge(md2,on='id')


# stack 메서드를 사용해 새로운 시리즈를 하나의 열로 쌓음.
# reset_index 메소드를 사용해 새로운 데이터프레임의 인덱스를 레벨 1로 재설정하고 원래 genres 열 삭제
# 장르의 결측지를 제거하고 다시 md의 값으로 넣어줌
md['genres'] = md['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])


# release_date 값에서 year 값을 분리하여 md 데이터프레임의 year 열에 저장(새로 생성)
for idx, date in enumerate(md['release_date']):
    if date != np.nan:
        year = str(date).split('-')[0]
    else:
        year = np.nan
    md.loc[idx, 'year'] = year


s = md.apply(lambda x: pd.Series(x['genres']), axis=1).stack().reset_index(level=1, drop=True)  # genres열에서 새로운 시리즈를 생성함
s.name = 'genre'
gen_md = md.drop('genres', axis=1).join(s)  # md의 genres열을 분리해서 새 gen_md 열을 생성함.
# 위에서 했던 자료들을 바탕으로 장르를 입력하면 순위 데이터프레임을 반환하는 함수 제작

def build_chart(genre, percentile=0.85):
    """각 장르별 차트 생성기"""
    df = gen_md[gen_md['genre'] == genre] # 장르로 데이터 뽑아 옴

    vc_notnull = df['vote_count'].notnull() # 투표 개수 null값 없는 것들만 변수에 담아 줌
    va_notnull = df['vote_average'].notnull() # 투표 평균 null값 없는 것들만 변수에 담아 줌
    vote_counts = df[vc_notnull]['vote_count'].astype('int') #int로 데이터타입 변경
    vote_averages = df[va_notnull]['vote_average'].astype('int') # int로 데이터타입 변경

    C = vote_averages.mean() # 투표의 평균값 계산
    m = vote_counts.quantile(percentile) # 투표갯수의 상위 15프로만 가져옴

    con1 = (df['vote_count'] >= m) # 조건1: 투표수가 상위 25프로 이내 있는 것
    # con2 = (df['vote_count'].notnull()) # 조건2: 투표수가 빈값이 없는 것(위에서 만들어온 조건과 같아서 생략)
    # con3 = (df['vote_average'].notnull()) # 조건3: 투표 평균중 빈값이 없는 것
    qualified = df[con1 & vc_notnull & va_notnull][['title', 'year', 'vote_count', 'vote_average', 'popularity']]

    # qualified = df[(df['vote_count'] >= m) & (df['vote_count'].notnull()) & (df['vote_average'].notnull())][
    #     ['title', 'year', 'vote_count', 'vote_average', 'popularity']]

    qualified['vote_count'] = qualified['vote_count'].astype('int') #int로 데이터타입 변경
    qualified['vote_average'] = qualified['vote_average'].astype('int')
    qualified['wr'] = qualified.apply(lambda x: calculate_wr(x['vote_count'], x['vote_average'], m, C), axis=1)
    # qualified['wr'] = qualified.apply( lambda x: (x['vote_count'] / (x['vote_count'] + m) * x['vote_average']) + (m / (m + x['vote_count']) * C),
    #     axis=1)
    qualified = qualified.sort_values('wr', ascending=False).head(250) #wr열(평점)에 따른 점수 오름차순으로 250개를 뽑아옴

    return qualified[['title', 'year', 'wr']]

def calculate_wr(vote_count, vote_average, m, C):
    """영화 평점에 대한 가중치 계산(mbid에 따름)"""
    return (vote_count / (vote_count + m) * vote_average) + (m / (m + vote_count) * C)


