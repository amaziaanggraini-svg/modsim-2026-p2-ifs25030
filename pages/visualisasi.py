import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Konfigurasi Halaman
st.set_page_config(page_title="Kuesioner Analytics Dashboard", layout="wide")

st.title("📊 Dashboard Visualisasi Data Kuesioner")
st.markdown("Unggah file hasil survei Anda untuk melihat analisis distribusi jawaban.")

# --- FITUR INPUT DATA ---
uploaded_file = st.sidebar.file_uploader("Pilih file Excel atau CSV", type=['xlsx', 'csv'])

if uploaded_file is not None:
    # Membaca data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Persiapan Data (Menghilangkan kolom non-kuesioner jika ada)
        # Asumsi: Kolom pertama adalah 'Partisipan', sisanya adalah pertanyaan
        data_q = df.drop(columns=['Partisipan']) if 'Partisipan' in df.columns else df
        
        mapping = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
        order = ['STS', 'TS', 'CTS', 'CS', 'S', 'SS'] # Urutan untuk grafik
        
        # --- PRE-PROCESSING UNTUK GRAFIK ---
        flat_data = data_q.stack().reset_index()
        flat_data.columns = ['Index', 'Pertanyaan', 'Jawaban']
        
        # 1. Distribusi Keseluruhan (Bar & Pie)
        overall_dist = flat_data['Jawaban'].value_counts().reindex(order).fillna(0).reset_index()
        
        # 2. Rata-rata per Pertanyaan
        df_numeric = data_q.replace(mapping)
        avg_scores = df_numeric.mean().reset_index()
        avg_scores.columns = ['Pertanyaan', 'Rata-rata Skor']

        # 3. Kategori Positif, Netral, Negatif
        def categorize(val):
            if val in ['SS', 'S']: return 'Positif'
            if val in ['CS']: return 'Netral'
            return 'Negatif'
        
        flat_data['Kategori'] = flat_data['Jawaban'].apply(categorize)
        cat_dist = flat_data['Kategori'].value_counts().reset_index()

        # --- LAYOUT DASHBOARD ---
        
        # Row 1: Ringkasan Umum
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribusi Jawaban (Bar)")
            fig1 = px.bar(overall_dist, x='Jawaban', y='count', color='Jawaban',
                          color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.subheader("Proporsi Jawaban (Pie)")
            fig2 = px.pie(overall_dist, names='Jawaban', values='count', hole=0.4)
            st.plotly_chart(fig2, use_container_width=True)

        # Row 2: Stacked Bar & Average
        st.divider()
        col3, col4 = st.columns([3, 2])

        with col3:
            st.subheader("Distribusi Jawaban per Pertanyaan")
            # Menghitung silang Pertanyaan vs Jawaban
            stacked_data = pd.crosstab(flat_data['Pertanyaan'], flat_data['Jawaban']).reindex(columns=order).fillna(0)
            fig3 = px.bar(stacked_data, barmode='stack', orientation='h')
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.subheader("Rata-rata Skor per Pertanyaan")
            fig4 = px.bar(avg_scores, x='Rata-rata Skor', y='Pertanyaan', orientation='h', 
                          color='Rata-rata Skor', color_continuous_scale='Viridis')
            st.plotly_chart(fig4, use_container_width=True)

        # Row 3: Sentimen & Bonus (Heatmap)
        st.divider()
        col5, col6 = st.columns(2)

        with col5:
            st.subheader("Distribusi Kategori Sentimen")
            fig5 = px.bar(cat_dist, x='Kategori', y='count', color='Kategori',
                          color_discrete_map={'Positif':'green', 'Netral':'gray', 'Negatif':'red'})
            st.plotly_chart(fig5, use_container_width=True)

        with col6:
            st.subheader("🔥 Bonus: Heatmap Korelasi")
            # Korelasi antar pertanyaan untuk melihat keterkaitan jawaban
            corr = df_numeric.corr()
            fig6 = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
            st.plotly_chart(fig6, use_container_width=True)

    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses data: {e}")
else:
    st.info("Silakan unggah file kuesioner di sidebar untuk memulai.")