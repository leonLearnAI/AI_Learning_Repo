from re import X
from sklearn.datasets import fetch_california_housing
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import test

# 1. load data
california = fetch_california_housing()
print(california.data.shape)
print(california.target)

# 2. data preprocessing
X_train, X_test, y_train, y_test = train_test_split(california.data, california.target, test_size=0.2, random_state=42)
# data standardization
scaler = StandardScaler()
X_train_sacler = scaler.fit_transform(X_train)
X_test_scaler = scaler.transform(X_test)

# 3. create and practise sdg regression

sdg_reg = SGDRegressor()
sdg_reg.fit(X_train_sacler, y_train)
print('Coefficients:', sdg_reg.coef_)
print('Intercept:', sdg_reg.intercept_)

# 4. predict and evaluate model
y_pred = sdg_reg.predict(X_test_scaler)
print('True Values:', y_test)
print('Predicted Values:', y_pred)
mse = mean_squared_error(y_test, y_pred)
print('MSE:', mse)