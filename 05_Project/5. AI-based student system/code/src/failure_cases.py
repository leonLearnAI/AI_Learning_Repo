from inference_service import InferenceService

svc = InferenceService()

tests = [
    ("I can’t access Moodle and my fee payment failed at the same time.", "Fees"),
    ("My exam timetable is missing in Moodle.", "Exams"),
    ("Payment receipt needed, also my timetable shows wrong room.", "Fees"),
    ("Exam deferral requested because I cannot log into my student portal.", "Exams"),
    ("WiFi is down but I also need a fee invoice urgently.", "Fees"),
    ("Timetable clash and Moodle shows error when submitting assignments.", "Timetable"),
]

for text, expected in tests:
    pred_cat, pred_prio, conf = svc.predict(text)
    print("\nTEXT:", text)
    print("EXPECTED:", expected)
    print("PRED:", pred_cat, pred_prio, conf)