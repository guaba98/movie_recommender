# from sklearn.feature_extraction.text import TfidfVectorizer
#
# corpus = [ 'you know I want your love', 'I like you', 'what should I do ' ]
# tfidfv = TfidfVectorizer().fit(corpus)
# print(tfidfv.vocabulary_)
# print("="*100)
# print(tfidfv.transform(corpus).toarray())
# print("="*100)
# print(tfidfv.fit_transform(corpus).toarray())
#
# print(tfidfv.fit_transform(corpus))

# from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
corpus = [ 'you know I want your love', 'I like you', 'what should I do ' ]
tfidfv = TfidfVectorizer().fit(corpus)
tfidf_matrix = tfidfv.fit_transform(corpus)
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
cosine_sim

