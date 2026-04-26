import mysql.connector

# koneksi ke MySQL XAMPP
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # default XAMPP kosong
    database="protein_db"
)

cursor = conn.cursor()

# =====================
# SIMPAN DATA
# =====================
def save_data(nama_file, teks, kategori):
    query = """
    INSERT INTO hasil_klasifikasi (nama_file, teks_ocr, kategori)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (nama_file, teks, kategori))
    conn.commit()

# =====================
# AMBIL DATA
# =====================
def get_data():
    cursor.execute("SELECT * FROM hasil_klasifikasi ORDER BY waktu DESC")
    return cursor.fetchall()