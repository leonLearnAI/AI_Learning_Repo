import time

worker_list = {
    "Lihong" : {
        "Department":"Technology",
        "Salary":3000,
        "Level":1
    },"Jay" : {
        "Department":"Marketing",
        "Salary":5000,
        "Level":2
    },"Jenny" : {
        "D":"Marketing",
        "Salary":7000,
        "Level":3
    },"Xueyou" : {
        "Department":"Technology",
        "Salary":4000,
        "Level":1
    },"Dehua" : {
        "Department":"Marketing",
        "Salary":6000,
        "Level":2
    }
}
print(f"Before promotion: {worker_list}")
for k in worker_list:
    info_list = worker_list[k]
    if int(info_list["Level"]) == 1:
        worker_list[k]["Salary"] += 1000
        worker_list[k]["Level"] += 1
print(f"After promotion: {worker_list}")
