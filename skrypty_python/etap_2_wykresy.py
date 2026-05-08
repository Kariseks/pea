import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np
# ============================================================
# PARAMETRY I KONFIGURACJA
# ============================================================

INPUT_CSV = "../etap_2/wyniki.csv"
KILLED_CSV = "../etap_2/killed.csv"
OUTPUT_DIR = "../etap_2/sprawko/rys"
CSV_SEPARATOR = ";"
SAVE_LATEX_TABLES = True
FIGSIZE = (12, 7)

ALGORITHMS = ["deep_first_search", "breadth_first_search", "best_first_search"]

ALGORITHM_COLORS = {
    "deep_first_search": "tab:blue",
    "breadth_first_search": "tab:orange",
    "best_first_search": "tab:green",
}

ALGORITHM_DISPLAY_NAMES = {
    "deep_first_search": "DFS",
    "breadth_first_search": "BFS",
    "best_first_search": "LC",
}


def format_engineering_time(seconds: float) -> str:
    """Konwertuje sekundy na czytelny format (h, min, s, ms, us, ns)."""
    if seconds == 0:
        return "0 s"

    abs_sec = abs(seconds)

    if abs_sec >= 3600:
        h = int(abs_sec // 3600)
        m = int((abs_sec % 3600) // 60)
        s = int(abs_sec % 60)
        return f"{h} h {m} min {s} s"
    elif abs_sec >= 60:
        m = int(abs_sec // 60)
        s = int(abs_sec % 60)
        return f"{m} min {s} s"
    elif abs_sec >= 1:
        return f"{seconds:.3f} s"
    elif abs_sec >= 1e-3:
        return f"{seconds * 1e3:.3f} ms"
    elif abs_sec >= 1e-6:
        # raw string rf"" naprawia SyntaxWarning dla \mu
        return rf"{seconds * 1e6:.3f} $\mu$s"
    else:
        return f"{seconds * 1e9:.3f} ns"


import re

# ============================================================
# WCZYTANIE I PRZYGOTOWANIE DANYCH
# ============================================================

Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
columns = ["instance_name", "time_seconds", "instance_size", "algorithm", "cost", "date"]

# 1. Wczytanie wyników głównych (wyniki.csv)
df_raw = pd.read_csv(INPUT_CSV, sep=CSV_SEPARATOR, header=None, names=columns)
df_raw = df_raw[df_raw["algorithm"].isin(ALGORITHMS)].copy()

for col in ["time_seconds", "instance_size", "cost"]:
    df_raw[col] = pd.to_numeric(df_raw[col], errors='coerce')

# Średnia po instancji (wyniki udane)
df_instance_avg = df_raw.groupby(["instance_name", "instance_size", "algorithm"], as_index=False).agg(
    avg_time_seconds=("time_seconds", "mean"),
    avg_cost=("cost", "mean")
)

# Średnia po rozmiarze N (do wykresów)
df_size_avg = df_instance_avg.groupby(["instance_size", "algorithm"], as_index=False).agg(
    avg_time_seconds=("avg_time_seconds", "mean")
)


# 2. Wczytanie i naprawa danych o zabitych procesach (killed.csv)
def extract_size_from_name(name):
    """Wyciąga liczby z nazwy instancji, np. 'br17' -> 17."""
    if pd.isna(name):
        return 0
    match = re.search(r'\d+', str(name))
    return int(match.group()) if match else 0


if os.path.exists(KILLED_CSV):
    # Wczytujemy jako tekst, by uniknąć problemów z typami
    df_killed = pd.read_csv(KILLED_CSV, sep=CSV_SEPARATOR, header=None, names=columns, dtype=str)

    # Rozmiar wyciągamy tylko z nazwy
    df_killed["instance_size"] = df_killed["instance_name"].apply(extract_size_from_name)

    # Dla zabitych procesów ustawiamy -1, aby odróżnić je od poprawnych pomiarów
    df_killed["avg_time_seconds"] = -1.0
    df_killed["instance_size"] = pd.to_numeric(df_killed["instance_size"], errors='coerce')

    df_killed = df_killed[["instance_name", "instance_size", "algorithm", "avg_time_seconds"]]
else:
    df_killed = pd.DataFrame(columns=["instance_name", "instance_size", "algorithm", "avg_time_seconds"])

# ============================================================
# ŁĄCZENIE DANYCH (PRIORYTET DLA WYNIKI.CSV)
# ============================================================

df_results = df_instance_avg.copy()
df_killed_raw = df_killed.copy()

if not df_killed_raw.empty:
    finished_tasks = set(zip(df_results["instance_name"], df_results["algorithm"]))
    mask = df_killed_raw.apply(lambda x: (x["instance_name"], x["algorithm"]) not in finished_tasks, axis=1)
    df_killed_filtered = df_killed_raw[mask].copy()
else:
    df_killed_filtered = df_killed_raw

# Połączenie i mapowanie nazw
df_combined = pd.concat([df_results, df_killed_filtered], ignore_index=True)
df_combined["algorithm"] = df_combined["algorithm"].map(ALGORITHM_DISPLAY_NAMES)

# ============================================================
# PRZYGOTOWANIE TABELI (PIVOT)
# ============================================================

# pivot_table automatycznie wstawi NaN tam, gdzie nie ma danych w ogóle
df_pivot = df_combined.pivot_table(
    index=["instance_size", "instance_name"],
    columns="algorithm",
    values="avg_time_seconds",
    aggfunc='mean'
).reset_index()

df_pivot = df_pivot.sort_values("instance_size")
available_algs = [name for name in ["BFS", "DFS", "LC"] if name in df_pivot.columns]
df_pivot = df_pivot[["instance_size", "instance_name"] + available_algs]
df_pivot.columns = ["Rozmiar", "Instancja"] + available_algs

# ============================================================
# EKSPORT TABEL (CSV & LATEX)
# ============================================================

csv_path = os.path.join(OUTPUT_DIR, "results_by_instance_name.csv")
latex_path = os.path.join(OUTPUT_DIR, "average_results_by_size.tex")

df_pivot.to_csv(csv_path, index=False)

if SAVE_LATEX_TABLES:
    df_latex = df_pivot.copy()


    def final_format(val):
        # TRAKTOWANIE BRAKU DANYCH:
        # Jeśli NaN (brak rekordu w obu plikach)
        # lub <= 0 (proces zabity lub błąd pomiaru)
        # -> zwróć kreskę
        if pd.isna(val) or (isinstance(val, (int, float)) and val <= 0):
            return "-"
        return format_engineering_time(val)


    for col in available_algs:
        df_latex[col] = df_latex[col].apply(final_format)

    latex_table = df_latex.to_latex(
        index=False,
        escape=False,
        column_format="l l r r r"
    )

    with open(latex_path, "w", encoding="utf-8") as f:
        f.write(latex_table)
# ============================================================
# GENEROWANIE WYKRESÓW
# ============================================================

# Wykres 1: Średni czas (Liniowy)
plt.figure(figsize=FIGSIZE)
for alg in ALGORITHMS:
    subset = df_size_avg[df_size_avg["algorithm"] == alg].sort_values("instance_size")
    plt.plot(subset["instance_size"], subset["avg_time_seconds"], marker="o",
             label=ALGORITHM_DISPLAY_NAMES[alg], color=ALGORITHM_COLORS[alg])
plt.xlabel("Rozmiar instancji");
plt.ylabel("Średni czas [s]");
plt.grid(True);
plt.legend()
plot1_path = os.path.join(OUTPUT_DIR, "avg_time_vs_instance_size.pdf")
plt.savefig(plot1_path);
plt.close()

# Wykres 2: Wszystkie instancje (Punkty, Skala liniowa) + ETYKIETY
plt.figure(figsize=FIGSIZE)
for alg in ALGORITHMS:
    subset = df_instance_avg[df_instance_avg["algorithm"] == alg]
    plt.scatter(subset["instance_size"], subset["avg_time_seconds"],
                label=ALGORITHM_DISPLAY_NAMES[alg], color=ALGORITHM_COLORS[alg], alpha=0.6)

    # Dodawanie nazw instancji nad punktami
    for _, row in subset.iterrows():
        plt.text(row["instance_size"], row["avg_time_seconds"], str(row["instance_name"]),
                 fontsize=8, va="bottom", ha="center", rotation=45, alpha=0.7)

plt.xlabel("Rozmiar instancji")
plt.ylabel("Czas [s]")
plt.title("Czasy wykonania poszczególnych instancji (skala liniowa)")
plt.grid(True, alpha=0.3)
plt.legend()
plot2_path = os.path.join(OUTPUT_DIR, "instance_points.pdf")
plt.savefig(plot2_path)
plt.close()

# Wykres 3: Wszystkie instancje (Punkty, Skala logarytmiczna) + ETYKIETY
plt.figure(figsize=FIGSIZE)
for alg in ALGORITHMS:
    subset = df_instance_avg[df_instance_avg["algorithm"] == alg]
    plt.scatter(subset["instance_size"], subset["avg_time_seconds"],
                label=ALGORITHM_DISPLAY_NAMES[alg], color=ALGORITHM_COLORS[alg], alpha=0.6)

    # Dodawanie nazw instancji na skali logarytmicznej
    for _, row in subset.iterrows():
        plt.text(row["instance_size"], row["avg_time_seconds"], str(row["instance_name"]),
                 fontsize=8, va="bottom", ha="center", rotation=45, alpha=0.7)

plt.yscale("log")
plt.xlabel("Rozmiar instancji")
plt.ylabel("Czas [s] (log)")
plt.title("Czasy wykonania poszczególnych instancji (skala logarytmiczna)")
plt.grid(True, which="both", ls="--", alpha=0.3)
plt.legend()
plot3_path = os.path.join(OUTPUT_DIR, "instance_points_log.pdf")
plt.savefig(plot3_path)
plt.close()

# Wykres 4: Średni czas (Log)
plt.figure(figsize=FIGSIZE)
for alg in ALGORITHMS:
    subset = df_size_avg[df_size_avg["algorithm"] == alg].sort_values("instance_size")
    plt.plot(subset["instance_size"], subset["avg_time_seconds"], marker="o",
             label=ALGORITHM_DISPLAY_NAMES[alg], color=ALGORITHM_COLORS[alg])
plt.yscale("log")
plt.xlabel("Rozmiar instancji");
plt.ylabel("Średni czas [s] (log)");
plt.grid(True, which="both", alpha=0.3);
plt.legend()
plt.xticks(rotation=0) #etykiety na 0* zeby nie byly obrocoen
plot4_path = os.path.join(OUTPUT_DIR, "avg_time_vs_size_log.pdf")
plt.savefig(plot4_path)
plt.close()

# ============================================================
# INFO KOŃCOWE
# ============================================================

print("\nEksport zakończony sukcesem:")
print(f"- CSV:   {csv_path}")
print(f"- LaTeX: {latex_path}")
print(f"- Wykresy w folderze: {OUTPUT_DIR}")

# ============================================================
# ANALIZA MATEMATYCZNA TRENDÓW
# ============================================================

print("\n" + "=" * 50)
print("ANALIZA ZŁOŻONOŚCI WYKŁADNICZEJ (Trend: y = C * k^n)")
print("=" * 50)

for alg in ALGORITHMS:
    subset = df_size_avg[df_size_avg["algorithm"] == alg].sort_values("instance_size")
    valid_data = subset[subset["avg_time_seconds"] > 0].dropna()

    x = valid_data["instance_size"].values
    y = valid_data["avg_time_seconds"].values

    if len(x) > 1:
        # Regresja liniowa na logarytmach: ln(y) = a*n + ln(C)
        coeffs = np.polyfit(x, np.log(y), 1)
        a = coeffs[0]
        ln_C = coeffs[1]

        # Wykładnik bazy k = e^a
        # Czas rośnie k-krotnie przy każdym n+1
        k = np.exp(a)

        display_name = ALGORITHM_DISPLAY_NAMES[alg]
        print(f"\nAlgorytm: {display_name}")
        print(f"  Równanie: t(n) = {np.exp(ln_C):.2e} * {k:.3f}^n")
        print(f"  Współczynnik wzrostu (k): {k:.3f}")
        print(f"  Interpretacja: Każdy kolejny wierzchołek wydłuża czas o ok. {((k - 1) * 100):.1f}%")
    else:
        print(f"\nAlgorytm: {ALGORITHM_DISPLAY_NAMES[alg]}")
        print("  Brak wystarczającej liczby danych do wyznaczenia trendu.")

print("=" * 50)