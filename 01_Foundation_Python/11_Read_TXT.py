with open("test_file.txt","r", encoding="UTF-8") as f:
    lines = f.read()
    print(lines)
    str_l = lines.split("\n")
    print(str_l)
    str_list = [word for item in str_l for word in item.split(" ")]
    print(str_list)
    count = 0
    for item in str_list:
        if item == "itheima":
            count += 1
    print(f"in total there are {count} itheima")