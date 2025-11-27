import random
# if I distribute the salary like this, i think i will been killed by the college. hahahh
# total = 10000
# i = 1
# while total > 0:
#     work_num = random.randint(1,11)
#     if work_num >= 5:
#         print(f"the {i}th employee, performance is greater than 5, give 1000 yuan salary, balance is {total - 1000}")
#         total -= 1000
#         if total == 0 or i == 20:
#             print("salary distribution is completed")
#             break
#     else:
#         print(f"the {i}th employee performance is not good, no salary")
#     i = i + 1

money = 10000
for i in range(1,21):
    score = random.randint(1,10)
    if score < 5:
        print(f"the employee {i} performance is {score}, not good, no salary, next one")
        continue
    if money >= 1000:
        money -= 1000
        print(f"employee {i} performance is {score}, good, give 1000 yuan salary, current balance is {money}")
    else:
        print("balance is not enough, please come next month")
        break