import streamlit as st
from classifier import process_image
from database import save_data, get_data
from PIL import Image

st.title("Klasifikasi Susu Protein (OCR + Rule-Based)")

uploaded_file = st.file_uploader("Upload Gambar", type=["jpg","png","jpeg"])

if uploaded_file:
    # baca gambar
    image = Image.open(uploaded_file).convert("RGB")

    # tampilkan gambar
    st.image(image, caption="Gambar Input", use_column_width=True)

    # proses
    text, kategori, score, gray, thresh = process_image(image)

    # simpan ke DB
    save_data(uploaded_file.name, text, kategori)

    # hasil
    st.subheader("Hasil OCR")
    st.text(text)

    st.subheader("Kategori")
    st.success(kategori)

    st.subheader("Score")
    st.write(score)

    # preprocessing
    st.subheader("Preprocessing")
    col1, col2 = st.columns(2)

    with col1:
        st.image(gray, caption="Grayscale", channels="GRAY")

    with col2:
        st.image(thresh, caption="Threshold", channels="GRAY")

# =====================
# RIWAYAT
# =====================
st.subheader("Riwayat Klasifikasi")

data = get_data()

for row in data:
    st.write(f"File: {row[1]}")
    st.write(f"Kategori: {row[3]}")
    st.write(f"Waktu: {row[4]}")
    st.write("---")
