from sklearn.datasets import load_iris
from sklearn.feature_selection import SelectKBest, f_classif


X, y = load_iris(return_X_y=True)

selector = SelectKBest(score_func=f_classif, k=2)
X_new = selector.fit_transform(X, y)

print(X.shape[1])
print(X_new.shape[1])
print(selector.scores_)