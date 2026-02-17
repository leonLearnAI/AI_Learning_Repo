from ast import mod
import pickle
from pyexpat import model
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

df = pd.read_csv("data/tickets.csv")
X_train, X_test, y_train, y_test = train_test_split(df["text"], df["category"], test_size=0.2, random_state=42)

vec = TfidfVectorizer()
X_train_vec = vec.fit_transform(X_train)
X_test_vec = vec.transform(X_test)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

pred = model.predict(X_test_vec)
print("accuracy:", accuracy_score(y_test, pred))

pickle.dump(model, open("models/model.pkl", "wb"))
pickle.dump(vec, open("models/vec.pkl", "wb"))
print("models saved")

