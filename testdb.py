import sqlite3
conn = sqlite3.connect('database_chat.db',check_same_thread=False)
cursor = conn.execute("SELECT * FROM user WHERE USERNAME = 'to' AND PASSWORD = 'to' ")
print(cursor.fetchone())


conn.close()