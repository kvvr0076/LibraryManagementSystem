import sqlite3

conn = sqlite3.connect('library.db')
cursor = conn.cursor()

# Insert admin user
cursor.execute('''
INSERT INTO users (username, password, role) 
VALUES ('admin', 'admin123', 'admin')
''')

conn.commit()
conn.close()

print("Admin user created!")
