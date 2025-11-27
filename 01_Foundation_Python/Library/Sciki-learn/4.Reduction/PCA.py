from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


iris = load_iris()
X, y = iris.data, iris.target

scaler = StandardScaler()
x_scaler = scaler.fit_transform(X)

print(x_scaler)
pca = PCA(n_components=2)

X_pca = pca.fit_transform(x_scaler)

print(X.shape)
print(X_pca.shape)