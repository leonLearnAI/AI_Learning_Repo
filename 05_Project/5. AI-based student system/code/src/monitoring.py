from textwrap import indent
import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix

import event_bus

Priority_Order = {"Low": 0, "Medium": 1, "High": 2}

def compute_metrics(y_true, y_pred):

    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="macro", zero_division=0)

    return {"accuracy": float(acc), 
            "precision_macro": float(precision), 
            "recall_macro": float(recall), 
            "f1_macro": float(f1)
    }

def daily_high_priority_count(events_df: pd.DataFrame) -> pd.DataFrame:
    df = events_df.copy()
    df["day"] = pd.to_datetime(df["timestamp"]).dt.date.astype(str)
    return (
        df[df["priority"] == "High"]
        .groupby("day")
        .size()
        .reset_index(name="high_priority_count")
    )

def drift_check_confidence(events_df: pd.DataFrame) -> pd.DataFrame:
    df =events_df.copy()
    df["day"] = pd.to_datetime(df["timestamp"]).dt.date.astype(str)
    return (
        df.groupby("day")["confidence"]
        .mean()
        .reset_index(name="mean_confidence")
        .sort_values("day")
    )

def run_monitoring(events_df: pd.DataFrame, y_ture, y_pred, labels):
    metrics = compute_metrics(y_ture, y_pred)
    cm = confusion_matrix(y_ture, y_pred, labels=labels)

    high_daily = daily_high_priority_count(events_df)
    drift = drift_check_confidence(events_df)

    return metrics, cm, high_daily, drift

if __name__ == "__main__":
    from inference_service import InferenceService
    import os, json

    df = pd.read_csv("data/tickets.csv")
    svc = InferenceService()

    events = []
    y_true = df["category"].tolist()
    y_pred = []

    for _, row in df.iterrows():
        cate_pred, priority, conf = svc.predict(str(row["text"]))
        y_pred.append(cate_pred)
        events.append({"event": "ticket_created", 
                       "Category": cate_pred, 
                       "priority": priority, 
                       "confidence": conf, 
                       "timestamp": row["timestamp"]
        })

    events_df = pd.DataFrame(events)
    labels = sorted(df["category"].unique())

    metrics, cm, high_daily, drift = run_monitoring(events_df, y_true, y_pred, labels)

    print(metrics)
    print("\nConfusion Matrix (rows=true, cols=pred):")
    print(pd.DataFrame(cm, columns=labels, index=labels))

    print("\nDaily high priority count:")
    print(high_daily)

    print("\nDrift check (avg confidence per day):")
    print(drift)

    # output to file

    os.makedirs("outputs", exist_ok=True)
    json.dump(metrics, open("outputs/metrics.json", "w"), indent=2)
    pd.DataFrame(cm, columns=labels, index=labels).to_csv("outputs/confusion_matrix.csv", index=False)
    high_daily.to_csv("outputs/high_priority_Daily_count.csv", index=False)
    drift.to_csv("outputs/drift_confidence_Daily.csv", index=False)

    print("Done")