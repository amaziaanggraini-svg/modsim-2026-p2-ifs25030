import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Kuesioner Pro", layout="wide")

# Custom CSS untuk mempercantik tampilan
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Dashboard Visualisasi Data Kuesioner")

# --- FITUR INPUT DATA ---
st.sidebar.header("📁 Pengaturan Data")
uploaded_file = st.sidebar.file_uploader("Upload file Excel (.xlsx) atau CSV", type=['xlsx', 'csv'])

def load_data(file):
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return None

# Cek sumber data
df = None
if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    try:
        df = pd.read_excel("data_kuesioner.xlsx")
    except:
        st.info("💡 Silakan unggah file di sidebar atau pastikan 'data_kuesioner.xlsx' tersedia.")
        st.stop()

# --- PREPROCESSING ---
# Menghapus kolom identitas jika ada (asumsi kolom pertanyaan dimulai setelah 'Partisipan' atau 'Nama')
cols_to_drop = ['Partisipan', 'Nama', 'Timestamp', 'No']
data_q = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

# Definisi Skala
mapping = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
order_skala = ['STS', 'TS', 'CTS', 'CS', 'S', 'SS']
color_map = {'SS': '#1a9641', 'S': '#a6d96a', 'CS': '#ffffbf', 'CTS': '#fdae61', 'TS': '#f46d43', 'STS': '#d7191c'}

# Transformasi data ke format panjang (Long Format)
flat_data = data_q.stack().reset_index()
flat_data.columns = ['Index', 'Pertanyaan', 'Jawaban']

# --- RINGKASAN STATISTIK (Metric) ---
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Total Responden", len(df))
col_m2.metric("Total Pertanyaan", data_q.shape[1])
avg_total = data_q.replace(mapping).mean().mean()
col_m3.metric("Rata-rata Skor Global", f"{avg_total:.2f} / 6.0")

st.divider()

# --- VISUALISASI ---

# Row 1: Distribusi & Proporsi Keseluruhan
col1, col2 = st.columns([6, 4])

with col1:
    st.subheader("🎯 Distribusi Jawaban Keseluruhan")
    counts_all = flat_data['Jawaban'].value_counts().reindex(order_skala).fillna(0).reset_index()
    fig_bar = px.bar(counts_all, x='Jawaban', y='count', color='Jawaban', 
                     color_discrete_map=color_map, text_auto=True)
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.subheader("🍕 Proporsi Jawaban")
    fig_pie = px.pie(counts_all, names='Jawaban', values='count', 
                     color='Jawaban', color_discrete_map=color_map, hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# Row 2: Stacked Bar (Per Pertanyaan)
st.subheader("📑 Distribusi Jawaban per Pertanyaan")
stacked_df = pd.crosstab(flat_data['Pertanyaan'], flat_data['Jawaban']).reindex(columns=order_skala).fillna(0)
fig_stacked = px.bar(stacked_df, barmode='stack', orientation='h', color_discrete_map=color_map)
st.plotly_chart(fig_stacked, use_container_width=True)

# Row 3: Average Score & Sentiment
col3, col4 = st.columns(2)

with col3:
    st.subheader("📈 Rata-rata Skor per Pertanyaan")
    avg_scores = data_q.replace(mapping).mean().sort_values().reset_index()
    avg_scores.columns = ['Pertanyaan', 'Skor']
    fig_avg = px.bar(avg_scores, x='Skor', y='Pertanyaan', orientation='h', 
                     color='Skor', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig_avg, use_container_width=True)

with col4:
    st.subheader("🎭 Analisis Sentimen Kategori")
    pos = flat_data['Jawaban'].isin(['SS', 'S']).sum()
    net = flat_data['Jawaban'].isin(['CS']).sum()
    neg = flat_data['Jawaban'].isin(['CTS', 'TS', 'STS']).sum()
    
    sentiment_df = pd.DataFrame({
        'Kategori': ['Positif (SS, S)', 'Netral (CS)', 'Negatif (CTS, TS, STS)'],
        'Jumlah': [pos, net, neg]
    })
    fig_sent = px.bar(sentiment_df, x='Kategori', y='Jumlah', color='Kategori',
                      color_discrete_map={'Positif (SS, S)':'#2ecc71','Netral (CS)':'#f1c40f','Negatif (CTS, TS, STS)':'#e74c3c'})
    st.plotly_chart(fig_sent, use_container_width=True)

# --- BONUS: DIAGRAM LAINNYA ---
st.divider()
st.subheader("✨ Visualisasi Tambahan (Bonus)")
col5, col6 = st.columns(2)

with col5:
    # Bonus 1: Radar Chart (Analisis Profil)
    st.write("**Radar Chart: Karakteristik Jawaban**")
    avg_val = data_q.replace(mapping).mean().tolist()
    categories = data_q.columns.tolist()
    
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(r=avg_val, theta=categories, fill='toself', name='Skor Rata-rata'))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 6])))
    st.plotly_chart(fig_radar, use_container_width=True)

with col6:
    # Bonus 2: Heatmap (Pola Jawaban Responden)
    st.write("**Heatmap: Intensitas Jawaban (Responden vs Pertanyaan)**")
    heatmap_data = data_q.replace(mapping)
    fig_heat = px.imshow(heatmap_data, labels=dict(x="Pertanyaan", y="Responden", color="Skor"),
                         color_continuous_scale='YlGnBu')
    st.plotly_chart(fig_heat, use_container_width=True)

# Data Table
with st.expander("🔍 Lihat Detail Data Mentah"):
    st.dataframe(df, use_container_width=True)