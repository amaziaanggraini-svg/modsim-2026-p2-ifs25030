import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Dashboard Analisis Kuesioner", layout="wide")

# --- 2. MEMUAT DATA ---
@st.cache_data
def load_data():
    # Membaca data utama kuesioner
    df_kuesioner = pd.read_csv("data_kuesioner (1).xlsx - Kuesioner.csv")
    # Membaca data pertanyaan untuk label grafik
    df_pertanyaan = pd.read_csv("data_kuesioner (1).xlsx - Pertanyaan.csv")
    return df_kuesioner, df_pertanyaan

try:
    df, df_soal = load_data()
    
    # Persiapan Data
    # Menghapus kolom 'Partisipan' untuk analisis
    data_q = df.drop(columns=['Partisipan'])
    
    # Mapping Skala
    skala_map = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
    urutan_label = ['SS', 'S', 'CS', 'CTS', 'TS', 'STS']
    
    # Membuat kamus pertanyaan { 'P1': 'Teks Pertanyaan...' }
    dict_soal = dict(zip(df_soal['ID'], df_soal['Pertanyaan']))

    # --- UI DASHBOARD ---
    st.title("📊 Dashboard Visualisasi Data Kuesioner")
    st.info("Data berhasil dimuat dari file CSV yang diunggah.")

    # --- TABEL RINGKASAN (METRICS) ---
    total_responden = len(df)
    total_soal = len(data_q.columns)
    col_a, col_b = st.columns(2)
    col_a.metric("Total Responden", f"{total_responden} Orang")
    col_b.metric("Total Pertanyaan", f"{total_soal} Butir")

    st.markdown("---")

    # --- SECTION 1: DISTRIBUSI KESELURUHAN ---
    st.subheader("🎯 Distribusi Jawaban Keseluruhan")
    c1, c2 = st.columns(2)
    
    seluruh_data = data_q.stack().value_counts().reindex(urutan_label).reset_index()
    seluruh_data.columns = ['Skala', 'Jumlah']

    with c1:
        fig_bar = px.bar(seluruh_data, x='Skala', y='Jumlah', color='Skala',
                         title="Total Frekuensi Jawaban",
                         color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with c2:
        fig_pie = px.pie(seluruh_data, values='Jumlah', names='Skala', 
                         title="Proporsi Jawaban (%)",
                         color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- SECTION 2: STACKED BAR PER PERTANYAAN ---
    st.subheader("📚 Distribusi per Pertanyaan")
    df_stack = data_q.apply(pd.Series.value_counts).fillna(0).T.reindex(columns=urutan_label)
    
    # Gunakan teks pertanyaan sebagai hover data
    df_stack['Teks'] = [dict_soal.get(i, i) for i in df_stack.index]
    
    fig_stack = px.bar(df_stack, barmode='stack', 
                       title="Detail Jawaban Tiap Butir Pertanyaan",
                       labels={'index': 'Kode Soal', 'value': 'Jumlah Responden'},
                       hover_data={'Teks': True})
    st.plotly_chart(fig_stack, use_container_width=True)

    # --- SECTION 3: RATA-RATA SKOR ---
    st.subheader("📈 Rata-rata Skor per Pertanyaan")
    rata_skor = data_q.replace(skala_map).mean().reset_index()
    rata_skor.columns = ['ID', 'Rata-rata']
    rata_skor['Pertanyaan'] = rata_skor['ID'].map(dict_soal)

    fig_avg = px.bar(rata_skor, x='ID', y='Rata-rata', 
                     hover_data=['Pertanyaan'], color='Rata-rata',
                     title="Skor Rata-rata (Skala 1-6)",
                     color_continuous_scale='GnBu')
    st.plotly_chart(fig_avg, use_container_width=True)

    # --- SECTION 4: POSITIF, NETRAL, NEGATIF ---
    st.subheader("🎭 Analisis Sentimen Jawaban")
    flat = data_q.stack()
    pos = flat.isin(['SS', 'S']).sum()
    net = flat.isin(['CS']).sum()
    neg = flat.isin(['CTS', 'TS', 'STS']).sum()
    
    df_sentimen = pd.DataFrame({
        'Kategori': ['Positif (SS, S)', 'Netral (CS)', 'Negatif (CTS, TS, STS)'],
        'Jumlah': [pos, net, neg]
    })
    
    fig_sent = px.bar(df_sentimen, x='Kategori', y='Jumlah', color='Kategori',
                      color_discrete_map={
                          'Positif (SS, S)': '#2ecc71',
                          'Netral (CS)': '#bdc3c7',
                          'Negatif (CTS, TS, STS)': '#e74c3c'
                      })
    st.plotly_chart(fig_sent, use_container_width=True)

    # --- BONUS: HEATMAP ---
    st.subheader("🔥 Bonus: Heatmap Respon")
    df_num = data_q.replace(skala_map)
    fig_heat = px.imshow(df_num.T, 
                         labels=dict(x="Responden", y="Pertanyaan", color="Skor"),
                         color_continuous_scale='YlGnBu',
                         aspect="auto")
    st.plotly_chart(fig_heat, use_container_width=True)

except Exception as e:
    st.error(f"Gagal memuat data. Pastikan file CSV tersedia. Error: {e}")