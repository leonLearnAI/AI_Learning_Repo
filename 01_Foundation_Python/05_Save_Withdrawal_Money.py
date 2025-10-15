
money = 5000
name = None

name = input("pleas input your name:")
def save_money(m):
    global money
    money += m
    print("----------Deposit----------")
    print(f"Dear {name}, you have deposited {m}, your current balance is {money} yuan")

def get_money(m):
    global money
    money -= m
    print("----------Withdrawal----------")
    print(f"Dear {name}, you have withdrawn {m}, your current balance is {money} yuan")

def query():
    print("----------Query-----------")
    print(f"Dear {name}, your current balance is {money} yuan")

def main():
    print("----------Main Menu----------")
    print(f"{name} Welcome to ATM, please select your operation:")
    print("Query Balance\t[1]")
    print("Deposit\t\t[2]")
    print("Withdrawal\t[3]")
    print("Exit\t\t[4]")


flag = True
while flag:
    main()
    operation_num = int(input("Please enter your operation:"))
    if operation_num == 1:
        query()
        continue
    if operation_num == 2:
        save_money(500)
        continue
    if operation_num == 3:
        get_money(100)
        continue
    if operation_num == 4:
        flag = False
        break