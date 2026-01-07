import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --- 1. SETTINGS & PFADE ---
csv_file_path = Path(r"data/inkar_bayern_nordbayern.csv")

# Auswahl der relevanten Indikatoren
pos_indikatoren = [
    "Einzelhandelsrelevante Kaufkraft",
    "Haushalte mit hohem Einkommen",
    "Medianeinkommen",
    "Einwohnerdichte",
    "Beschäftigtendichte (AO)",
    "Bruttoinlandsprodukt je Einwohner in Kaufkraftstandards (KKS)",
    "Pkw-Dichte"
]
neg_indikatoren = [
    "Arbeitslosenquote",
    "Haushalte mit niedrigem Einkommen"
]
alle_indikatoren = pos_indikatoren + neg_indikatoren

# Einheiten-Mapping für die Tabelle
einheiten = {
    "Einzelhandelsrelevante Kaufkraft": "€/Einw.",
    "Haushalte mit hohem Einkommen": "%",
    "Medianeinkommen": "€",
    "Einwohnerdichte": "Einw./km²",
    "Beschäftigtendichte (AO)": "Jobs/km²",
    "Bruttoinlandsprodukt je Einwohner in Kaufkraftstandards (KKS)": "KKS",
    "Pkw-Dichte": "Pkw/1000",
    "Arbeitslosenquote": "%",
    "Haushalte mit niedrigem Einkommen": "%"
}

if not csv_file_path.exists():
    print(f"Datei nicht gefunden: {csv_file_path}")
else:
    # --- 2. DATEN LADEN & FILTERN ---
    df_raw = pd.read_csv(csv_file_path, sep=",", dtype={"Kennziffer": str})

    # Filter auf Nordbayern und Indikatoren
    mask = (df_raw["Nordbayern"] == True) & (df_raw["Indikator"].isin(alle_indikatoren))
    df_filtered = df_raw[mask].copy()
    df_filtered["Wert"] = pd.to_numeric(df_filtered["Wert"], errors="coerce")

    latest_year = df_filtered["Zeitbezug"].max()

    df_pivot = df_filtered[df_filtered["Zeitbezug"] == latest_year].pivot_table(
        index=["Name"], columns="Indikator", values="Wert"
    ).reset_index()

    # --- 3. SCORING ---
    df_ranking = df_pivot.copy()
    score_cols = []

    for col in pos_indikatoren:
        if col in df_ranking.columns:
            c_min, c_max = df_ranking[col].min(), df_ranking[col].max()
            df_ranking[f"Score_{col}"] = (df_ranking[col] - c_min) / (c_max - c_min) * 100
            score_cols.append(f"Score_{col}")

    for col in neg_indikatoren:
        if col in df_ranking.columns:
            c_min, c_max = df_ranking[col].min(), df_ranking[col].max()
            df_ranking[f"Score_{col}"] = (c_max - df_ranking[col]) / (c_max - c_min) * 100
            score_cols.append(f"Score_{col}")

    df_ranking["Gesamt_Index"] = df_ranking[score_cols].mean(axis=1)
    top_10 = df_ranking.sort_values(by="Gesamt_Index", ascending=False).head(10).copy()
    top_10.insert(0, 'Platz', range(1, 11))

    # --- 4. CLEAN VISUALISIERUNG (NUR GESAMT SCORE) ---
    plt.style.use('seaborn-v0_8-white')
    plot_df = top_10.sort_values(by="Gesamt_Index", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(plot_df["Name"], plot_df["Gesamt_Index"], color="#1a4a7c", height=0.6)

    ax.set_title(f'Top 10 Standortpotenziale Nordbayern ({latest_year})\n',
                 fontsize=18, fontweight='bold', loc='left')
    ax.set_xlabel('Gesamt-Potenzial (Score 0-100)')
    ax.set_xlim(0, 110)

    for bar in bars:
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height() / 2,
                f'{width:.1f} Pkt.', va='center', fontweight='bold', color='#1a4a7c')

    sns.despine(left=True, bottom=True)
    ax.xaxis.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()

    plt.savefig(f"Ranking_Gesamt_{latest_year}.png", dpi=300, bbox_inches="tight")
    plt.show()

    # --- 5. VOLLSTÄNDIGE TABELLE (MIT ALLEN VARIABLEN) ---
    # Hier werden nun alle Indikatoren wieder hinzugefügt
    final_cols = ["Platz", "Name", "Gesamt_Index"] + [c for c in alle_indikatoren if c in top_10.columns]
    report_table = top_10[final_cols].copy()

    # Spaltennamen für die Tabelle verschönern (Einheiten hinzufügen)
    new_headers = []
    for col in report_table.columns:
        if col in einheiten:
            new_headers.append(f"{col} ({einheiten[col]})")
        elif col == "Gesamt_Index":
            new_headers.append("Index (0-100)")
        else:
            new_headers.append(col)

    report_table.columns = new_headers

    print("\n" + "═" * 300)
    print(f" STRATEGISCHER STANDORT-REPORT NORDBAYERN: TOP 10 RANKING (BASIS: {csv_file_path}) ".center(180))
    print("═" * 300)
    pd.options.display.max_columns = None
    pd.options.display.width = 1000
    print(report_table.to_string(index=False, float_format=lambda x: "{:,.1f}".format(x)))
    print("═" * 300)