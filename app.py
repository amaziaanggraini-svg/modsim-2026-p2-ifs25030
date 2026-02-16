import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Analisis Kuesioner", layout="wide")

# --- 1. FUNGSI MEMUAT DATA ---
@st.cache_data
def load_data():
    file_excel = "data_kuesioner.xlsx"
    file_csv = "data_kuesioner (1).xlsx - Kuesioner.csv"
    
    if os.path.exists(file_excel):
        return pd.read_excel(file_excel)
    elif os.path.exists(file_csv):
        return pd.read_csv(file_csv)
    else:
        st.error("❌ File data tidak ditemukan! Pastikan file excel atau csv tersedia.")
        st.stop()

df = load_data()

# --- 2. PERSIAPAN DATA ---
# Drop kolom 'Partisipan' agar hanya menyisakan pertanyaan (Q1, Q2, dst)
if 'Partisipan' in df.columns:
    data_q = df.drop(columns=['Partisipan'])
else:
    data_q = df.copy()

# Mapping Skor sesuai instruksi gambar: SS=6, S=5, CS=4, CTS=3, TS=2, STS=1
mapping = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
data_numeric = data_q.replace(mapping).apply(pd.to_numeric, errors='coerce')
order = ['SS', 'S', 'CS', 'CTS', 'TS', 'STS']

# --- 3. LAYOUT DASHBOARD ---
st.title("📊 Dashboard Analisis Kuesioner")
st.markdown("Visualisasi otomatis untuk hasil kuesioner berdasarkan kategori sentimen dan skor rata-rata.")
st.divider()

# --- ROW 1: Distribusi Keseluruhan & Proporsi (Pie Chart) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribusi Jawaban Keseluruhan")
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

# --- ROW 2: Stacked Bar per Pertanyaan ---
st.divider()
st.subheader("Distribusi Jawaban per Pertanyaan (Stacked Bar)")

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

# --- ROW 3: Rata-rata Skor & Sentimen ---
st.divider()
col3, col4 = st.columns(2)

with col3:
    st.subheader("Rata-rata Skor per Pertanyaan")
    # Menghitung rata-rata berdasarkan skala 1-6
    avg_scores = data_numeric.mean().reset_index()
    avg_scores.columns = ['Pertanyaan', 'Rata-rata']
    fig4 = px.bar(avg_scores, x='Pertanyaan', y='Rata-rata', 
                 color='Rata-rata', color_continuous_scale='Viridis')
    # Menambahkan garis bantu untuk rata-rata ideal
    fig4.update_yaxes(range=[0, 6])
    st.plotly_chart(fig4, use_container_width=True)

with col4:
    st.subheader("Distribusi Kategori Sentimen")
    # Logika Kategori sesuai gambar: Positif (SS, S), Netral (CS), Negatif (CTS, TS, STS)
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

# --- BONUS: Matriks Korelasi ---
st.divider()
st.subheader("💡 Bonus: Matriks Korelasi antar Pertanyaan")
st.write("Melihat hubungan antar pertanyaan (Semakin mendekati 1, semakin kuat hubungannya).")
corr = data_numeric.corr()
fig6 = px.imshow(corr, text_auto=".2f", color_continuous_scale='RdBu_r', aspect="auto")
st.plotly_chart(fig6, use_container_width=True)

# --- BAGIAN ANALISIS TEKSTUAL (Opsional untuk pengecekan) ---
with st.expander("Klik untuk melihat Ringkasan Statistik"):
    total_responses = len(flat_data)
    st.write(f"**Total Data Jawaban:** {total_responses}")
    st.write(f"**Skor Rata-rata Global:** {data_numeric.values.mean():.2f}")
    st.write(f"**Persentase Sentimen Positif:** {(pos/total_responses)*100:.1f}%")