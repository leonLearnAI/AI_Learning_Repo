str = "hello, world, come on, it's me"
# str1 = str[5:10]
# print(str1)
# str2 = str1[::-1]
# print(str2)

str_list = str.split(",")
str1 = str_list[1]
print(str1)
str2 = str1.replace("come","")
print(str2)
str3 = str2[::-1]
print(str3)