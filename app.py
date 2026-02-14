import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Analisis Kuesioner", layout="wide")
st.title("📊 Dashboard Analisis Kuesioner")

# 2. Fungsi Memuat Data (Disesuaikan dengan nama file di folder Anda)
@st.cache_data
def load_data():
    # Nama file harus sesuai persis dengan yang ada di gambar folder Anda
    file_path = "data_kuesioner.xlsx" 
    try:
        # Menggunakan engine='openpyxl' untuk membaca file .xlsx
        return pd.read_excel(file_path)
    except Exception as e:
        st.error(f"Gagal memuat file '{file_path}'. Pastikan file sudah di-upload ke GitHub.")
        st.stop()

df = load_data()

# 3. Persiapan Data (Menghapus kolom non-kuesioner seperti 'Partisipan')
# Pastikan nama kolom 'Partisipan' sesuai dengan di file Anda
data_q = df.drop(columns=['Partisipan'])
n_partisipan = len(df)
mapping = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
order_skala = ['STS', 'TS', 'CTS', 'CS', 'S', 'SS']

# --- VISUALISASI SESUAI PERMINTAAN ---

# Row 1: Bar Chart & Pie Chart (Distribusi Keseluruhan)
col1, col2 = st.columns(2)
all_counts = data_q.stack().value_counts().reindex(order_skala).fillna(0)

with col1:
    st.subheader("Distribusi Jawaban Keseluruhan")
    fig_bar = px.bar(x=all_counts.index, y=all_counts.values, labels={'x':'Skala', 'y':'Jumlah'})
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("Proporsi Jawaban Keseluruhan")
    fig_pie = px.pie(names=all_counts.index, values=all_counts.values)
    st.plotly_chart(fig_pie, use_container_width=True)

# Row 2: Stacked Bar (Per Pertanyaan)
st.subheader("Distribusi Jawaban per Pertanyaan (Stacked Bar)")
stacked_data = data_q.apply(lambda x: x.value_counts()).reindex(order_skala).T.fillna(0)
fig_stacked = px.bar(stacked_data, barmode="stack")
st.plotly_chart(fig_stacked, use_container_width=True)

# Row 3: Rata-rata Skor & Sentimen
col3, col4 = st.columns(2)

with col3:
    st.subheader("Rata-rata Skor per Pertanyaan")
    avg_scores = data_q.replace(mapping).mean()
    fig_avg = px.bar(x=avg_scores.index, y=avg_scores.values, labels={'x':'Pertanyaan', 'y':'Skor'})
    st.plotly_chart(fig_avg, use_container_width=True)

with col4:
    st.subheader("Distribusi Kategori Sentimen")
    flat_data = data_q.stack()
    pos = flat_data.isin(['SS', 'S']).sum()
    net = flat_data.isin(['CS']).sum()
    neg = flat_data.isin(['CTS', 'TS', 'STS']).sum()
    sentiment_df = pd.DataFrame({'Kategori': ['Positif', 'Netral', 'Negatif'], 'Jumlah': [pos, net, neg]})
    fig_sent = px.bar(sentiment_df, x='Kategori', y='Jumlah', color='Kategori')
    st.plotly_chart(fig_sent, use_container_width=True)