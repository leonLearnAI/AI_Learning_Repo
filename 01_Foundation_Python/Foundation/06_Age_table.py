
age_list = [21, 25, 21, 23, 22, 20]
#
age_list.append(31)
print(age_list)
age_list.extend([29, 33, 30])
print(age_list)
first_one = age_list[0]
print(first_one)
print(age_list)
last_one = age_list[-1]
print(last_one)
print(age_list)
people_index = age_list.index(31)
print(age_list)
print(people_index)

def list_for_age():
    for i in age_list:
        if i % 2 == 1:
            print(i)

def list_while_age():
    index = 0
    while index < len(age_list):
        if age_list[index] % 2 == 1:
            print(age_list[index])
        index += 1
print("------------------")
list_for_age()
print("------------------")
list_while_age()