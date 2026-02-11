import pandas as pd

# Load data langsung dari file yang Anda berikan
# Kita asumsikan file CSV hasil ekspor dari Excel Anda
try:
    df = pd.read_csv("data_kuesioner.xlsx - Kuesioner.csv")
except:
    df = pd.read_excel("data_kuesioner.xlsx", sheet_name="Kuesioner")

# Persiapan data
cols_q = [f'Q{i}' for i in range(1, 18)]
data_q = df[cols_q]
total_resp = len(df)
all_val = data_q.values.flatten()
counts = pd.Series(all_val).value_counts()

# Skor sesuai file Keterangan.csv
score_map = {'SS': 6, 'S': 5, 'CS': 4, 'CTS': 3, 'TS': 2, 'STS': 1}

target_question = input()

if target_question == "q1":
    # Skala paling banyak dipilih secara keseluruhan
    skala = counts.idxmax()
    jumlah = counts.max()
    persen = (jumlah / data_q.size) * 100
    print(f"{skala}|{jumlah}|{persen:.1f}")

elif target_question == "q2":
    # Skala paling sedikit dipilih secara keseluruhan
    skala = counts.idxmin()
    jumlah = counts.min()
    persen = (jumlah / data_q.size) * 100
    print(f"{skala}|{jumlah}|{persen:.1f}")

elif target_question == "q3":
    # SS paling banyak
    res = data_q.apply(lambda x: (x == "SS").sum())
    print(f"{res.idxmax()}|{res.max()}|{(res.max()/total_resp*100):.1f}")

elif target_question == "q4":
    # S paling banyak
    res = data_q.apply(lambda x: (x == "S").sum())
    print(f"{res.idxmax()}|{res.max()}|{(res.max()/total_resp*100):.1f}")

elif target_question == "q5":
    # CS paling banyak
    res = data_q.apply(lambda x: (x == "CS").sum())
    print(f"{res.idxmax()}|{res.max()}|{(res.max()/total_resp*100):.1f}")

elif target_question == "q6":
    # CTS paling banyak
    res = data_q.apply(lambda x: (x == "CTS").sum())
    print(f"{res.idxmax()}|{res.max()}|{(res.max()/total_resp*100):.1f}")

elif target_question == "q7":
    # TS paling banyak
    res = data_q.apply(lambda x: (x == "TS").sum())
    print(f"{res.idxmax()}|{res.max()}|{(res.max()/total_resp*100):.1f}")

elif target_question == "q8":
    # TS paling banyak (duplikasi q7 sesuai struktur anda)
    res = data_q.apply(lambda x: (x == "TS").sum())
    print(f"{res.idxmax()}|{res.max()}|{(res.max()/total_resp*100):.1f}")

elif target_question == "q9":
    # Mencari pertanyaan yang ada pilihan STS
    sts_list = [f"{c}:{(data_q[c]=='STS').sum()/total_resp*100:.1f}" for c in cols_q if (data_q[c]=='STS').any()]
    print("|".join(sts_list))

elif target_question == "q10":
    # Rata-rata keseluruhan
    avg = data_q.replace(score_map).values.mean()
    print(f"{avg:.2f}")

elif target_question == "q11":
    # Skor rata-rata tertinggi
    avg_q = data_q.replace(score_map).mean()
    print(f"{avg_q.idxmax()}:{avg_q.max():.2f}")

elif target_question == "q12":
    # Skor rata-rata terendah
    avg_q = data_q.replace(score_map).mean()
    print(f"{avg_q.idxmin()}:{avg_q.min():.2f}")

elif target_question == "q13":
    # Kategori positif, netral, negatif
    pos = counts.get('SS', 0) + counts.get('S', 0)
    net = counts.get('CS', 0)
    neg = counts.get('CTS', 0) + counts.get('TS', 0) + counts.get('STS', 0)
    total = pos + net + neg
    print(f"positif={pos}:{(pos/total*100):.1f}|netral={net}:{(net/total*100):.1f}|negatif={neg}:{(neg/total*100):.1f}")