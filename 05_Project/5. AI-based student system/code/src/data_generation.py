from pydoc import text
import random
from datetime import datetime, timedelta
from string import Template

import pandas as pd

Categories = ["IT", "Fees", "Timetable", "Exams", "General"]

Categories_to_priority = {
    "IT": "Medium",
    "Fees": "High",
    "Timetable": "Low",
    "Exams": "High",
    "General": "Low",
}

Templates = {
    "IT": ["Can't access Moodle", "WiFi not working", "Password reset failed"],
    "Fees": ["Payment failed", "Need fee receipt", "Charged twice"],
    "Timetable": ["Timetable missing", "Schedule clash", "Wrong classroom shown"],
    "Exams": ["Exam deferral request", "Exam timetable incorrect", "Need exam reschedule"],
    "General": ["Need student services help", "How to contact support?", "General guidance needed"],
}

noise = ["please", "urgent", "asap", "thanks", "still not working"]

def random_timestamp(days_span: int=7) -> str:

    start = datetime.now() - timedelta(days=days_span)
    dt = start + timedelta(
        days=random.randint(0, days_span - 1),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    return dt.isoformat(timespec="seconds")

def generate_Datasets(n: int=300, seed: int=42) -> pd.DataFrame:
    if not (200 <= n <= 500):
        raise ValueError("n must be between 200 and 500")
    random.seed(seed)
    rows = []

    for i in range(1, n + 1):
        cat = random.choice(Categories)
        text = random.choice(Templates[cat])

        if random.random() < 0.6:
            text = f"{text}.{random.choice(noise)}"

        rows.append(
            {
                "ticket_id": i,
                "timestamp":random_timestamp(),
                "text": text,
                "category": cat,
                "priority": Categories_to_priority[cat],
            }
        )
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = generate_Datasets(n=300, seed=42)
    df.to_csv("data/tickets.csv", index=False)

    print("saved to data/tickets.csv")
    print(df.shape)
    print(df.head())