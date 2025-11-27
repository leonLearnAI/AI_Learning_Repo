import pandas as pd
import numpy as np
from sklearn.discriminant_analysis import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler, minmax_scale

data = {
    'age': [25, 30, np.nan, 45, 60,30, 15],
    'salary': [50000,54000,60000,np.nan,100000,40000,20000],
    'country': ['USA', 'UK','China','USA','India','China','UK'], 
    'gender': ['M', 'F', 'F', 'M', 'M','F','F']
}

pd_data = pd.DataFrame(data)
# orginal data
print(pd_data)

imputer = SimpleImputer(strategy='mean')
numeric_feature = ['age','salary']
df_numeric = pd_data[numeric_feature]

imputer.fit(df_numeric)
pd_data[numeric_feature] = imputer.transform(df_numeric)
# imputed data
print(pd_data)

stander_scaler = StandardScaler()
# scaled data
df_numeric_scaler = pd_data[numeric_feature]
scalerd_numeric = stander_scaler.fit_transform(df_numeric_scaler)
pd_data[numeric_feature] = scalerd_numeric
print(pd_data)
# print the mean and standard deviation of the scaled data
print(scalerd_numeric.mean(), "-----",scalerd_numeric.std())