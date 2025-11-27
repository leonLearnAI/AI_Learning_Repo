
from sklearn.datasets import fetch_california_housing
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split

california_housing = fetch_california_housing()

X_train, X_test, y_train, y_test = train_test_split(california_housing.data, california_housing.target, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

ri_model = Ridge()
ri_model.fit(X_train_scaled, y_train)

y_pred = ri_model.predict(X_test_scaled)
print('True Values:', y_test[:20])
print('Predicted Values:', y_pred[:20])
mse = mean_squared_error(y_test, y_pred)
print('Mean Squared Error:', mse)