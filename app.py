"""
===================================================
     🏦 ANTRIAN BANK PRIORITAS - CSV VERSION 🏦
===================================================
"""

import streamlit as st
import csv
import os
from collections import deque
from datetime import datetime

# ==================== SETUP ====================
st.set_page_config(
    page_title="Antrian Bank Prioritas (CSV)",
    page_icon="🏦",
    layout="centered"
)

# ==================== FILE CSV ====================
FILE_CSV = "antrian_bank.csv"

# ==================== FUNGSI CSV ====================
def load_data_csv():
    """Baca data dari file CSV"""
    antrian = deque()
    riwayat = []
    total = 0
    
    if os.path.exists(FILE_CSV):
        try:
            with open(FILE_CSV, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['jenis'] == 'antrian':
                        antrian.append((
                            int(row['prioritas']),
                            int(row['counter']),
                            {
                                'nomor': int(row['nomor']),
                                'nama': row['nama'],
                                'prioritas': int(row['prioritas']),
                                'waktu': row['waktu']
                            }
                        ))
                        total = max(total, int(row['nomor']))
                    elif row['jenis'] == 'riwayat':
                        riwayat.append({
                            'nomor': int(row['nomor']),
                            'nama': row['nama'],
                            'prioritas': int(row['prioritas']),
                            'waktu': row['waktu']
                        })
        except Exception as e:
            st.error(f"Error membaca CSV: {e}")
    
    return antrian, riwayat, total

def save_data_csv(antrian_list, riwayat, counter_prioritas):
    """Simpan data ke file CSV"""
    try:
        with open(FILE_CSV, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow(['jenis', 'nomor', 'nama', 'prioritas', 'counter', 'waktu'])
            
            # Data Antrian
            for p, cp, d in antrian_list:
                writer.writerow(['antrian', d['nomor'], d['nama'], d['prioritas'], cp, d['waktu']])
            
            # Data Riwayat
            for d in riwayat:
                writer.writerow(['riwayat', d['nomor'], d['nama'], d['prioritas'], 0, d['waktu']])
                
    except Exception as e:
        st.error(f"Error menyimpan CSV: {e}")

def update_csv():
    """Update file CSV dari session_state"""
    save_data_csv(
        st.session_state.antrian,
        st.session_state.riwayat,
        st.session_state.counter_prioritas
    )

# ==================== INISIALISASI DATA ====================
def init_session():
    """Inisialisasi session state dari CSV"""
    if 'initialized' not in st.session_state:
        antrian, riwayat, total = load_data_csv()
        
        st.session_state.antrian = antrian
        st.session_state.riwayat = riwayat
        st.session_state.nomor_antrian = total
        st.session_state.counter_prioritas = total
        st.session_state.teller = [None, None, None]
        st.session_state.total_dilayani = len(riwayat)
        st.session_state.initialized = True

# ==================== CLASS ====================
class AntrianBank:
    """Sistem Antrian Bank dengan Prioritas + CSV"""
    
    def __init__(self):
        # Pastikan data ter-load
        init_session()
    
    def ambil_nomor(self, nama, prioritas):
        st.session_state.nomor_antrian += 1
        st.session_state.counter_prioritas += 1
        
        data = {
            'nomor': st.session_state.nomor_antrian,
            'nama': nama,
            'prioritas': prioritas,
            'waktu': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.antrian.append((prioritas, st.session_state.counter_prioritas, data))
        
        # SAVE KE CSV
        update_csv()
        
        return st.session_state.nomor_antrian
    
    def cek_nomor(self, nomor):
        for p, cp, d in st.session_state.antrian:
            if d['nomor'] == nomor:
                return d, "Menunggu"
        
        for i, t in enumerate(st.session_state.teller, 1):
            if t and t['nomor'] == nomor:
                return t, f"Teller {i}"
        return None, None
    
    def lihat_semua(self):
        return sorted(st.session_state.antrian, key=lambda x: (x[0], x[1]))
    
    def update_data(self, nomor, nama_baru, prioritas_baru):
        for p, cp, d in st.session_state.antrian:
            if d['nomor'] == nomor:
                if nama_baru:
                    d['nama'] = nama_baru
                # UPDATE CSV
                update_csv()
                return True
        
        for t in st.session_state.teller:
            if t and t['nomor'] == nomor:
                if nama_baru:
                    t['nama'] = nama_baru
                # UPDATE CSV
                update_csv()
                return True
        return False
    
    def Batal_antrian(self, nomor):
        for p, cp, d in st.session_state.antrian:
            if d['nomor'] == nomor:
                st.session_state.antrian.remove((p, cp, d))
                # UPDATE CSV
                update_csv()
                return True
        return False
    
    def panggil(self, teller_id):
        if not st.session_state.antrian:
            return None
        
        antrian_urut = deque(sorted(st.session_state.antrian, key=lambda x: (x[0], x[1])))
        
        _, _, data = antrian_urut.popleft()
        st.session_state.antrian = antrian_urut
        st.session_state.teller[teller_id - 1] = data
        
        # UPDATE CSV
        update_csv()
        
        return data
    
    def selesai(self, teller_id):
        if st.session_state.teller[teller_id - 1]:
            data = st.session_state.teller[teller_id - 1]
            st.session_state.teller[teller_id - 1] = None
            st.session_state.riwayat.append(data)
            st.session_state.total_dilayani += 1
            
            # UPDATE CSV
            update_csv()
            
            return data
        return None
    
    def label_prioritas(self, p):
        labels = {0: "SANGAT UTAMA", 1: "UTAMA", 2: "TINGGI", 3: "NORMAL"}
        return labels.get(p, f"P-{p}")

# ==================== CUSTOM CSS ====================
st.markdown("""
    <style>
        .stApp { background-color: #F0F4F8; }
        [data-testid="stSidebar"] { background-color: #1E293B; }
        [data-testid="stSidebar"] .stMarkdown, 
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label { color: #FFFFFF !important; }
    </style>
""", unsafe_allow_html=True)

# ==================== INIT ====================
bank = AntrianBank()

# ==================== SIDEBAR ====================
st.sidebar.title("🏦 Menu")
menu = st.sidebar.selectbox(
    "Pilih Menu:",
    ["🏠 Home", "📝 Ambil Nomor", "📋 Lihat Antrian", 
     "🔍 Cek Nomor", "✏️ Ubah Data", "❌ Batal", 
     "📞 Panggil", "✅ Selesai", "📊 Status"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Prioritas")
st.sidebar.markdown("""
- **P-0**: SANGAT UTAMA (Ibu Hamil/Lansia)
- **P-1**: UTAMA (VIP)
- **P-2**: TINGGI (Pensiunan)
- **P-3**: NORMAL (Umum)
""")

# ==================== HOME ====================
if menu == "🏠 Home":
    st.title("🏦 Antrian Bank Prioritas")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Menunggu", len(st.session_state.antrian))
    with col2:
        st.metric("👨‍💼 Teller Aktif", sum(1 for t in st.session_state.teller if t))
    with col3:
        st.metric("✅ Total Dilayani", st.session_state.total_dilayani)
    
    st.markdown("---")
    st.subheader("👨‍💼 Status Teller")
    for i, t in enumerate(st.session_state.teller, 1):
        if t:
            label = bank.label_prioritas(t['prioritas'])
            st.success(f"Teller {i}: {t['nama']} (No.{t['nomor']}) [{label}]")
        else:
            st.info(f"Teller {i}: 🟢 Idle")
    
    st.markdown("---")
    st.caption("💾 Data disimpan ke: antrian_bank.csv")

# ==================== CREATE ====================
elif menu == "📝 Ambil Nomor":
    st.title("📝 Ambil Nomor Antrian")
    st.markdown("---")
    
    with st.form("form_ambil"):
        nama = st.text_input("Nama Nasabah", placeholder="Masukkan nama...")
        pilihan_prioritas = st.selectbox(
            "Prioritas",
            options=[
                (0, "SANGAT UTAMA - Ibu Hamil/Lansia"), 
                (1, "UTAMA - VIP"), 
                (2, "TINGGI - Pensiunan"), 
                (3, "NORMAL - Umum")
            ],
            format_func=lambda x: x[1]
        )
        
        submit = st.form_submit_button("✅ Ambil Nomor")
        
        if submit:
            if nama:
                no = bank.ambil_nomor(nama, pilihan_prioritas[0])
                st.success(f"✅ {nama} ➜ Nomor Antrian: {no} [{bank.label_prioritas(pilihan_prioritas[0])}]")
            else:
                st.error("❌ Nama tidak boleh kosong!")

# ==================== READ ====================
elif menu == "📋 Lihat Antrian":
    st.title("📋 Daftar Antrian")
    st.markdown("---")
    
    antrian_urut = bank.lihat_semua()
    
    if antrian_urut:
        data_list = []
        for _, _, d in antrian_urut:
            data_list.append({
                "No. Antrian": d['nomor'],
                "Nama": d['nama'],
                "Prioritas": bank.label_prioritas(d['prioritas']),
                "Waktu": d.get('waktu', '-')
            })
        
        st.dataframe(data_list, use_container_width=True)
        
        st.markdown("---")
        st.write(f"📋 Total: **{len(antrian_urut)}** orang menunggu")
    else:
        st.info("📋 Antrian kosong!")

# ==================== CEK NOMOR ====================
elif menu == "🔍 Cek Nomor":
    st.title("🔍 Cek Nomor Antrian")
    st.markdown("---")
    
    no = st.number_input("Masukkan Nomor Antrian", min_value=1, step=1)
    
    if st.button("🔍 Cek"):
        data, status = bank.cek_nomor(no)
        
        if data:
            st.success(f"📋 Data Nasabah No.{no}")
            st.write(f"**Nama:** {data['nama']}")
            st.write(f"**Prioritas:** {bank.label_prioritas(data['prioritas'])}")
            st.write(f"**Status:** {status}")
        else:
            st.error(f"❌ Nomor {no} tidak ditemukan!")

# ==================== UPDATE ====================
elif menu == "✏️ Ubah Data":
    st.title("✏️ Ubah Data Nasabah")
    st.markdown("---")
    
    update_no = st.number_input("Nomor Antrian", min_value=1, step=1, key="update_no")
    update_nama = st.text_input("Nama Baru", key="update_nama")
    
    if st.button("✏️ Ubah Data"):
        if bank.update_data(update_no, update_nama if update_nama else None, None):
            st.success(f"✅ Berhasil ubah data No.{update_no}")
        else:
            st.error(f"❌ Gagal: No.{update_no} tidak ditemukan!")

# ==================== DELETE ====================
elif menu == "❌ Batal":
    st.title("❌ Batal Antrian")
    st.markdown("---")
    
    batal_no = st.number_input("Nomor Antrian", min_value=1, step=1, key="batal_no")
    
    if st.button("❌ Batal Antrian"):
        if bank.Batal_antrian(batal_no):
            st.success(f"✅ Antrian No.{batal_no} dibatalkan!")
        else:
            st.error(f"❌ Gagal: No.{batal_no} tidak ditemukan!")

# ==================== PANGGIL ====================
elif menu == "📞 Panggil":
    st.title("📞 Panggil Nasabah")
    st.markdown("---")
    
    pilih_teller = st.selectbox("Pilih Teller", options=[1, 2, 3], format_func=lambda x: f"Teller {x}")
    
    if st.button("📞 Panggil Nasabah"):
        data = bank.panggil(pilih_teller)
        
        if data:
            st.success(f"Teller {pilih_teller}: Memanggil {data['nama']} (No.{data['nomor']}) [{bank.label_prioritas(data['prioritas'])}]")
        else:
            st.warning(f"Teller {pilih_teller}: Antrian kosong!")

# ==================== SELESAI ====================
elif menu == "✅ Selesai":
    st.title("✅ Selesai Layanan")
    st.markdown("---")
    
    selesaikan_teller = st.selectbox("Pilih Teller", options=[1, 2, 3], format_func=lambda x: f"Teller {x}")
    
    if st.button("✅ Selesai"):
        data = bank.selesai(selesaikan_teller)
        
        if data:
            st.success(f"Teller {selesaikan_teller}: ✅ Selesai melayani {data['nama']}")
        else:
            st.warning(f"Teller {selesaikan_teller}: Tidak ada yang dilayani!")

# ==================== STATUS ====================
elif menu == "📊 Status":
    st.title("📊 Status Lengkap")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Menunggu", len(st.session_state.antrian))
    with col2:
        st.metric("👨‍💼 Teller Aktif", sum(1 for t in st.session_state.teller if t))
    with col3:
        st.metric("✅ Dilayani", st.session_state.total_dilayani)
    with col4:
        st.metric("📝 Total", st.session_state.nomor_antrian)
    
    st.markdown("---")
    st.subheader("📋 Antrian Menunggu")
    antrian_urut = bank.lihat_semua()
    
    if antrian_urut:
        for _, _, d in antrian_urut:
            label = bank.label_prioritas(d['prioritas'])
            st.write(f"• No.{d['nomor']:2d} - {d['nama']:20s} [{label}]")
    else:
        st.info("Antrian kosong!")
    
    st.markdown("---")
    st.subheader("👨‍💼 Status Teller")
    for i, t in enumerate(st.session_state.teller, 1):
        if t:
            label = bank.label_prioritas(t['prioritas'])
            st.success(f"Teller {i}: {t['nama']} (No.{t['nomor']}) [{label}]")
        else:
            st.info(f"Teller {i}: 🟢 Idle")
