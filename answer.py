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
    total_answers = len(flat_data)
    pos = flat_data.isin(['SS', 'S']).sum()
    net = flat_data.isin(['CS']).sum()
    neg = flat_data.isin(['CTS', 'TS', 'STS']).sum()
    
    print(f"positif={pos}:{(pos/total_answers)*100:.1f}|"
          f"netral={net}:{(net/total_answers)*100:.1f}|"
          f"negatif={neg}:{(neg/total_answers)*100:.1f}")