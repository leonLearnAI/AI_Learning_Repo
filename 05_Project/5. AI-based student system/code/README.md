# EEAI Assignment — AI-based Student Support Ticket System

A minimal end-to-end NLP pipeline that classifies student support tickets into **five categories**  
(**IT / Fees / Timetable / Exams / General**), assigns **priority** (**Low / Medium / High**), publishes a
**TICKET_CLASSIFIED** event to a simple in-memory queue, and produces **monitoring outputs**
(metrics, confusion matrix, daily high-priority count, confidence drift).

---

## Features
- Synthetic ticket generation (**200–500** samples)
- Baseline text classifier: **TF-IDF + Logistic Regression**
- Inference outputs: **category + priority + confidence**
- Event queue simulation using `queue.Queue()`
- Monitoring outputs:
  - Accuracy / Precision / Recall / F1 (macro)
  - Confusion matrix
  - Daily high-priority count
  - Confidence trend (drift signal)

---

## Project Structure
```text
src/
  data_generation.py      # generate synthetic tickets -> data/tickets.csv
  train_model.py          # train baseline model -> models/*.pkl
  inference_service.py    # load artifacts -> predict category/priority/confidence
  event_bus.py            # queue.Queue publish/consume
  monitoring.py           # metrics + confusion matrix + drift + daily high-priority
  demo.py                 # end-to-end demo (inference -> event -> monitoring)

data/
  tickets.csv             # generated dataset (created at runtime)

models/
  model.pkl               # trained classifier (created at runtime)
  vectorizer.pkl          # trained TF-IDF vectorizer (created at runtime)

outputs/
  metrics.json
  confusion_matrix.csv
  high_priority_daily.csv
  drift_confidence_daily.csv