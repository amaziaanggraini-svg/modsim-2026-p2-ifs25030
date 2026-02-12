import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Kuesioner Otomatis", layout="wide")

# --- DATA LOADING ---
# Fungsi untuk memuat data secara otomatis
@st.cache_data
def get_data():
    try:
        # Mengambil data dari file lokal
        return pd.read_excel("data_kuesioner.xlsx")
    except:
        # Jika file tidak ditemukan, buat data dummy agar visualisasi tetap muncul (Hanya untuk demo)
        data = {
            'Partisipan': [f'P{i}' for i in range(1, 11)],
            'Q1': ['SS', 'S', 'CS', 'SS', 'TS', 'S', 'SS', 'CS', 'S', 'SS'],
            'Q2': ['S', 'S', 'CTS', 'S', 'STS', 'S', 'CS', 'S', 'S', 'S'],
            'Q3': ['SS', 'SS', 'S', 'SS', 'CS', 'SS', 'S', 'SS', 'SS', 'SS']
        }
        return pd.DataFrame(data)

df = get_data()

# --- LOGIKA PENGOLAHAN DATA ---
data_q = df.drop(columns=['Partisipan']) if 'Partisipan' in df.columns else df
mapping = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
order_skala = ['STS', 'TS', 'CTS', 'CS', 'S', 'SS']

# Flatten data untuk grafik agregat
flat_data = data_q.stack().reset_index()
flat_data.columns = ['Index', 'Pertanyaan', 'Jawaban']

# --- DASHBOARD UI ---
st.title("📊 Visualisasi Hasil Kuesioner")
st.markdown("Dashboard ini menampilkan analisis distribusi jawaban secara otomatis.")

# Baris 1: Distribusi & Proporsi Keseluruhan
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Distribusi Jawaban Keseluruhan")
    counts_all = flat_data['Jawaban'].value_counts().reindex(order_skala).fillna(0).reset_index()
    fig_bar = px.bar(counts_all, x='Jawaban', y='count', color='Jawaban', 
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("2. Proporsi Jawaban (%)")
    fig_pie = px.pie(counts_all, names='Jawaban', values='count', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

# Baris 2: Distribusi per Pertanyaan
st.divider()
st.subheader("3. Distribusi Jawaban per Pertanyaan (Stacked Bar)")
stacked_df = pd.crosstab(flat_data['Pertanyaan'], flat_data['Jawaban']).reindex(columns=order_skala).fillna(0)
fig_stacked = px.bar(stacked_df, barmode='stack', orientation='h', 
                     color_discrete_sequence=px.colors.sequential.Viridis)
st.plotly_chart(fig_stacked, use_container_width=True)

# Baris 3: Skor Rata-rata & Sentimen
st.divider()
col3, col4 = st.columns(2)

with col3:
    st.subheader("4. Rata-rata Skor per Pertanyaan")
    avg_scores = data_q.replace(mapping).mean().sort_values().reset_index()
    avg_scores.columns = ['Pertanyaan', 'Skor']
    fig_avg = px.bar(avg_scores, x='Skor', y='Pertanyaan', orientation='h', 
                     color='Skor', color_continuous_scale='Blues')
    st.plotly_chart(fig_avg, use_container_width=True)

with col4:
    st.subheader("5. Kategori Sentimen")
    pos = flat_data['Jawaban'].isin(['SS', 'S']).sum()
    net = flat_data['Jawaban'].isin(['CS']).sum()
    neg = flat_data['Jawaban'].isin(['CTS', 'TS', 'STS']).sum()
    
    sentiment_df = pd.DataFrame({
        'Kategori': ['Positif (SS/S)', 'Netral (CS)', 'Negatif (CTS/TS/STS)'],
        'Jumlah': [pos, net, neg]
    })
    fig_sent = px.bar(sentiment_df, x='Kategori', y='Jumlah', color='Kategori',
                      color_discrete_map={'Positif (SS/S)':'#2ecc71',
                                          'Netral (CS)':'#bdc3c7',
                                          'Negatif (CTS/TS/STS)':'#e74c3c'})
    st.plotly_chart(fig_sent, use_container_width=True)

# Bonus: Heatmap Korelasi antar Pertanyaan
st.divider()
st.subheader("💡 Bonus: Heatmap Korelasi antar Pertanyaan")
numeric_df = data_q.replace(mapping)
corr = numeric_df.corr()
fig_heat = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
st.plotly_chart(fig_heat, use_container_width=True)