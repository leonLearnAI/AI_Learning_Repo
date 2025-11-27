from encodings.punycode import T
from sklearn.feature_extraction import DictVectorizer


data = [
    {'name': 'John', 'age': 20, 'city': 'New York', 'income': 40000},
    {'name': 'Jane', 'age': 30, 'city': 'Boston', 'income': 65000},
    {'name': 'Bob', 'age': 40, 'city': 'Chicago', 'income': 80000},
]

dict_vec = DictVectorizer(sparse=True)
x_dict = dict_vec.fit_transform(data)
print('Dictionary vectorized data:')
print(x_dict)
print('feature names:')
print(dict_vec.get_feature_names_out())