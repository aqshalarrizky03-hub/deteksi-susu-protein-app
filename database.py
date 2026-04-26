import sqlite3

conn = sqlite3.connect("protein.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS hasil (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_file TEXT,
    teks TEXT,
    kategori TEXT,
    waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

def save_data(nama_file, teks, kategori):
    cursor.execute(
        "INSERT INTO hasil (nama_file, teks, kategori) VALUES (?, ?, ?)",
        (nama_file, teks, kategori)
    )
    conn.commit()

def get_data():
    cursor.execute("SELECT * FROM hasil ORDER BY waktu DESC")
    return cursor.fetchall()
