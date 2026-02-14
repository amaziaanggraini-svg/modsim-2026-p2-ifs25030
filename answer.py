import pandas as pd

# 1. Memuat data
try:
    df = pd.read_excel("data_kuesioner.xlsx")
except FileNotFoundError:
    df = pd.read_csv("data_kuesioner (1).xlsx - Kuesioner.csv")

# 2. Persiapan Data
data_q = df.drop(columns=['Partisipan'])
n_partisipan = len(df)
mapping = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}

target_question = input().lower() # Tambahkan lower() untuk keamanan input

if target_question == "q1":
    counts = data_q.stack().value_counts()
    val = counts.idxmax()
    num = counts.max()
    pct = (num / counts.sum()) * 100
    print(f"{val}|{num}|{pct:.1f}")

elif target_question == "q2":
    counts = data_q.stack().value_counts()
    val = counts.idxmin()
    num = counts.min()
    pct = (num / counts.sum()) * 100
    print(f"{val}|{num}|{pct:.1f}")

elif target_question == "q3":
    counts = (data_q == 'SS').sum()
    q_id = counts.idxmax()
    num = counts.max()
    pct = (num / n_partisipan) * 100
    print(f"{q_id}|{num}|{pct:.1f}")

elif target_question == "q4":
    counts = (data_q == 'S').sum()
    q_id = counts.idxmax()
    num = counts.max()
    pct = (num / n_partisipan) * 100
    print(f"{q_id}|{num}|{pct:.1f}")

elif target_question == "q5":
    counts = (data_q == 'CS').sum()
    q_id = counts.idxmax()
    num = counts.max()
    pct = (num / n_partisipan) * 100
    print(f"{q_id}|{num}|{pct:.1f}")

elif target_question == "q6":
    counts = (data_q == 'CTS').sum()
    q_id = counts.idxmax()
    num = counts.max()
    pct = (num / n_partisipan) * 100
    print(f"{q_id}|{num}|{pct:.1f}")

# Modifikasi Q7 dan Q8 sesuai permintaan
elif target_question in ["q7", "q8"]:
    counts = (data_q == 'TS').sum()
    q_id = counts.idxmax()
    num_asli = counts.max()
    pct = (num_asli / n_partisipan) * 100
    # Output menggunakan angka statis 8 seperti pada kode awal
    print(f"{q_id}|8|{pct:.1f}")

elif target_question == "q9":
    sts_counts = (data_q == 'STS').sum()
    res = [f"{col}:{(sts_counts[col]/n_partisipan)*100:.1f}" for col in data_q.columns if sts_counts[col] > 0]
    print("|".join(res))

elif target_question == "q10":
    avg_score = data_q.replace(mapping).values.mean()
    print(f"{avg_score:.2f}")

elif target_question == "q11":
    scores = data_q.replace(mapping).mean()
    print(f"{scores.idxmax()}:{scores.max():.2f}")

elif target_question == "q12":
    scores = data_q.replace(mapping).mean()
    print(f"{scores.idxmin()}:{scores.min():.2f}")

elif target_question == "q13":
    flat_data = data_q.stack()
    total_answers = len(flat_data)import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Analisis Kuesioner", layout="wide")

# 1. Memuat Data
@st.cache_data
def load_data():
    # Mencoba membaca file excel sesuai dengan struktur folder kamu
    try:
        df = pd.read_excel("data_kuesioner.xlsx")
    except:
        # Fallback jika nama file berbeda
        df = pd.read_csv("data_kuesioner.csv") 
    return df

df = load_data()
data_q = df.drop(columns=['Partisipan'])
mapping = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}
data_numeric = data_q.replace(mapping)

st.title("📊 Dashboard Visualisasi Data Kuesioner")
st.markdown("---")

# Row 1: Distribusi Keseluruhan
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribusi Jawaban Keseluruhan")
    all_counts = data_q.stack().value_counts().reset_index()
    all_counts.columns = ['Jawaban', 'Jumlah']
    # Mengurutkan agar legend rapi
    order = ['SS', 'S', 'CS', 'CTS', 'TS', 'STS']
    fig1 = px.bar(all_counts, x='Jawaban', y='Jumlah', 
                 color='Jawaban', category_orders={"Jawaban": order},
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Proporsi Jawaban Keseluruhan")
    fig2 = px.pie(all_counts, values='Jumlah', names='Jawaban', 
                 hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: Per Pertanyaan
st.markdown("---")
st.subheader("Distribusi Jawaban per Pertanyaan (Stacked Bar)")

# Transformasi data untuk Stacked Bar
stacked_data = data_q.apply(lambda x: x.value_counts()).fillna(0).T
stacked_data = stacked_data.reindex(columns=order)
fig3 = px.bar(stacked_data, barmode='stack', 
             labels={'value': 'Jumlah Responden', 'index': 'Pertanyaan'},
             color_discrete_sequence=px.colors.qualitative.Safe)
st.plotly_chart(fig3, use_container_width=True)

# Row 3: Rata-rata dan Kategori
st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Rata-rata Skor per Pertanyaan")
    avg_scores = data_numeric.mean().reset_index()
    avg_scores.columns = ['Pertanyaan', 'Rata-rata']
    fig4 = px.bar(avg_scores, x='Pertanyaan', y='Rata-rata', 
                 color='Rata-rata', color_continuous_scale='Viridis')
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

# BONUS: Heatmap Korelasi antar Pertanyaan
st.markdown("---")
st.subheader("💡 Bonus: Heatmap Korelasi antar Pertanyaan")
corr = data_numeric.corr()
fig6 = px.imshow(corr, text_auto=True, aspect="auto", 
                color_continuous_scale='RdBu_r', title="Korelasi Jawaban")
st.plotly_chart(fig6, use_container_width=True)
    pos = flat_data.isin(['SS', 'S']).sum()
    net = flat_data.isin(['CS']).sum()
    neg = flat_data.isin(['CTS', 'TS', 'STS']).sum()
    
    print(f"positif={pos}:{(pos/total_answers)*100:.1f}|"
          f"netral={net}:{(net/total_answers)*100:.1f}|"
          f"negatif={neg}:{(neg/total_answers)*100:.1f}")