
from operator import mul
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import fetch_20newsgroups
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report

# 1. load data
news = fetch_20newsgroups(subset='all')

# 2. preproccessing data
x_train, x_test, y_train, y_test = train_test_split(news.data, news.target, test_size=0.2, random_state=42)

# 3. create and practise MultinomialNB
tfidf = TfidfVectorizer()

# 4. predict and evaluate model
x_train_Scaled = tfidf.fit_transform(x_train)
x_test_scaled = tfidf.transform(x_test)

multi_nb = MultinomialNB()
multi_nb.fit(x_train_Scaled, y_train)

y_pred = multi_nb.predict(x_test_scaled)
print(classification_report(y_test, y_pred))

acc = accuracy_score(y_test, y_pred)
print(acc)
print(classification_report(y_test, y_pred, target_names=news.target_names))