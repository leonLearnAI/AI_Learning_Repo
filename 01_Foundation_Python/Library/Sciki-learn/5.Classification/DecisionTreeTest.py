
from sklearn.metrics import accuracy_score
from sklearn.datasets import load_iris
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor


iris_loaded = load_iris()
X = iris_loaded.data
y = iris_loaded.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

dct = DecisionTreeRegressor()

dct.fit(X_train, y_train)

y_pred = dct.predict(X_test)

print(y_test)
print(y_pred)

acc = accuracy_score(y_test, y_pred)
print(acc)
print(classification_report(y_test, y_pred, target_names=iris_loaded.target_names))