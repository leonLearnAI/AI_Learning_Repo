import time

worker_list = {
    "王力鸿" : {
        "部门":"科技部",
        "工资":3000,
        "级别":1
    },"周杰轮" : {
        "部门":"市场部",
        "工资":5000,
        "级别":2
    },"林俊节" : {
        "部门":"市场部",
        "工资":7000,
        "级别":3
    },"张学油" : {
        "部门":"科技部",
        "工资":4000,
        "级别":1
    },"刘德滑" : {
        "部门":"市场部",
        "工资":6000,
        "级别":2
    }
}
print(f"调级之前：{worker_list}")
for k in worker_list:
    info_list = worker_list[k]
    if int(info_list["级别"]) == 1:
        worker_list[k]["工资"] += 1000
        worker_list[k]["级别"] += 1
print(f"调级之后：{worker_list}")
