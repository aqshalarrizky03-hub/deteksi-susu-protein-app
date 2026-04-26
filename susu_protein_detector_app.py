import streamlit as st
import tempfile
from classifier import process_image
from database import save_data, get_data
import cv2
import matplotlib.pyplot as plt

st.title("Klasifikasi Susu Protein (OCR + Rule-Based)")

uploaded_file = st.file_uploader("Upload Gambar", type=["jpg","png","jpeg"])

if uploaded_file:
    # simpan sementara
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    # tampilkan gambar
    st.image(uploaded_file, caption="Gambar Input", use_column_width=True)

    # proses
    text, kategori, score, gray, thresh = process_image(tfile.name)

    # simpan ke DB
    save_data(uploaded_file.name, text, kategori)

    # hasil
    st.subheader("Hasil OCR")
    st.text(text)

    st.subheader("Kategori")
    st.success(kategori)

    st.subheader("Score")
    st.write(score)

    # tampilkan preprocessing
    st.subheader("Preprocessing")
    col1, col2 = st.columns(2)

    with col1:
        st.image(gray, caption="Grayscale")

    with col2:
        st.image(thresh, caption="Threshold")

# =====================
# RIWAYAT DATA
# =====================
st.subheader("Riwayat Klasifikasi")

data = get_data()

for row in data:
    st.write(f"File: {row[1]}")
    st.write(f"Kategori: {row[3]}")
    st.write(f"Waktu: {row[4]}")
    st.write("---")