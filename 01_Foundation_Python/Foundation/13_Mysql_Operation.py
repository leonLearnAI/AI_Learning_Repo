from pymysql import connect

con = connect(
    host="localhost",
    port=3306,
    user="root",
    passwd="888777",
    autocommit=True
)
cursor = con.cursor()
con.select_db("sys")
cursor.execute("select * from student")
result = cursor.fetchall()
for x in result:
    print(f"{x}")
cursor. execute(
    "insert into student values (66,'lilei', 6, 'male')"
)
con.close()
