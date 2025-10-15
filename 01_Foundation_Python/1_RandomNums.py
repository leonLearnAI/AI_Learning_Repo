import random
random_num = random.randint(1,100)
count = 0
flag = True
while flag:
    num = int(input("Please have a try to guess the number"))
    count += 1
    if num == random_num:
        print(f"congratulations, you guessed the number in {count} times")
        flag = False
    elif num != random_num:
        if num > random_num:
            print("your guess is too big")
        else:
            print("your guess is too small")
print("guess the number in 10 times or less")