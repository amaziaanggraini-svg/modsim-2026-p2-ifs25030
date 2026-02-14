import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Analisis Kuesioner", layout="wide")

# --- 1. FUNGSI MEMUAT DATA (SOLUSI ERROR) ---
@st.cache_data
def load_data():
    # Daftar kemungkinan nama file yang ada di direktori kamu
    possible_files = [
        "data_kuesioner.xlsx", 
        "data_kuesioner.csv",
        "data_kuesioner (1).xlsx - Kuesioner.csv"
    ]
    
    for file in possible_files:
        try:
            if file.endswith('.xlsx'):
                return pd.read_excel(file)
            else:
                return pd.read_csv(file)
        except (FileNotFoundError, Exception):
            continue
    
    # Jika semua file tidak ditemukan
    st.error("❌ File data tidak ditemukan di direktori! Pastikan file 'data_kuesioner.xlsx' sudah diunggah.")
    st.stop()

# Memanggil fungsi load data
df = load_data()

# --- 2. PERSIAPAN DATA ---
# Menghapus kolom 'Partisipan' untuk analisis
data_q = df.drop(columns=['Partisipan'])
mapping = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
data_numeric = data_q.replace(mapping)
order = ['SS', 'S', 'CS', 'CTS', 'TS', 'STS']

# --- 3. LAYOUT DASHBOARD ---
st.title("📊 Dashboard Analisis Kuesioner")
st.markdown("Dashboard ini menampilkan visualisasi otomatis dari data kuesioner yang tersedia.")
st.divider()

# ROW 1: Distribusi & Proporsi
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribusi Jawaban Keseluruhan")
    all_counts = data_q.stack().value_counts().reset_index()
    all_counts.columns = ['Jawaban', 'Jumlah']
    fig1 = px.bar(all_counts, x='Jawaban', y='Jumlah', 
                 color='Jawaban', category_orders={"Jawaban": order},
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Proporsi Jawaban (Pie Chart)")
    fig2 = px.pie(all_counts, values='Jumlah', names='Jawaban', 
                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig2, use_container_width=True)

# ROW 2: Stacked Bar per Pertanyaan
st.divider()
st.subheader("Distribusi Jawaban per Pertanyaan")
stacked_data = data_q.apply(lambda x: x.value_counts()).fillna(0).T
# Memastikan kolom berurutan SS -> STS
stacked_columns = [col for col in order if col in stacked_data.columns]
stacked_data = stacked_data[stacked_columns]

fig3 = px.bar(stacked_data, barmode='stack', 
             labels={'value': 'Jumlah Responden', 'index': 'Pertanyaan'},
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
                 color='Rata-rata', color_continuous_scale='Blues')
    st.plotly_chart(fig4, use_container_width=True)

with col4:
    st.subheader("Distribusi Kategori Sentimen")
    flat_data = data_q.stack()
    pos = flat_data.isin(['SS', 'S']).sum()
    net = flat_data.isin(['CS']).sum()
    neg = flat_data.isin(['CTS', 'TS', 'STS']).sum()
    
    sentiment_df = pd.DataFrame({
        'Kategori': ['Positif', 'Netral', 'Negatif'],
        'Jumlah': [pos, net, neg]
    })
    fig5 = px.bar(sentiment_df, x='Kategori', y='Jumlah', 
                 color='Kategori', color_discrete_map={
                     'Positif': '#2ecc71', 'Netral': '#f1c40f', 'Negatif': '#e74c3c'
                 })
    st.plotly_chart(fig5, use_container_width=True)

# BONUS: Heatmap
st.divider()
st.subheader("💡 Bonus: Matriks Korelasi Jawaban")
corr = data_numeric.corr()
fig6 = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r')
st.plotly_chart(fig6, use_container_width=True)