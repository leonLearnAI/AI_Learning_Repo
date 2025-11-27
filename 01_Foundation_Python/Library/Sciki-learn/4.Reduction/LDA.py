from sklearn.datasets import load_iris
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.preprocessing import StandardScaler


iris = load_iris()
X, y = iris.data, iris.target

scaler = StandardScaler()
x_scaler = scaler.fit_transform(X)

print(x_scaler)
lda = LinearDiscriminantAnalysis(n_components=2)

X_lda = lda.fit_transform(x_scaler, y)

print(X.shape)
print(X_lda.shape)