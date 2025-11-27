from re import X
from sklearn.linear_model import LinearRegression
from sklearn.datasets import fetch_california_housing
from sklearn.discriminant_analysis import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

#1.  load california housing dataset
california = fetch_california_housing()

print(california.data, california.data.shape)
print(california.target)
print(california.feature_names)

#2.  data preprocessing------ split data into training and testing sets, 
X_train, X_test, y_train, y_test = train_test_split(california.data, california.target, test_size=0.2, random_state=42)
# data standardization
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_Scaled = scaler.transform(X_test)

# 3. create and practise Linear Regression
lr_model = LinearRegression()
lr_model.fit(X_train_scaled, y_train)
print('Coefficients:', lr_model.coef_)
print('Intercept:', lr_model.intercept_)
# 4. predict and evaluate model
y_pred = lr_model.predict(X_test_Scaled)
print('True Values:', y_test)
print('Predicted Values:', y_pred)
mse = mean_squared_error(y_test, y_pred)
print('Mean Squared Error:', mse)