from supabase import create_client
import streamlit as st

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_data(nama_file, teks, kategori):
    data = {
        "nama_file": nama_file,
        "teks": teks,
        "kategori": kategori
    }
    supabase.table("hasil").insert(data).execute()

def get_data():
    response = supabase.table("hasil").select("*").execute()
    return response.data
