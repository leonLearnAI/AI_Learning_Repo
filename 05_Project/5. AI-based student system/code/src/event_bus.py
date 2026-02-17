from queue import Queue, Empty

class EventBus:
    def __init__(self):
        self.q = Queue()
    
    def publish(self, event: dict):
        self.q.put(event)

    def consume(self, timeout: float=0.1):
        try:
            event = self.q.get(timeout=timeout)
            return event
        except Empty:
            return None
if __name__ == "__main__":
    bus = EventBus()
    bus.publish({"event": "ticket_created", "Category": "IT", "priority": "Medium", "confidence": 0.85})
    print(bus.consume())