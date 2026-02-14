import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Kuesioner", layout="wide")
st.title("📊 Dashboard Analisis Kuesioner")

# 2. Memuat Data
@st.cache_data
def load_data():
    try:
        # Mencoba membaca file Excel atau CSV sesuai environment
        df = pd.read_excel("data_kuesioner.xlsx")
    except:
        df = pd.read_csv("data_kuesioner (1).xlsx - Kuesioner.csv")
    return df

df = load_data()
data_q = df.drop(columns=['Partisipan'])
mapping = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
order_skala = ['STS', 'TS', 'CTS', 'CS', 'S', 'SS']

# --- BAGIAN VISUALISASI ---

# Row 1: Distribusi Keseluruhan (Bar & Pie)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribusi Jawaban Keseluruhan")
    all_counts = data_q.stack().value_counts().reindex(order_skala)
    fig_bar_all = px.bar(x=all_counts.index, y=all_counts.values, 
                         labels={'x': 'Skala', 'y': 'Jumlah'},
                         color=all_counts.index, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_bar_all, use_container_width=True)

with col2:
    st.subheader("Proporsi Jawaban Keseluruhan")
    fig_pie = px.pie(names=all_counts.index, values=all_counts.values, 
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

# Row 2: Stacked Bar (Per Pertanyaan)
st.divider()
st.subheader("Distribusi Jawaban per Pertanyaan")
stacked_data = data_q.apply(lambda x: x.value_counts()).reindex(order_skala).T.fillna(0)
fig_stacked = px.bar(stacked_data, barmode="stack", 
                     labels={'value': 'Jumlah Responden', 'index': 'Pertanyaan', 'variable': 'Skala'},
                     color_discrete_sequence=px.colors.diverging.RdYlGn)
st.plotly_chart(fig_stacked, use_container_width=True)

# Row 3: Rata-rata Skor & Kategori
col3, col4 = st.columns(2)

with col3:
    st.subheader("Rata-rata Skor per Pertanyaan")
    avg_scores = data_q.replace(mapping).mean().sort_values()
    fig_avg = px.bar(x=avg_scores.values, y=avg_scores.index, orientation='h',
                     labels={'x': 'Rata-rata Skor', 'y': 'Pertanyaan'},
                     color=avg_scores.values, color_continuous_scale='Viridis')
    st.plotly_chart(fig_avg, use_container_width=True)

with col4:
    st.subheader("Distribusi Kategori Jawaban")
    flat_data = data_q.stack()
    pos = flat_data.isin(['SS', 'S']).sum()
    net = flat_data.isin(['CS']).sum()
    neg = flat_data.isin(['CTS', 'TS', 'STS']).sum()
    
    kat_df = pd.DataFrame({'Kategori': ['Positif', 'Netral', 'Negatif'], 'Jumlah': [pos, net, neg]})
    fig_kat = px.bar(kat_df, x='Kategori', y='Jumlah', color='Kategori',
                     color_discrete_map={'Positif': '#2ecc71', 'Netral': '#f1c40f', 'Negatif': '#e74c3c'})
    st.plotly_chart(fig_kat, use_container_width=True)

# BONUS: Heatmap Distribusi (Diagram Lainnya)
st.divider()
st.subheader("Bonus: Heatmap Intensitas Jawaban")
fig_heat = px.imshow(stacked_data.T, labels=dict(x="Pertanyaan", y="Skala", color="Jumlah"),
                     color_continuous_scale='YlGnBu')
st.plotly_chart(fig_heat, use_container_width=True)