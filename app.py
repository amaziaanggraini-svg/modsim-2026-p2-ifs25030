import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- CONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Analisis Kuesioner", layout="wide")

# --- 1. FUNGSI MEMUAT DATA ---
@st.cache_data
def load_data():
    # Menyesuaikan dengan nama file yang terlihat di gambar folder kamu
    file_excel = "data_kuesioner.xlsx"
    file_csv = "data_kuesioner.csv" # Asumsi file 'data_kuesioner' tanpa ekstensi di gambar adalah CSV
    
    if os.path.exists(file_excel):
        return pd.read_excel(file_excel)
    elif os.path.exists(file_csv):
        return pd.read_csv(file_csv)
    else:
        st.error(f"❌ File tidak ditemukan! Pastikan file '{file_excel}' ada di folder yang sama dengan 'app.py'")
        st.stop()

# Memanggil fungsi load data
df = load_data()

# --- 2. PERSIAPAN DATA ---
# Menghapus kolom 'Partisipan' (pastikan nama kolom sesuai dengan file Excel kamu)
if 'Partisipan' in df.columns:
    data_q = df.drop(columns=['Partisipan'])
else:
    data_q = df.copy()

# Mapping Jawaban Likert
mapping = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
data_numeric = data_q.replace(mapping).apply(pd.to_numeric, errors='coerce')
order = ['SS', 'S', 'CS', 'CTS', 'TS', 'STS']

# --- 3. LAYOUT DASHBOARD ---
st.title("📊 Dashboard Analisis Kuesioner")
st.markdown("Visualisasi otomatis untuk hasil kuesioner.")
st.divider()

# ROW 1: Distribusi & Proporsi
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribusi Jawaban Keseluruhan")
    # Menghitung kemunculan tiap jawaban di seluruh tabel
    all_counts = data_q.stack().value_counts().reindex(order).reset_index()
    all_counts.columns = ['Jawaban', 'Jumlah']
    
    fig1 = px.bar(all_counts, x='Jawaban', y='Jumlah', 
                 color='Jawaban', 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Proporsi Jawaban (Pie Chart)")
    fig2 = px.pie(all_counts, values='Jumlah', names='Jawaban', 
                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig2, use_container_width=True)

# ROW 2: Stacked Bar per Pertanyaan
st.divider()
st.subheader("Distribusi Jawaban per Pertanyaan (Stacked Bar)")

# Mengolah data untuk Stacked Bar
stacked_list = []
for col in data_q.columns:
    counts = data_q[col].value_counts().reindex(order, fill_value=0)
    temp_df = pd.DataFrame({'Pertanyaan': col, 'Jawaban': counts.index, 'Jumlah': counts.values})
    stacked_list.append(temp_df)

df_stacked = pd.concat(stacked_list)

fig3 = px.bar(df_stacked, x='Pertanyaan', y='Jumlah', color='Jawaban',
             category_orders={"Jawaban": order},
             color_discrete_sequence=px.colors.qualitative.Safe)
st.plotly_chart(fig3, use_container_width=True)

# ROW 3: Skor Rata-rata & Kategori Sentimen
st.divider()
col3, col4 = st.columns(2)

with col3:
    st.subheader("Rata-rata Skor per Pertanyaan")
    avg_scores = data_numeric.mean().reset_index()
    avg_scores.columns = ['Pertanyaan', 'Rata-rata']
    fig4 = px.bar(avg_scores, x='Pertanyaan', y='Rata-rata', 
                 color='Rata-rata', color_continuous_scale='Viridis')
    st.plotly_chart(fig4, use_container_width=True)

with col4:
    st.subheader("Distribusi Kategori Sentimen")
    flat_data = data_q.stack()
    pos = flat_data.isin(['SS', 'S']).sum()
    net = flat_data.isin(['CS']).sum()
    neg = flat_data.isin(['CTS', 'TS', 'STS']).sum()
    
    sentiment_df = pd.DataFrame({
        'Kategori': ['Positif (SS/S)', 'Netral (CS)', 'Negatif (CTS/TS/STS)'],
        'Jumlah': [pos, net, neg]
    })
    fig5 = px.bar(sentiment_df, x='Kategori', y='Jumlah', 
                 color='Kategori', color_discrete_map={
                     'Positif (SS/S)': '#2ecc71', 
                     'Netral (CS)': '#f1c40f', 
                     'Negatif (CTS/TS/STS)': '#e74c3c'
                 })
    st.plotly_chart(fig5, use_container_width=True)

# BONUS: Heatmap Korelasi
st.divider()
st.subheader("💡 Bonus: Matriks Korelasi antar Pertanyaan")
corr = data_numeric.corr()
fig6 = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', aspect="auto")
st.plotly_chart(fig6, use_container_width=True)