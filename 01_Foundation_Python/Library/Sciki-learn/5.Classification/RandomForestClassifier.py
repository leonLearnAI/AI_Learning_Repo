
from sklearn.metrics import accuracy_score
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV, train_test_split

  
iris_loaded = load_iris()
X = iris_loaded.data
y = iris_loaded.target

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

param_grid = {
    'n_estimators': [100, 200, 300],
   'max_depth': [5, 10, 20, None],
   'min_samples_split': [2, 5, 10],
   'max_features': ['sqrt', 'log2']
}

grid_search = GridSearchCV(
    estimator=RandomForestClassifier(random_state=42),
    param_grid=param_grid,
    cv=5,
    n_jobs=-1,
    scoring='accuracy'
)

# rft = RandomForestClassifier(
#     n_estimators=100,
#     max_depth=5,
#     random_state=42,
#     oob_score=True
# )

grid_search.fit(X_train, y_train)

print(grid_search.best_params_)
print(grid_search.best_score_)
# rft.fit(X_train, y_train)

best_model = grid_search.best_estimator_

y_pred = best_model.predict(X_test)

print(y_test)
print(y_pred)

acc = accuracy_score(y_test, y_pred)
print(acc)
print(classification_report(y_test, y_pred))