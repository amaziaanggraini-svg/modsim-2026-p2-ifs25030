import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. MEMUAT DATA ---
st.set_page_config(page_title="Dashboard Kuesioner", layout="wide")

try:
    df = pd.read_excel("data_kuesioner.xlsx")
except FileNotFoundError:
    # Sesuaikan dengan nama file CSV Anda jika file excel tidak ada
    df = pd.read_csv("data_kuesioner (1).xlsx - Kuesioner.csv")

# Persiapan Data
data_pertanyaan = df.drop(columns=['Partisipan'])
skala_ke_angka = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
urutan_label = ['SS', 'S', 'CS', 'CTS', 'TS', 'STS']

# --- HEADER ---
st.title("📊 Dashboard Visualisasi Data Kuesioner")
st.markdown("---")

# --- 2. DISTRIBUSI KESELURUHAN (Bar & Pie Chart) ---
st.subheader("🎯 Distribusi Jawaban Keseluruhan")
kol1, kol2 = st.columns(2)

seluruh_jawaban = data_pertanyaan.stack().value_counts().reindex(urutan_label).reset_index()
seluruh_jawaban.columns = ['Jawaban', 'Jumlah']

with kol1:
    fig_bar = px.bar(seluruh_jawaban, x='Jawaban', y='Jumlah', 
                     title="Distribusi Jawaban (Bar Chart)",
                     color='Jawaban', color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_bar, use_container_width=True)

with kol2:
    fig_pie = px.pie(seluruh_jawaban, values='Jumlah', names='Jawaban', 
                     title="Proporsi Jawaban (Pie Chart)",
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 3. STACKED BAR (Distribusi per Pertanyaan) ---
st.subheader("📚 Distribusi Jawaban per Pertanyaan")
df_stacked = data_pertanyaan.apply(pd.Series.value_counts).fillna(0).T
df_stacked = df_stacked.reindex(columns=urutan_label)

fig_stacked = px.bar(df_stacked, barmode='stack', 
                     title="Stacked Bar: Jawaban per Pertanyaan",
                     labels={'value': 'Jumlah Responden', 'index': 'Pertanyaan'})
st.plotly_chart(fig_stacked, use_container_width=True)

# --- 4. RATA-RATA SKOR PER PERTANYAAN ---
st.subheader("📈 Rata-rata Skor per Pertanyaan")
skor_rata2 = data_pertanyaan.replace(skala_ke_angka).mean().reset_index()
skor_rata2.columns = ['Pertanyaan', 'Rata-rata']

fig_rata = px.bar(skor_rata2, x='Pertanyaan', y='Rata-rata', 
                  title="Rata-rata Skor (Skala 1-6)",
                  color='Rata-rata', color_continuous_scale='Viridis')
st.plotly_chart(fig_rata, use_container_width=True)

# --- 5. KATEGORI POSITIF, NETRAL, NEGATIF ---
st.subheader("🎭 Distribusi Kategori Jawaban")
flat_data = data_pertanyaan.stack()
kat_pos = flat_data.isin(['SS', 'S']).sum()
kat_net = flat_data.isin(['CS']).sum()
kat_neg = flat_data.isin(['CTS', 'TS', 'STS']).sum()

df_kat = pd.DataFrame({
    'Kategori': ['Positif', 'Netral', 'Negatif'],
    'Jumlah': [kat_pos, kat_net, kat_neg]
})

fig_kat = px.bar(df_kat, x='Kategori', y='Jumlah', 
                 color='Kategori', 
                 color_discrete_map={'Positif': 'green', 'Netral': 'gray', 'Negatif': 'red'},
                 title="Distribusi Sentimen Jawaban")
st.plotly_chart(fig_kat, use_container_width=True)

# --- 6. BONUS: HEATMAP (Implementasi Diagram Lainnya) ---
st.subheader("🔥 Bonus: Heatmap Kepadatan Jawaban")
# Mengonversi data ke angka untuk heatmap
df_numeric = data_pertanyaan.replace(skala_ke_angka)
fig_heat = px.imshow(df_numeric.T, 
                     labels=dict(x="Responden", y="Pertanyaan", color="Skor"),
                     title="Heatmap Pola Jawaban Responden",
                     color_continuous_scale='RdYlGn')
st.plotly_chart(fig_heat, use_container_width=True)