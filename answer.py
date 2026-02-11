import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Kuesioner", layout="wide")

# Judul Utama
st.title("📊 Dashboard Visualisasi Data Kuesioner")

# --- FITUR INPUT DATA ---
st.sidebar.header("Input Data")
uploaded_file = st.sidebar.file_uploader("Upload file Excel (.xlsx) atau CSV", type=['xlsx', 'csv'])

# Gunakan data default jika belum ada upload (untuk menghindari error saat pertama jalan)
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return None

if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    # Mencoba mencari file lokal jika ada di direktori
    try:
        df = pd.read_excel("data_kuesioner.xlsx")
    except:
        st.info("💡 Silakan unggah file Excel/CSV di sidebar untuk melihat visualisasi.")
        st.stop()

# --- LOGIKA PENGOLAHAN DATA ---
# Menghilangkan kolom non-kuesioner
data_q = df.drop(columns=['Partisipan']) if 'Partisipan' in df.columns else df
n_partisipan = len(df)
mapping = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
order_skala = ['STS', 'TS', 'CTS', 'CS', 'S', 'SS']

# Data Flatten untuk grafik umum
flat_data = data_q.stack().reset_index()
flat_data.columns = ['Index', 'Pertanyaan', 'Jawaban']

# --- VISUALISASI ---

# Row 1: Bar & Pie (Distribusi Keseluruhan)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribusi Jawaban Keseluruhan")
    counts_all = flat_data['Jawaban'].value_counts().reindex(order_skala).fillna(0).reset_index()
    fig_bar = px.bar(counts_all, x='Jawaban', y='count', color='Jawaban', 
                     color_discrete_sequence=px.colors.qualitative.Safe)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("Proporsi Jawaban")
    fig_pie = px.pie(counts_all, names='Jawaban', values='count', hole=0.3)
    st.plotly_chart(fig_pie, use_container_width=True)

# Row 2: Stacked Bar (Distribusi per Pertanyaan)
st.divider()
st.subheader("Distribusi Jawaban per Pertanyaan (Stacked Bar)")
stacked_df = pd.crosstab(flat_data['Pertanyaan'], flat_data['Jawaban']).reindex(columns=order_skala).fillna(0)
fig_stacked = px.bar(stacked_df, barmode='stack', orientation='h')
st.plotly_chart(fig_stacked, use_container_width=True)

# Row 3: Average Score & Sentiment
st.divider()
col3, col4 = st.columns(2)

with col3:
    st.subheader("Rata-rata Skor per Pertanyaan")
    avg_scores = data_q.replace(mapping).mean().sort_values().reset_index()
    avg_scores.columns = ['Pertanyaan', 'Skor']
    fig_avg = px.bar(avg_scores, x='Skor', y='Pertanyaan', orientation='h', color='Skor')
    st.plotly_chart(fig_avg, use_container_width=True)

with col4:
    st.subheader("Kategori Positif, Netral, Negatif")
    pos = flat_data['Jawaban'].isin(['SS', 'S']).sum()
    net = flat_data['Jawaban'].isin(['CS']).sum()
    neg = flat_data['Jawaban'].isin(['CTS', 'TS', 'STS']).sum()
    
    sentiment_df = pd.DataFrame({
        'Kategori': ['Positif', 'Netral', 'Negatif'],
        'Jumlah': [pos, net, neg]
    })
    fig_sent = px.bar(sentiment_df, x='Kategori', y='Jumlah', 
                      color='Kategori', color_discrete_map={'Positif':'green','Netral':'gray','Negatif':'red'})
    st.plotly_chart(fig_sent, use_container_width=True)

# Bonus: Tabel Data Mentah
with st.expander("Lihat Data Mentah"):
    st.write(df)