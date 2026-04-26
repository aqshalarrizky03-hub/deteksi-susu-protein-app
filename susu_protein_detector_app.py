import streamlit as st
from classifier import process_image
from database import save_data, get_data
from PIL import Image

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ProteinScan - Klasifikasi Susu Protein",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #1a1a2e;
}

.stApp {
    background: #f5f7ff;
    min-height: 100vh;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 2.5rem 3rem 2.5rem;
    max-width: 1200px;
}

/* ── Top Header Banner ── */
.top-header {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 50%, #1e40af 100%);
    margin: 0 -2.5rem 2.5rem -2.5rem;
    padding: 2.5rem 2.5rem 2rem 2.5rem;
    position: relative;
    overflow: hidden;
}
.top-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 260px; height: 260px;
    border-radius: 50%;
    background: rgba(255,255,255,0.07);
}
.top-header::after {
    content: '';
    position: absolute;
    bottom: -80px; left: 30%;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: rgba(255,255,255,0.05);
}
.header-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #93c5fd;
    margin-bottom: 0.5rem;
}
.header-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.1;
    margin: 0 0 0.5rem 0;
}
.header-subtitle {
    font-size: 0.95rem;
    color: #bfdbfe;
    font-weight: 300;
    margin: 0;
}
.header-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 999px;
    padding: 0.3rem 0.9rem;
    font-size: 0.78rem;
    color: #e0f2fe;
    margin-top: 1rem;
    font-weight: 500;
    letter-spacing: 0.04em;
}

/* ── Section Labels ── */
.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #1e3a8a;
    margin: 0 0 0.75rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 2px;
    background: linear-gradient(to right, #bfdbfe, transparent);
    border-radius: 2px;
}

/* ── Upload Card ── */
.upload-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 2rem;
    border: 2px dashed #bfdbfe;
    box-shadow: 0 1px 12px rgba(37,99,235,0.06);
    margin-bottom: 1.5rem;
    transition: border-color 0.2s;
}
.upload-card:hover { border-color: #2563eb; }

/* ── Result Cards ── */
.result-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin: 1rem 0 1.5rem 0;
}
.result-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 2px 16px rgba(37,99,235,0.07);
    border-top: 4px solid #2563eb;
}
.result-card.green { border-top-color: #16a34a; }
.result-card.amber { border-top-color: #d97706; }

.result-card-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 0.4rem;
}
.result-card-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #1a1a2e;
    word-break: break-word;
}
.result-card-value.big {
    font-size: 2rem;
}

/* ── OCR Text Box ── */
.ocr-box {
    background: #f8faff;
    border: 1px solid #dbeafe;
    border-left: 4px solid #2563eb;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    font-family: 'DM Mono', 'Courier New', monospace;
    font-size: 0.85rem;
    color: #374151;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
    margin-bottom: 1.5rem;
}

/* ── Preprocessing Cards ── */
.prep-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1rem 1rem 0.5rem 1rem;
    box-shadow: 0 2px 12px rgba(37,99,235,0.06);
    margin-bottom: 1rem;
}
.prep-card-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6b7280;
    margin-bottom: 0.6rem;
}

/* ── History Cards ── */
.history-header {
    background: linear-gradient(90deg, #eff6ff, #dbeafe);
    border-radius: 14px;
    padding: 1rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    border: 1px solid #bfdbfe;
}
.history-count {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    color: #2563eb;
}
.history-count-label {
    font-size: 0.8rem;
    color: #6b7280;
    font-weight: 400;
}
.history-row {
    background: #ffffff;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-bottom: 0.65rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 1px 8px rgba(37,99,235,0.05);
    border-left: 4px solid #2563eb;
    transition: transform 0.15s, box-shadow 0.15s;
}
.history-row:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(37,99,235,0.1);
}
.history-filename {
    font-weight: 600;
    font-size: 0.9rem;
    color: #1e3a8a;
}
.history-kategori {
    font-size: 0.8rem;
    background: #dbeafe;
    color: #1d4ed8;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-weight: 600;
}
.history-waktu {
    font-size: 0.78rem;
    color: #9ca3af;
}

/* ── Divider ── */
.custom-divider {
    height: 2px;
    background: linear-gradient(to right, #2563eb22, #2563eb55, #2563eb22);
    border: none;
    border-radius: 2px;
    margin: 2rem 0;
}

/* ── Streamlit widget overrides ── */
.stFileUploader > div > div {
    background: transparent !important;
    border: none !important;
}
.stFileUploader label {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    color: #1e3a8a !important;
}
[data-testid="stFileUploadDropzone"] {
    background: #eff6ff !important;
    border: 2px dashed #93c5fd !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    background: #dbeafe !important;
    border-color: #2563eb !important;
}
.stImage img {
    border-radius: 12px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="top-header">
    <div class="header-eyebrow">Computer Vision  &nbsp;|&nbsp;  OCR  &nbsp;|&nbsp;  Rule-Based AI</div>
    <h1 class="header-title">ProteinScan</h1>
    <p class="header-subtitle">Klasifikasi Kandungan Protein Susu secara Otomatis berbasis OCR dan Aturan</p>
    <span class="header-badge">Analisis Gambar Kemasan</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  UPLOAD SECTION
# ─────────────────────────────────────────────

with st.container():
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Pilih file gambar kemasan produk susu protein",
        type=["jpg", "png", "jpeg"],
        label_visibility="visible",
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PROCESSING
# ─────────────────────────────────────────────
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")

    # Process
    text, kategori, score, gray, thresh = process_image(image)

    # Save to DB
    save_data(uploaded_file.name, text, kategori, image, score)

    # ── Layout: Image | Results ──
    col_img, col_res = st.columns([1, 1.6], gap="large")

    with col_img:
        st.markdown('<p class="section-label">Gambar Input</p>', unsafe_allow_html=True)
        st.image(image, caption=uploaded_file.name, use_column_width=True)

    with col_res:
        st.markdown('<p class="section-label">Hasil Analisis</p>', unsafe_allow_html=True)

        score_color = "green" if score >= 70 else "amber" if score >= 40 else ""
        st.markdown(f"""
        <div class="result-grid">
            <div class="result-card green">
                <div class="result-card-label">Kategori</div>
                <div class="result-card-value">{kategori}</div>
            </div>
            <div class="result-card {score_color}">
                <div class="result-card-label">Confidence Score</div>
                <div class="result-card-value big">{score}</div>
            </div>
            <div class="result-card">
                <div class="result-card-label">File</div>
                <div class="result-card-value" style="font-size:0.85rem;font-family:'DM Sans',sans-serif;font-weight:500;">{uploaded_file.name}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="section-label">Teks OCR Terdeteksi</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="ocr-box">{text if text.strip() else "(Tidak ada teks yang terdeteksi)"}</div>', unsafe_allow_html=True)

    # ── Preprocessing ──
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    st.markdown('<p class="section-label">Tahapan Preprocessing Gambar</p>', unsafe_allow_html=True)

    col_g, col_t = st.columns(2, gap="medium")
    with col_g:
        st.markdown('<div class="prep-card"><div class="prep-card-label">Grayscale</div>', unsafe_allow_html=True)
        st.image(gray, channels="GRAY", use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with col_t:
        st.markdown('<div class="prep-card"><div class="prep-card-label">Threshold (Binarisasi)</div>', unsafe_allow_html=True)
        st.image(thresh, channels="GRAY", use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HISTORY SECTION
# ─────────────────────────────────────────────
st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
st.markdown('<p class="section-label">Riwayat Klasifikasi</p>', unsafe_allow_html=True)

data = get_data()

st.markdown(f"""
<div class="history-header">
    <div>
        <div class="history-count">{len(data)}</div>
        <div class="history-count-label">Total data tersimpan</div>
    </div>
    <div style="font-size:0.82rem;color:#6b7280;">Urutan terbaru di bawah</div>
</div>
""", unsafe_allow_html=True)

if data:
    for row in data:
        st.markdown(f"""
        <div class="history-row">
            <div>
                <div class="history-filename">{row['nama_file']}</div>
                <div class="history-waktu">{row['waktu']}</div>
            </div>
            <span class="history-kategori">{row['kategori']}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div style="text-align:center;padding:2.5rem;color:#9ca3af;font-size:0.9rem;background:#fff;border-radius:14px;border:1px dashed #e5e7eb;">
        Belum ada riwayat klasifikasi tersimpan.
    </div>
    """, unsafe_allow_html=True)
