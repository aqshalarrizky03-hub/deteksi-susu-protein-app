import streamlit as st
from classifier import process_image
from database import save_data, get_data, delete_data
from PIL import Image
import io, base64, csv

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
#  HELPERS
# ─────────────────────────────────────────────
def pil_to_b64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return base64.b64encode(buf.getvalue()).decode()

def kategori_color(k: str) -> str:
    k = (k or "").lower()
    if "tinggi" in k: return "#16a34a"
    if "sedang" in k: return "#d97706"
    if "rendah" in k: return "#dc2626"
    return "#2563eb"

def kategori_bg(k: str) -> str:
    k = (k or "").lower()
    if "tinggi" in k: return "#dcfce7"
    if "sedang" in k: return "#fef3c7"
    if "rendah" in k: return "#fee2e2"
    return "#dbeafe"

def score_class(score) -> str:
    try:
        s = float(score)
        if s >= 70: return "green"
        if s >= 40: return "amber"
    except:
        pass
    return "red"

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color: #1a1a2e; }
.stApp { background: #f0f4ff; min-height: 100vh; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2.5rem 4rem 2.5rem; max-width: 1240px; }

/* TOP HEADER */
.top-header {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 55%, #3b82f6 100%);
    margin: 0 -2.5rem 2rem -2.5rem;
    padding: 2.5rem 2.5rem 2rem 2.5rem;
    position: relative; overflow: hidden;
}
.top-header::before {
    content: ''; position: absolute; top: -50px; right: -50px;
    width: 240px; height: 240px; border-radius: 50%;
    background: rgba(255,255,255,0.07);
}
.top-header::after {
    content: ''; position: absolute; bottom: -70px; left: 35%;
    width: 160px; height: 160px; border-radius: 50%;
    background: rgba(255,255,255,0.05);
}
.header-eyebrow { font-size:0.7rem; font-weight:600; letter-spacing:0.2em; text-transform:uppercase; color:#93c5fd; margin-bottom:0.45rem; }
.header-title { font-family:'Syne',sans-serif; font-size:2.3rem; font-weight:800; color:#fff; line-height:1.1; margin:0 0 0.45rem 0; }
.header-subtitle { font-size:0.93rem; color:#bfdbfe; font-weight:300; margin:0; }
.header-badges { display:flex; gap:0.5rem; flex-wrap:wrap; margin-top:1rem; }
.header-badge {
    display:inline-block; background:rgba(255,255,255,0.14); border:1px solid rgba(255,255,255,0.22);
    border-radius:999px; padding:0.28rem 0.85rem; font-size:0.75rem; color:#e0f2fe; font-weight:500; letter-spacing:0.04em;
}

/* SECTION LABEL */
.section-label {
    font-family:'Syne',sans-serif; font-size:1.05rem; font-weight:700; color:#1e3a8a;
    margin:0 0 0.75rem 0; display:flex; align-items:center; gap:0.5rem;
}
.section-label::after { content:''; flex:1; height:2px; background:linear-gradient(to right,#bfdbfe,transparent); border-radius:2px; }

/* UPLOAD CARD */
.upload-card {
    background:#fff; border-radius:16px; padding:2rem;
    border:2px dashed #bfdbfe; box-shadow:0 1px 12px rgba(37,99,235,0.06);
    margin-bottom:1.5rem; transition:border-color 0.2s;
}
.upload-card:hover { border-color:#2563eb; }

/* RESULT CARDS */
.result-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin:0.75rem 0 1.5rem 0; }
.result-card {
    background:#fff; border-radius:14px; padding:1.2rem 1.4rem;
    box-shadow:0 2px 16px rgba(37,99,235,0.07); border-top:4px solid #2563eb;
}
.result-card.green { border-top-color:#16a34a; }
.result-card.amber { border-top-color:#d97706; }
.result-card.red   { border-top-color:#dc2626; }
.result-card-label { font-size:0.7rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:#6b7280; margin-bottom:0.35rem; }
.result-card-value { font-family:'Syne',sans-serif; font-size:1.3rem; font-weight:700; color:#1a1a2e; word-break:break-word; }
.result-card-value.big { font-size:1.9rem; }

/* SCORE BAR */
.score-bar-wrap { margin-bottom:1.4rem; }
.score-bar-label { font-size:0.78rem; font-weight:600; color:#6b7280; margin-bottom:0.4rem; display:flex; justify-content:space-between; }
.score-bar-track { background:#e5e7eb; border-radius:999px; height:10px; overflow:hidden; }
.score-bar-fill  { height:10px; border-radius:999px; }

/* OCR BOX */
.ocr-box {
    background:#f8faff; border:1px solid #dbeafe; border-left:4px solid #2563eb;
    border-radius:10px; padding:1.2rem 1.5rem;
    font-family:'Courier New',monospace; font-size:0.83rem; color:#374151;
    line-height:1.75; white-space:pre-wrap; word-break:break-word;
    margin-bottom:1.4rem; max-height:200px; overflow-y:auto;
}

/* PREP CARD */
.prep-card { background:#fff; border-radius:14px; padding:1rem 1rem 0.6rem 1rem; box-shadow:0 2px 12px rgba(37,99,235,0.06); margin-bottom:1rem; }
.prep-card-label { font-size:0.72rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; color:#6b7280; margin-bottom:0.6rem; }

/* STAT CARDS */
.stat-row { display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:1.75rem; }
.stat-card {
    background:#fff; border-radius:14px; padding:1.1rem 1.4rem;
    box-shadow:0 2px 14px rgba(37,99,235,0.07); border-top:3px solid #2563eb;
}
.stat-label { font-size:0.7rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:#9ca3af; margin-bottom:0.3rem; }
.stat-value { font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:800; color:#1e3a8a; }
.stat-sub   { font-size:0.75rem; color:#6b7280; margin-top:0.1rem; }

/* HISTORY MINI STATS */
.history-stats-row { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin-bottom:1.25rem; }
.history-mini-card {
    background:#fff; border-radius:12px; padding:1rem 1.25rem;
    box-shadow:0 1px 8px rgba(37,99,235,0.06); text-align:center;
    border-bottom:3px solid #2563eb;
}
.hmc-val   { font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:800; color:#1e3a8a; }
.hmc-label { font-size:0.72rem; color:#9ca3af; font-weight:500; margin-top:0.15rem; }

/* HISTORY CARD GRID */
.hist-card {
    background:#fff; border-radius:14px; overflow:hidden;
    box-shadow:0 2px 14px rgba(37,99,235,0.07);
    transition:transform 0.16s, box-shadow 0.16s;
    border:1.5px solid transparent;
}
.hist-card:hover { transform:translateY(-3px); box-shadow:0 8px 24px rgba(37,99,235,0.13); border-color:#bfdbfe; }
.hist-card-thumb { width:100%; aspect-ratio:16/9; object-fit:cover; display:block; background:#e0e7ff; }
.hist-card-thumb-placeholder {
    width:100%; aspect-ratio:16/9; background:linear-gradient(135deg,#eff6ff,#dbeafe);
    display:flex; align-items:center; justify-content:center;
    font-size:0.85rem; color:#93c5fd; font-weight:500;
}
.hist-card-body { padding:0.9rem 1rem 1rem 1rem; }
.hist-card-title { font-weight:600; font-size:0.88rem; color:#1e3a8a; margin-bottom:0.35rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.hist-card-row { display:flex; justify-content:space-between; align-items:center; margin-top:0.5rem; }
.hist-card-badge { font-size:0.73rem; font-weight:700; padding:0.22rem 0.7rem; border-radius:999px; letter-spacing:0.03em; }
.hist-card-waktu { font-size:0.73rem; color:#9ca3af; }
.hist-card-ocr { font-size:0.78rem; color:#6b7280; margin-top:0.35rem; line-height:1.4; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; }

/* INFO BOX */
.info-box {
    background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px;
    padding:0.85rem 1.2rem; font-size:0.85rem; color:#1d4ed8;
    margin-bottom:1rem; display:flex; gap:0.6rem; align-items:flex-start;
}

/* COMPARE TABLE */
.compare-table { width:100%; border-collapse:collapse; font-size:0.85rem; margin-top:0.75rem; }
.compare-table th { background:#eff6ff; color:#1e3a8a; font-family:'Syne',sans-serif; font-weight:700; text-align:left; padding:0.7rem 1rem; font-size:0.8rem; letter-spacing:0.04em; border-bottom:2px solid #dbeafe; }
.compare-table td { padding:0.7rem 1rem; border-bottom:1px solid #f1f5f9; vertical-align:middle; color:#374151; }
.compare-table tr:last-child td { border-bottom:none; }
.compare-table tr:hover td { background:#f8faff; }

/* DIVIDER */
.custom-divider { height:2px; background:linear-gradient(to right,#2563eb22,#2563eb55,#2563eb22); border:none; border-radius:2px; margin:2rem 0; }

/* EMPTY STATE */
.empty-state { text-align:center; padding:3rem 1rem; background:#fff; border-radius:16px; border:1px dashed #dbeafe; color:#9ca3af; font-size:0.9rem; }

/* Streamlit overrides */
[data-testid="stFileUploadDropzone"] { background:#eff6ff !important; border:2px dashed #93c5fd !important; border-radius:12px !important; }
[data-testid="stFileUploadDropzone"]:hover { background:#dbeafe !important; border-color:#2563eb !important; }
.stImage img { border-radius:12px; width:100%; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
for key, default in {
    "active_tab":   "Analisis",
    "hist_filter":  "Semua",
    "hist_search":  "",
    "detail_row":   None,
    "last_result":  None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="top-header">
    <div class="header-eyebrow">Computer Vision &nbsp;|&nbsp; OCR &nbsp;|&nbsp; Rule-Based AI</div>
    <h1 class="header-title">ProteinScan</h1>
    <p class="header-subtitle">Klasifikasi Kandungan Protein Susu secara Otomatis berbasis OCR dan Aturan</p>
    <div class="header-badges">
        <span class="header-badge">Analisis Kemasan</span>
        <span class="header-badge">Riwayat Visual</span>
        <span class="header-badge">Perbandingan Produk</span>
        <span class="header-badge">Ekspor CSV</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  NAVIGATION
# ─────────────────────────────────────────────
TABS = ["Analisis", "Riwayat", "Perbandingan", "Statistik"]
tab_cols = st.columns(len(TABS))
for i, tab in enumerate(TABS):
    with tab_cols[i]:
        is_active = st.session_state.active_tab == tab
        btn_style = "primary" if is_active else "secondary"
        if st.button(tab, key=f"nav_{tab}", use_container_width=True, type=btn_style):
            st.session_state.active_tab = tab
            st.session_state.detail_row = None
            st.rerun()

st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)

data_all = get_data()

# ═════════════════════════════════════════════
#  TAB 1 — ANALISIS
# ═════════════════════════════════════════════
if st.session_state.active_tab == "Analisis":

    st.markdown('<p class="section-label">Unggah Gambar Kemasan</p>', unsafe_allow_html=True)
    st.markdown('<div class="upload-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Pilih file gambar kemasan produk susu protein",
        type=["jpg","png","jpeg"], label_visibility="visible",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        text, kategori, score, gray, thresh = process_image(image)
        # NOTE: save_data perlu menerima parameter image (PIL) agar gambar bisa ditampilkan di Riwayat.
        # Sesuaikan signature database.save_data(nama_file, teks_ocr, kategori, image=None)
        save_data(uploaded_file.name, text, kategori, image, score)

        st.session_state.last_result = {
            "nama_file": uploaded_file.name,
            "teks_ocr": text, "kategori": kategori, "score": score, "image": image,
        }

        col_img, col_res = st.columns([1, 1.6], gap="large")

        with col_img:
            st.markdown('<p class="section-label">Gambar Input</p>', unsafe_allow_html=True)
            st.image(image, caption=uploaded_file.name, use_column_width=True)

        with col_res:
            st.markdown('<p class="section-label">Hasil Analisis</p>', unsafe_allow_html=True)

            sc  = score_class(score)
            kc  = kategori_color(kategori)
            try:    pct = min(int(score), 100)
            except: pct = 0
            bar_col = "#16a34a" if pct >= 70 else "#d97706" if pct >= 40 else "#dc2626"

            st.markdown(f"""
            <div class="result-grid">
                <div class="result-card green">
                    <div class="result-card-label">Kategori</div>
                    <div class="result-card-value" style="color:{kc}">{kategori}</div>
                </div>
                <div class="result-card {sc}">
                    <div class="result-card-label">Confidence Score</div>
                    <div class="result-card-value big">{score}</div>
                </div>
                <div class="result-card">
                    <div class="result-card-label">Nama File</div>
                    <div class="result-card-value" style="font-size:0.82rem;font-family:'DM Sans',sans-serif;font-weight:500;">{uploaded_file.name}</div>
                </div>
            </div>
            <div class="score-bar-wrap">
                <div class="score-bar-label"><span>Confidence Score</span><span>{score} / 100</span></div>
                <div class="score-bar-track">
                    <div class="score-bar-fill" style="width:{pct}%;background:{bar_col};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<p class="section-label">Teks OCR Terdeteksi</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="ocr-box">{text.strip() or "(Tidak ada teks terdeteksi)"}</div>', unsafe_allow_html=True)

            if text.strip():
                st.download_button("Unduh Teks OCR (.txt)", data=text,
                    file_name=f"ocr_{uploaded_file.name}.txt", mime="text/plain", use_container_width=True)

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

    else:
        if data_all:
            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
            st.markdown('<p class="section-label">Scan Terbaru</p>', unsafe_allow_html=True)
            recent = list(reversed(data_all))[:3]
            cols = st.columns(len(recent), gap="medium")
            for i, row in enumerate(recent):
                with cols[i]:
                    kc = kategori_color(row.get("kategori",""))
                    kb = kategori_bg(row.get("kategori",""))
                    if row.get("image"):
                        try:
                            b64 = pil_to_b64(row["image"])
                            thumb = f'<img src="data:image/jpeg;base64,{b64}" class="hist-card-thumb">'
                        except:
                            thumb = '<div class="hist-card-thumb-placeholder">Tidak Ada Gambar</div>'
                    else:
                        thumb = '<div class="hist-card-thumb-placeholder">Tidak Ada Gambar</div>'
                    st.markdown(f"""
                    <div class="hist-card">
                        {thumb}
                        <div class="hist-card-body">
                            <div class="hist-card-title">{row.get('nama_file','')}</div>
                            <div class="hist-card-row">
                                <span class="hist-card-badge" style="background:{kb};color:{kc};">{row.get('kategori','')}</span>
                                <span class="hist-card-waktu">{str(row.get('waktu',''))[:16]}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)


# ═════════════════════════════════════════════
#  TAB 2 — RIWAYAT
# ═════════════════════════════════════════════
elif st.session_state.active_tab == "Riwayat":

    total  = len(data_all)
    tinggi = sum(1 for r in data_all if "tinggi" in (r.get("kategori","")).lower())
    sedang = sum(1 for r in data_all if "sedang" in (r.get("kategori","")).lower())

    st.markdown(f"""
    <div class="history-stats-row">
        <div class="history-mini-card">
            <div class="hmc-val">{total}</div>
            <div class="hmc-label">Total Scan</div>
        </div>
        <div class="history-mini-card" style="border-color:#16a34a">
            <div class="hmc-val" style="color:#16a34a">{tinggi}</div>
            <div class="hmc-label">Protein Tinggi</div>
        </div>
        <div class="history-mini-card" style="border-color:#d97706">
            <div class="hmc-val" style="color:#d97706">{sedang}</div>
            <div class="hmc-label">Protein Sedang</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Search & sort
    col_s, col_o = st.columns([2.5, 1], gap="medium")
    with col_s:
        search_q = st.text_input("", value=st.session_state.hist_search,
            placeholder="Cari nama file...", label_visibility="collapsed")
        st.session_state.hist_search = search_q
    with col_o:
        sort_order = st.selectbox("", ["Terbaru", "Terlama", "Nama A-Z"], label_visibility="collapsed")

    # Filter chips
    all_cats = ["Semua"] + sorted(set(r.get("kategori","") for r in data_all if r.get("kategori")))
    chip_cols = st.columns(len(all_cats))
    for i, cat in enumerate(all_cats):
        with chip_cols[i]:
            if st.button(cat, key=f"chip_{cat}", use_container_width=True,
                         type="primary" if st.session_state.hist_filter == cat else "secondary"):
                st.session_state.hist_filter = cat
                st.rerun()

    # Filter
    filtered = list(data_all)
    if st.session_state.hist_filter != "Semua":
        filtered = [r for r in filtered if r.get("kategori") == st.session_state.hist_filter]
    if search_q:
        filtered = [r for r in filtered if search_q.lower() in r.get("nama_file","").lower()]
    if sort_order == "Terbaru":   filtered = filtered[::-1]
    elif sort_order == "Terlama": pass
    elif sort_order == "Nama A-Z": filtered = sorted(filtered, key=lambda x: x.get("nama_file",""))

    # Export CSV
    if filtered:
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["nama_file","kategori","waktu","teks_ocr"])
        writer.writeheader()
        for r in filtered:
            writer.writerow({"nama_file":r.get("nama_file",""),"kategori":r.get("kategori",""),
                             "waktu":str(r.get("waktu","")),"teks_ocr":r.get("teks_ocr","")})
        st.download_button(f"Ekspor {len(filtered)} Data ke CSV", data=buf.getvalue(),
            file_name="riwayat_proteinscan.csv", mime="text/csv")

    st.markdown(f"<div style='font-size:0.82rem;color:#6b7280;margin:0.5rem 0 1rem 0;'>Menampilkan {len(filtered)} dari {total} data</div>", unsafe_allow_html=True)

    if not filtered:
        st.markdown('<div class="empty-state">Tidak ada data yang cocok dengan filter ini.</div>', unsafe_allow_html=True)
    else:
        PER_ROW = 3
        for row_start in range(0, len(filtered), PER_ROW):
            items = filtered[row_start:row_start+PER_ROW]
            cols  = st.columns(PER_ROW, gap="medium")
            for ci, row in enumerate(items):
                with cols[ci]:
                    kc = kategori_color(row.get("kategori",""))
                    kb = kategori_bg(row.get("kategori",""))
                    if row.get("image"):
                        try:
                            b64 = pil_to_b64(row["image"])
                            thumb = f'<img src="data:image/jpeg;base64,{b64}" class="hist-card-thumb">'
                        except:
                            thumb = '<div class="hist-card-thumb-placeholder">Tidak Ada Gambar</div>'
                    else:
                        thumb = '<div class="hist-card-thumb-placeholder">Tidak Ada Gambar</div>'

                    ocr_prev = (row.get("teks_ocr","") or "")[:120]
                    st.markdown(f"""
                    <div class="hist-card">
                        {thumb}
                        <div class="hist-card-body">
                            <div class="hist-card-title">{row.get('nama_file','')}</div>
                            <div class="hist-card-ocr">{ocr_prev or '(tidak ada teks)'}</div>
                            <div class="hist-card-row">
                                <span class="hist-card-badge" style="background:{kb};color:{kc};">{row.get('kategori','')}</span>
                                <span class="hist-card-waktu">{str(row.get('waktu',''))[:16]}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    b1, b2 = st.columns(2)
                    with b1:
                        if st.button("Detail", key=f"det_{row_start}_{ci}", use_container_width=True):
                            st.session_state.detail_row = row
                            st.rerun()
                    with b2:
                        if st.button("Hapus", key=f"del_{row_start}_{ci}", use_container_width=True):
                            delete_data(row.get("id"))
                            st.success("Data berhasil dihapus.")
                            st.rerun()

    # ── Detail panel ──
    if st.session_state.detail_row:
        row = st.session_state.detail_row
        kc  = kategori_color(row.get("kategori",""))
        try:    pct = min(int(row.get("score", 0)), 100)
        except: pct = 0
        bar_col = "#16a34a" if pct >= 70 else "#d97706" if pct >= 40 else "#dc2626"

        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
        st.markdown(f'<p class="section-label">Detail Produk: {row.get("nama_file","")}</p>', unsafe_allow_html=True)

        dc1, dc2 = st.columns([1, 1.5], gap="large")
        with dc1:
            if row.get("image"):
                st.image(row["image"], use_column_width=True)
            else:
                st.markdown('<div class="hist-card-thumb-placeholder" style="border-radius:12px;min-height:200px;">Tidak Ada Gambar</div>', unsafe_allow_html=True)
        with dc2:
            sc = score_class(row.get("score", 0))
            st.markdown(f"""
            <div class="result-grid">
                <div class="result-card green">
                    <div class="result-card-label">Kategori</div>
                    <div class="result-card-value" style="color:{kc}">{row.get('kategori','')}</div>
                </div>
                <div class="result-card {sc}">
                    <div class="result-card-label">Confidence Score</div>
                    <div class="result-card-value big">{row.get('score','-')}</div>
                </div>
                <div class="result-card">
                    <div class="result-card-label">Waktu Scan</div>
                    <div class="result-card-value" style="font-size:0.82rem;font-family:'DM Sans',sans-serif;">{str(row.get('waktu',''))[:19]}</div>
                </div>
            </div>
            <div class="score-bar-wrap">
                <div class="score-bar-label"><span>Confidence Score</span><span>{row.get('score','-')} / 100</span></div>
                <div class="score-bar-track">
                    <div class="score-bar-fill" style="width:{pct}%;background:{bar_col};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('<p class="section-label">Teks OCR Lengkap</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="ocr-box">{row.get("teks_ocr","") or "(tidak ada teks)"}</div>', unsafe_allow_html=True)

        if st.button("Tutup Detail", use_container_width=False):
            st.session_state.detail_row = None
            st.rerun()


# ═════════════════════════════════════════════
#  TAB 3 — PERBANDINGAN
# ═════════════════════════════════════════════
elif st.session_state.active_tab == "Perbandingan":

    st.markdown('<p class="section-label">Bandingkan Produk dari Riwayat</p>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Pilih 2 hingga 4 produk dari riwayat untuk membandingkan kategori, confidence score, dan teks OCR secara berdampingan.</div>', unsafe_allow_html=True)

    if not data_all:
        st.markdown('<div class="empty-state">Belum ada riwayat untuk dibandingkan.</div>', unsafe_allow_html=True)
    else:
        file_names = [r.get("nama_file","") for r in data_all]
        selected = st.multiselect(
            "Pilih produk yang ingin dibandingkan:",
            options=file_names, max_selections=4,
            placeholder="Pilih 2 hingga 4 produk...",
        )

        if len(selected) >= 2:
            compare_data = [r for r in data_all if r.get("nama_file") in selected]

            img_cols = st.columns(len(compare_data), gap="medium")
            for i, row in enumerate(compare_data):
                with img_cols[i]:
                    kc = kategori_color(row.get("kategori",""))
                    kb = kategori_bg(row.get("kategori",""))
                    st.markdown(f'<div class="prep-card-label" style="text-align:center;margin-bottom:0.5rem;">{row.get("nama_file","")}</div>', unsafe_allow_html=True)
                    if row.get("image"):
                        st.image(row["image"], use_column_width=True)
                    else:
                        st.markdown('<div class="hist-card-thumb-placeholder" style="border-radius:12px;min-height:160px;">Tidak Ada Gambar</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="text-align:center;margin-top:0.5rem"><span class="hist-card-badge" style="background:{kb};color:{kc};font-size:0.85rem;padding:0.3rem 1rem;">{row.get("kategori","")}</span></div>', unsafe_allow_html=True)

            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
            st.markdown('<p class="section-label">Tabel Perbandingan</p>', unsafe_allow_html=True)

            def td_kat(r):
                kc = kategori_color(r.get("kategori",""))
                kb = kategori_bg(r.get("kategori",""))
                return f'<td><span style="background:{kb};color:{kc};padding:0.2rem 0.6rem;border-radius:999px;font-weight:700;font-size:0.8rem;">{r.get("kategori","")}</span></td>'

            st.markdown(f"""
            <table class="compare-table">
                <thead><tr>
                    <th style="width:130px">Atribut</th>
                    {"".join(f"<th>{r.get('nama_file','')}</th>" for r in compare_data)}
                </tr></thead>
                <tbody>
                    <tr><td><b>Kategori</b></td>{"".join(td_kat(r) for r in compare_data)}</tr>
                    <tr><td><b>Score</b></td>{"".join(f'<td><b>{r.get("score","-")}</b></td>' for r in compare_data)}</tr>
                    <tr><td><b>Waktu Scan</b></td>{"".join(f'<td>{str(r.get("waktu",""))[:16]}</td>' for r in compare_data)}</tr>
                    <tr><td><b>Penggalan OCR</b></td>{"".join(f'<td style="font-size:0.78rem;color:#6b7280;max-width:180px">{(r.get("teks_ocr") or "")[:150]}</td>' for r in compare_data)}</tr>
                </tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">Pilih minimal 2 produk dari dropdown di atas untuk mulai membandingkan.</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════
#  TAB 4 — STATISTIK
# ═════════════════════════════════════════════
elif st.session_state.active_tab == "Statistik":

    st.markdown('<p class="section-label">Ringkasan Statistik</p>', unsafe_allow_html=True)

    if not data_all:
        st.markdown('<div class="empty-state">Belum ada data untuk ditampilkan.</div>', unsafe_allow_html=True)
    else:
        total = len(data_all)
        cats  = {}
        for r in data_all:
            k = r.get("kategori","Tidak Diketahui")
            cats[k] = cats.get(k, 0) + 1

        tinggi_n = sum(v for k, v in cats.items() if "tinggi" in k.lower())
        sedang_n = sum(v for k, v in cats.items() if "sedang" in k.lower())
        rendah_n = sum(v for k, v in cats.items() if "rendah" in k.lower())

        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-card">
                <div class="stat-label">Total Scan</div>
                <div class="stat-value">{total}</div>
                <div class="stat-sub">gambar diproses</div>
            </div>
            <div class="stat-card" style="border-top-color:#16a34a">
                <div class="stat-label">Protein Tinggi</div>
                <div class="stat-value" style="color:#16a34a">{tinggi_n}</div>
                <div class="stat-sub">produk</div>
            </div>
            <div class="stat-card" style="border-top-color:#d97706">
                <div class="stat-label">Protein Sedang</div>
                <div class="stat-value" style="color:#d97706">{sedang_n}</div>
                <div class="stat-sub">produk</div>
            </div>
            <div class="stat-card" style="border-top-color:#dc2626">
                <div class="stat-label">Protein Rendah</div>
                <div class="stat-value" style="color:#dc2626">{rendah_n}</div>
                <div class="stat-sub">produk</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="section-label">Distribusi Kategori</p>', unsafe_allow_html=True)
        for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
            pct = round(count / total * 100)
            bc  = kategori_color(cat)
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
                <div class="score-bar-label">
                    <span style="font-weight:600;color:#374151;">{cat}</span>
                    <span>{count} produk ({pct}%)</span>
                </div>
                <div class="score-bar-track">
                    <div class="score-bar-fill" style="width:{pct}%;background:{bc};"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">Timeline 10 Scan Terbaru</p>', unsafe_allow_html=True)
        for row in list(reversed(data_all))[:10]:
            kc = kategori_color(row.get("kategori",""))
            kb = kategori_bg(row.get("kategori",""))
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:1rem;background:#fff;border-radius:12px;
                        padding:0.8rem 1.2rem;margin-bottom:0.5rem;
                        box-shadow:0 1px 8px rgba(37,99,235,0.05);border-left:4px solid {kc};">
                <div style="flex:1;font-weight:600;font-size:0.88rem;color:#1e3a8a;">{row.get('nama_file','')}</div>
                <span style="background:{kb};color:{kc};padding:0.2rem 0.7rem;border-radius:999px;font-size:0.75rem;font-weight:700;">{row.get('kategori','')}</span>
                <div style="font-size:0.75rem;color:#9ca3af;white-space:nowrap;">{str(row.get('waktu',''))[:16]}</div>
            </div>
            """, unsafe_allow_html=True)
