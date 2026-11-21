import sqlite3

# connect to db
conn = sqlite3.connect('student.db')

# create a cursor
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS students(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
phone TEXT
)""")
c.execute("""CREATE TABLE IF NOT EXISTS subjects(
id INTEGER PRIMARY KEY AUTOINCREMENT,
subject TEXT,
mark INTEGER,
FOREIGN KEY (id) REFERENCES students(id)
)""")

# c.execute("""
# INSERT INTO students VALUES(
# 'John', '+375298568458'
# )""")

# group = [
#     ('Kate', '+3758486840'),
#     ('May', '+37584685128'),
#     ('Ted', '+37584685218')
# ]
#
# subj = [
#     ('manth', 5),
#     ('teormeh', 10),
#     ('fizika', 9)
# ]
#
# c.executemany("INSERT INTO students('name', 'phone') VALUES (?, ?)", group)
# c.executemany("INSERT INTO subjects('subject', 'mark') VALUES (?, ?)", subj)

# c.execute("""
# CREATE TABLE IF NOT EXISTS customers (
# first_name TEXT,
# last_name TEXT,
# phone_numb TEXT
# )""")

# c.execute("INSERT INTO customers VALUES ('Ilon', 'MASK', '+375441254685')")
#
# a_few_customers = [
#     ('John', 'Green', '+375298456258'),
#     ('James', 'Smith', '+375259856487'),
#     ('Ann', 'Trumph', '+375448511235')
# ]
# c.executemany("INSERT INTO customers VALUES (?, ?, ?)", a_few_customers)

# query the db
# c.execute("SELECT rowid, * FROM customers")
# # print(c.fetchone()[1])
# # print(c.fetchmany(2))
# # print(c.fetchall())
#
# for e in c.fetchall():
#     # print(f'{e[0]} {e[1]} \t\t\t {e[2]}')
#     print(e)

# c.execute("""SELECT * FROM students""")
# item = c.fetchall()
#
# for i in item:
#     print(f"{i[0]} {i[1]}\t{i[2]}")

c.execute("""SELECT * FROM subjects IF """)
ite = c.fetchall()

for i in ite:
    print(f"{i[0]} {i[1]}\t{i[2]}")

print("Command executed successfully...")

# commit our commands
conn.commit()
# close our connection
conn.close()
