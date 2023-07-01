import pandas as pd
import numpy as np


# 자료 읽어오기
md2 = pd.read_csv('tmdb_5000_credits.csv')
md = pd.read_csv('tmdb_5000_movies.csv')
md2.columns = ['id','tittle','cast','crew']
md= md.merge(md2,on='id')

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

def weighted_rating(x):
    """평점 구하기(상대적)"""
    v = x['vote_count']
    R = x['vote_average']
    return (v / (v + m) * R) + (m / (m + v) * C)

qualified['wr'] = qualified.apply(weighted_rating,
                                  axis=1)  # weighted_rating 을 wr이라는 열로 새로 생성해서 만든다. axis = 1값은 행값만 반환한다.
qualified = qualified.sort_values('wr', ascending=False).head(250)
qualified_list = qualified['title'].tolist()
# for idx, i in enumerate(qualified['title'].tolist()):
#     print(i, end=", ")
#     if idx % 10 == 9:
#         print()
