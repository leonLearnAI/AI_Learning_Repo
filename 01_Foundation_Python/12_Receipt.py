with open("test_file.txt", "r", encoding = "UTF-8") as f:
    bill_list = f.readlines()
    print(bill_list)
with open("bill_file.txt", "w", encoding = "UTF-8") as new_file:
    for bill in bill_list:
        bill_str = bill.strip()
        bill_filed = bill_str.split(",")
        print(f"the new bill is：{bill_filed}, the type of the bill is {type(bill_filed)}")
        if bill_filed[0] == "name" or "formal" in bill_filed[-1]:
           new_file.write(",".join(bill_filed) + "\n")

