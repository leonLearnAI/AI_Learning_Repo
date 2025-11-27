
from sklearn.metrics import accuracy_score
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV, train_test_split
import joblib

  
iris_loaded = load_iris()
X = iris_loaded.data
y = iris_loaded.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

best_model =joblib.load('best_model.pkl')

y_pred = best_model.predict(X_test)

print(y_test)
print(y_pred)

acc = accuracy_score(y_test, y_pred)
print(acc)
print(classification_report(y_test, y_pred))
