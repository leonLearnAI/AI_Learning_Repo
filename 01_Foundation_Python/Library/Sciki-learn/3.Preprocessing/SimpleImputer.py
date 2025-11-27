
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer

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