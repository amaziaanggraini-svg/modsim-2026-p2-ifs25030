import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Analisis Kuesioner", layout="wide")

# Styling Header
st.title("📊 Dashboard Visualisasi Data Kuesioner")
st.markdown("---")

# --- 1. SIDEBAR & DATA LOADING ---
st.sidebar.header("Konfigurasi Data")
uploaded_file = st.sidebar.file_uploader("Upload file Excel (.xlsx) atau CSV", type=['xlsx', 'csv'])

# Definisi Skala Likert
mapping = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
order_skala = ['STS', 'TS', 'CTS', 'CS', 'S', 'SS']

def load_data(file):
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return None

# Load Data logic
df = None
if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    st.info("💡 Silakan unggah file kuesioner di sidebar. Pastikan kolom berisi jawaban (SS, S, CS, dll).")
    # Contoh data dummy agar dashboard tetap bisa dipreview (opsional)
    st.stop()

# --- 2. PENGOLAHAN DATA ---
# Menghapus kolom identitas jika ada (asumsi kolom 'Partisipan' atau 'Nama')
data_q = df.drop(columns=['Partisipan', 'Nama', 'No', 'Timestamp'], errors='ignore')

# Flatten data untuk agregasi global
flat_data = data_q.stack().reset_index()
flat_data.columns = ['ID', 'Pertanyaan', 'Jawaban']

# --- 3. VISUALISASI ---

# ROW 1: Distribusi Keseluruhan (Bar & Pie)
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Distribusi Jawaban (Bar)")
    counts_all = flat_data['Jawaban'].value_counts().reindex(order_skala).fillna(0).reset_index()
    fig_bar = px.bar(counts_all, x='Jawaban', y='count', color='Jawaban',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("2. Proporsi Jawaban (Pie)")
    fig_pie = px.pie(counts_all, names='Jawaban', values='count', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ROW 2: Stacked Bar per Pertanyaan
st.subheader("3. Distribusi Jawaban per Pertanyaan (Stacked Bar)")
stacked_df = pd.crosstab(flat_data['Pertanyaan'], flat_data['Jawaban']).reindex(columns=order_skala).fillna(0)
fig_stacked = px.bar(stacked_df, barmode='stack', orientation='h', 
                     color_discrete_sequence=px.colors.sequential.RdBu)
st.plotly_chart(fig_stacked, use_container_width=True)

st.divider()

# ROW 3: Rata-rata & Kategori Sentimen
col3, col4 = st.columns(2)

with col3:
    st.subheader("4. Rata-rata Skor per Pertanyaan")
    # Konversi jawaban teks ke angka untuk perhitungan rata-rata
    numeric_df = data_q.replace(mapping)
    avg_scores = numeric_df.mean().sort_values(ascending=True).reset_index()
    avg_scores.columns = ['Pertanyaan', 'Rata-rata Skor']
    
    fig_avg = px.bar(avg_scores, x='Rata-rata Skor', y='Pertanyaan', orientation='h',
                     color='Rata-rata Skor', color_continuous_scale='Viridis')
    st.plotly_chart(fig_avg, use_container_width=True)

with col4:
    st.subheader("5. Kategori Sentimen")
    pos = flat_data['Jawaban'].isin(['SS', 'S']).sum()
    net = flat_data['Jawaban'].isin(['CS']).sum()
    neg = flat_data['Jawaban'].isin(['CTS', 'TS', 'STS']).sum()
    
    sentiment_df = pd.DataFrame({
        'Kategori': ['Positif (SS/S)', 'Netral (CS)', 'Negatif (STS/TS/CTS)'],
        'Jumlah': [pos, net, neg]
    })
    fig_sent = px.bar(sentiment_df, x='Kategori', y='Jumlah', color='Kategori',
                      color_discrete_map={'Positif (SS/S)': '#2ecc71', 'Netral (CS)': '#f1c40f', 'Negatif (STS/TS/CTS)': '#e74c3c'})
    st.plotly_chart(fig_sent, use_container_width=True)

# --- 4. BONUS: RADAR CHART & DATA VIEW ---
st.divider()
st.subheader("✨ Bonus: Radar Chart (Profil Kuesioner)")

# Menyiapkan data untuk Radar Chart
categories = avg_scores['Pertanyaan'].tolist()
values = avg_scores['Rata-rata Skor'].tolist()

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
      r=values + [values[0]],
      theta=categories + [categories[0]],
      fill='toself',
      name='Skor Rata-rata'
))
fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 6])))
st.plotly_chart(fig_radar, use_container_width=True)

with st.expander("🔍 Lihat Detail Data Mentah"):
    st.dataframe(df)