from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report

# 1. load data
iris = load_iris()
X = iris.data
y = iris.target

# 2. preproccessing data
train_X, test_X, train_y, test_y = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(train_X)
X_test_scaled =scaler.transform(test_X)

# 3. create and practise KNN
knn =KNeighborsClassifier(n_neighbors=9)
knn.fit(X_train_scaled, train_y)

# 4. predict and evaluate model
y_pred = knn.predict(X_test_scaled)

print(test_y)
print(y_pred)
# 5. evaluate model
score = accuracy_score(test_y, y_pred)
print(score)
print(classification_report(test_y, y_pred, target_names=iris.target_names))