import pandas as pd

from inference_service import InferenceService
from event_bus import EventBus
from monitoring import drift_check_confidence, daily_high_priority_count

def main():
    svc = InferenceService()
    bus = EventBus()
    
    # 1. create some sample events
    texts = [
        "Can't access Moodle",
        "Payment failed",
        "Timetable missing",
        "Exam deferral request",
        "Need student services help",
    ]
    
    # 2. publish events to the event bus
    for t in texts:
        category, priority, confidence = svc.predict(t)
        event = {
            "event": "Ticket_classification",
            "category": category,
            "priority": priority,
            "confidence": confidence,
            "timestamp": pd.Timestamp.now().isoformat(timespec="seconds"),
            "text": t,
        }
        bus.publish(event)
    # 3. consume events
    events = []
    while True:
        e = bus.consume()
        if e is None:
            break
        events.append(e)
    
    events_df = pd.DataFrame(events)
    print("\nConsumed Events:\n", events_df[["event", "category", "priority", "confidence"]])

    # 4. monitoring output
    print("\nDaily high priority count:\n", daily_high_priority_count(events_df))
    print("\n Drift check (avg confidece by day)\n", drift_check_confidence(events_df))

if __name__ == "__main__":
    main()