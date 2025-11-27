from sklearn.feature_extraction.text import CountVectorizer
from tracemalloc import stop


corpus = [
    'I love love machine learning',
    'Machine learning is fun',
    'I love coding in Python'
]

count_vec = CountVectorizer(min_df=1, stop_words='english')

X = count_vec.fit_transform(corpus)
print('Count vectorized data:')
print(X.toarray())
print('Vocabulary:')
print(count_vec.get_feature_names_out())