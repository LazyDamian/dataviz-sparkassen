import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter

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


    # --- 1. DEFINITION DER ÜBERKATEGORIEN MIT ZUORDNUNG ---
    kategorien_gruppen = {
        "Privater_Wohlstand": {
            "cols": ["Einzelhandelsrelevante Kaufkraft", "Haushalte mit hohem Einkommen", "Medianeinkommen"],
            "color": "#1a4a7c",
            "label": "Finanzkraft & Wohlstand",
            "beschreibung": "Kaufkraft, Hohe Einkommen, Median-Gehalt"
        },
        "Markt_Wirtschaftskraft": {
            "cols": ["Einwohnerdichte", "Beschäftigtendichte (AO)",
                     "Bruttoinlandsprodukt je Einwohner in Kaufkraftstandards (KKS)"],
            "color": "#2a9d8f",
            "label": "Wirtschaftsaktivität & Dichte",
            "beschreibung": "Einwohner- & Jobdichte, BIP (KKS)"
        },
        "Mobilitaet": {
            "cols": ["Pkw-Dichte"],
            "color": "#457b9d",
            "label": "Mobilität & Infrastruktur",
            "beschreibung": "Pkw-Dichte pro 1000 Einwohner"
        },
        "Soziale_Stabilitaet": {
            "cols": ["Arbeitslosenquote", "Haushalte mit niedrigem Einkommen"],
            "color": "#e67e22",
            "label": "Soziale Stabilität (Risiko-Check)",
            "beschreibung": "Arbeitslosigkeit, Niedrige Einkommen (Invertiert)"
        }
    }

    import matplotlib.pyplot as plt
    import seaborn as sns
    import pandas as pd
    from collections import Counter

    # --- 0. GRUNDEINSTELLUNGEN ---
    plt.style.use('seaborn-v0_8-white')

    # Definition der individuellen Farb-Gradients (Dunkel nach Hell)
    # Der erste Wert in der Liste ist für Platz 1 (der oberste Balken)
    gradients = {
        "Wohlstand": ["#08306b", "#2171b5", "#4292c6", "#6baed6", "#9ecae1"],  # Deep Blue Gradient
        "Wirtschaft": ["#00441b", "#238b45", "#41ab5d", "#74c476", "#a1d99b"],  # Forest Green Gradient
        "Mobil": ["#4d004b", "#810f7c", "#88419d", "#8c6bb1", "#8c96c6"],  # Purple/Indigo Gradient
        "Stabil": ["#7f2704", "#a63603", "#d94801", "#f16913", "#fd8d3c"],  # Deep Orange/Rust Gradient
        "Allrounder": ["#b8860b", "#daa520", "#f4c430", "#ffd700"]  # Gold/Metallic Gradient
    }

    # --- 1. PLOT: PRIVATER WOHLSTAND ---
    plt.figure(figsize=(10, 6))
    group_name = "Temp_Score_Wohlstand"
    cols_w = ["Einzelhandelsrelevante Kaufkraft", "Haushalte mit hohem Einkommen", "Medianeinkommen"]
    df_ranking[group_name] = df_ranking[[f"Score_{c}" for c in cols_w if f"Score_{c}" in df_ranking.columns]].mean(
        axis=1)

    top_5 = df_ranking.sort_values(by=group_name).tail(5)
    bars = plt.barh(top_5["Name"], top_5[group_name], color=gradients["Wohlstand"][::-1], height=0.6)

    plt.title("FINANZKRAFT DER HAUSHALTE", fontsize=16, fontweight='bold', color="#08306b", loc='left', pad=20)
    plt.text(0, 1.02, "Faktoren: Kaufkraft, Hohe Einkommen, Medianeinkommen", transform=plt.gca().transAxes,
             color='gray', fontsize=10)

    for bar in bars:
        plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.1f} Pkt.', va='center',
                 fontweight='bold', color="#08306b")

    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.savefig("Plot_1_Wohlstand.png", dpi=300)
    plt.show()

    # --- 2. PLOT: WIRTSCHAFTSKRAFT & DICHTE ---
    plt.figure(figsize=(10, 6))
    group_name = "Temp_Score_Wirtschaft"
    cols_wi = ["Einwohnerdichte", "Beschäftigtendichte (AO)",
               "Bruttoinlandsprodukt je Einwohner in Kaufkraftstandards (KKS)"]
    df_ranking[group_name] = df_ranking[[f"Score_{c}" for c in cols_wi if f"Score_{c}" in df_ranking.columns]].mean(
        axis=1)

    top_5 = df_ranking.sort_values(by=group_name).tail(5)
    bars = plt.barh(top_5["Name"], top_5[group_name], color=gradients["Wirtschaft"][::-1], height=0.6)

    plt.title("WIRTSCHAFTLICHE AKTIVITÄT & DICHTE", fontsize=16, fontweight='bold', color="#00441b", loc='left', pad=20)
    plt.text(0, 1.02, "Faktoren: Jobdichte, Einwohnerdichte, BIP pro Kopf", transform=plt.gca().transAxes, color='gray',
             fontsize=10)

    for bar in bars:
        plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.1f} Pkt.', va='center',
                 fontweight='bold', color="#00441b")

    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.savefig("Plot_2_Wirtschaft.png", dpi=300)
    plt.show()


    # --- 3. PLOT: MOBILITÄT & INFRASTRUKTUR (GRAU & ELECTRIC BLUE) ---
    plt.figure(figsize=(10, 6))
    group_name = "Temp_Score_Mobil"
    cols_mobil = ["Pkw-Dichte"]
    df_ranking[group_name] = df_ranking[[f"Score_{c}" for c in cols_mobil if f"Score_{c}" in df_ranking.columns]].mean(
        axis=1)

    top_5_m = df_ranking.sort_values(by=group_name).tail(5)
    colors_m = ["#caa3ef", "#b17be3", "#924ed1", "#54007c", "#46005f"]  # lila Highlight

    bars_m = plt.barh(top_5_m["Name"], top_5_m[group_name], color=colors_m, height=0.6, edgecolor="#2c3e50",
                      linewidth=0.5)
    plt.title("MOBILITÄT & INFRASTRUKTUR", fontsize=16, fontweight='bold', color="#2c3e50", loc='left', pad=20)
    plt.text(0, 1.02, "Faktor: Pkw-Dichte pro 1.000 Einwohner", transform=plt.gca().transAxes, color='gray',
             fontsize=10)

    for bar in bars_m:
        plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.1f} Pkt.',
                 va='center', fontweight='bold', color="#4d0092")

    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.savefig("Plot_3_Mobilitaet.png", dpi=300)
    plt.show()

    # --- 4. PLOT: SOZIALE STABILITÄT (ERDTÖNE & ORANGE) ---
    plt.figure(figsize=(10, 6))
    group_name = "Temp_Score_Stabil"
    cols_stabil = ["Arbeitslosenquote", "Haushalte mit niedrigem Einkommen"]
    df_ranking[group_name] = df_ranking[[f"Score_{c}" for c in cols_stabil if f"Score_{c}" in df_ranking.columns]].mean(
        axis=1)

    top_5_s = df_ranking.sort_values(by=group_name).tail(5)
    colors_s = ["#db9c60", "#ae794b", "#976841", "#6a452c", "#3d2217"]  # Braun & Orange Highlight

    bars_s = plt.barh(top_5_s["Name"], top_5_s[group_name], color=colors_s, height=0.6, edgecolor="#2c3e50",
                      linewidth=0.5)
    plt.title("SOZIALE STABILITÄT (RISIKO-MINIMIERUNG)", fontsize=16, fontweight='bold', color="#3d2217", loc='left',
              pad=20)
    plt.text(0, 1.02, "Faktoren: Arbeitslosenquote, Niedrige Einkommen (invertiert)", transform=plt.gca().transAxes,
             color='gray', fontsize=10)

    for bar in bars_s:
        plt.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.1f} Pkt.',
                 va='center', fontweight='bold', color="#3d2217")

    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.savefig("Plot_4_Stabilitaet.png", dpi=300)
    plt.show()

    # --- 5. FINALES RANKING: ALLROUNDER KONSISTENZ (ANTHRAZIT & GOLD) ---
    top_auftritte = []
    kategorie_spalten = ["Temp_Score_Wohlstand", "Temp_Score_Wirtschaft", "Temp_Score_Mobil", "Temp_Score_Stabil"]

    for spalte in kategorie_spalten:
        if spalte in df_ranking.columns:
            top_5_namen = df_ranking.sort_values(by=spalte, ascending=False).head(5)["Name"].tolist()
            top_auftritte.extend(top_5_namen)

    auftritte_count = Counter(top_auftritte)
    df_allrounder = pd.DataFrame(auftritte_count.items(), columns=['Name', 'Anzahl']).sort_values(by='Anzahl',
                                                                                                  ascending=True)
    df_allrounder = df_allrounder.tail(4)  # Top 4

    plt.figure(figsize=(11, 6))
    max_count = df_allrounder["Anzahl"].max()
    colors_final = ["#ff4d00"]

    bars_f = plt.barh(df_allrounder["Name"], df_allrounder["Anzahl"], color=colors_final, height=0.5,
                      edgecolor="#2c3e50")
    plt.title('DIE KONSISTENZ-ELITE NORDBAYERNS', fontsize=18, fontweight='bold', color='#2c3e50', loc='left', pad=20)
    plt.text(0, 1.02, 'Anzahl der Top-5-Platzierungen über alle 4 Analyse-Dimensionen', transform=plt.gca().transAxes,
             fontsize=11, color='#7f8c8d')

    for bar in bars_f:
        plt.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2, f' {int(bar.get_width())} von 4 Kategorien',
                 va='center', fontweight='bold', color='#2c3e50', fontsize=12)

    plt.xticks(range(0, 6))
    plt.xlim(0, 5.5)
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.savefig("Plot_5_Final_Allrounder.png", dpi=300)
    plt.show()

    # --- 4. ANGEPASSTES TOP 10 RANKING (MIT HIGHLIGHT-FARBE) ---

    # 1. Identifiziere die Top 4 Allrounder (analog zu deinem Plot 5)
    top_auftritte_list = []
    kategorie_spalten = ["Temp_Score_Wohlstand", "Temp_Score_Wirtschaft", "Temp_Score_Mobil", "Temp_Score_Stabil"]

    for spalte in kategorie_spalten:
        if spalte in df_ranking.columns:
            top_5_namen = df_ranking.sort_values(by=spalte, ascending=False).head(5)["Name"].tolist()
            top_auftritte_list.extend(top_5_namen)

    # Die 4 häufigsten Namen finden
    counts = Counter(top_auftritte_list)
    top_4_allrounder = [name for name, count in counts.most_common(4)]

    # 2. Plotting
    plt.style.use('seaborn-v0_8-white')
    plot_df = top_10.sort_values(by="Gesamt_Index", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))

    # Farblogik: Wenn Name in Top 4 Allroundern -> Orange-Rot, sonst Standard-Blau
    highlight_color = "#ff4d00"  # Die Farbe aus deinem Allrounder-Plot
    standard_color = "#1a4a7c"  # Dein ursprüngliches Blau

    bar_colors = [highlight_color if name in top_4_allrounder else standard_color for name in plot_df["Name"]]

    bars = ax.barh(plot_df["Name"], plot_df["Gesamt_Index"], color=bar_colors, height=0.6)

    ax.set_title(f'Top 10 Standortpotenziale Nordbayern ({latest_year})\n',
                 fontsize=18, fontweight='bold', loc='left')
    ax.set_xlabel('Gesamt-Potenzial (Score 0-100)')
    ax.set_xlim(0, 115)  # Etwas mehr Platz für die Text-Labels

    # Untertitel zur Erklärung der Farben
    ax.text(0, 1.02, f"Markiert in Orange: Die Top 4 'Allrounder' mit der höchsten Konstanz über alle Kategorien",
            transform=ax.transAxes, fontsize=10, color=highlight_color, fontweight='bold')

    for bar, color in zip(bars, bar_colors):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height() / 2,
                f'{width:.1f} Pkt.', va='center', fontweight='bold', color=color)

    sns.despine(left=True, bottom=True)
    ax.xaxis.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()

    plt.savefig(f"Ranking_Gesamt_Highlighted_{latest_year}.png", dpi=300, bbox_inches="tight")
    plt.show()

    print("Alle 5 Visualisierungen wurden erfolgreich als PNG gespeichert.")

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