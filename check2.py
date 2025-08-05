import sqlite3

conn = sqlite3.connect("student_portal.db")
cursor = conn.cursor()

# Get list of indexes on the users table
cursor.execute("PRAGMA index_list('users')")
indexes = cursor.fetchall()

for index in indexes:
    print(index)

conn.close()
