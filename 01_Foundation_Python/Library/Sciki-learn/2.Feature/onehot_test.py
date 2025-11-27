from codecs import ignore_errors
from encodings.punycode import T
from json import encoder
from sklearn.preprocessing import OneHotEncoder


data = [['red'], ['blue'], ['green'], ['red'], ['blue']]

encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
x_encoded = encoder.fit_transform(data)
print('Encoded data:')
print(x_encoded)
print(encoder.get_feature_names_out())

data2 = [['red'], ['blue'], ['yellow'], ['cyan'], ['blue']]
new_encode = encoder.transform(data2)
print('New encoded data:')
print(new_encode)
print(encoder.get_feature_names_out())