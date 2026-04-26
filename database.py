from supabase import create_client
import streamlit as st
import base64
import io

# ambil dari secrets streamlit
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

# =========================
# SAVE DATA
# =========================
def save_data(nama_file, teks_ocr, kategori, image=None, score=0):
    img_b64 = None

    if image:
        buf = io.BytesIO()
        image.save(buf, format="JPEG")
        img_b64 = base64.b64encode(buf.getvalue()).decode()

    data = {
        "nama_file": nama_file,
        "teks_ocr": teks_ocr,
        "kategori": kategori,
        "score": score,
        "image": img_b64
    }

    supabase.table("hasil").insert(data).execute()


# =========================
# GET DATA
# =========================
def get_data():
    res = supabase.table("hasil").select("*").order("id").execute()
    data = res.data

    # convert base64 → PIL (biar bisa ditampilkan)
    from PIL import Image
    import io
    import base64

    for row in data:
        if row.get("image"):
            try:
                img_bytes = base64.b64decode(row["image"])
                row["image"] = Image.open(io.BytesIO(img_bytes))
            except:
                row["image"] = None

    return data


# =========================
# DELETE DATA
# =========================
def delete_data(row_id):
    supabase.table("hasil").delete().eq("id", row_id).execute()
