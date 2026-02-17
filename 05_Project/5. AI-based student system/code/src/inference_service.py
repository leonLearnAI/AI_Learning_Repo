import pickle
from random import sample
from unicodedata import category

Category_to_Priority = {
    "IT": "Medium",
    "Fees": "High",
    "Timetable": "Low",
    "Exams": "High",
    "General": "Low",
}

model_path = "models/model.pkl"
vec_path = "models/vec.pkl"

class InferenceService:
    def __init__(self, model_path=model_path, vec_path=vec_path):
        self.model = pickle.load(open(model_path, "rb"))
        self.vec = pickle.load(open(vec_path, "rb"))

    def predict(self, text:str):
        x = self.vec.transform([text])
        proba = self.model.predict_proba(x)[0]
        idx = proba.argmax()
        category = self.model.classes_[idx]
        confidence = float(proba[idx])
        priority = Category_to_Priority.get(category, "Low")
        return category, priority, confidence
if __name__ == "__main__":
    service = InferenceService()
    sample_text = "Can't access Moodle"
    print(service.predict(sample_text))