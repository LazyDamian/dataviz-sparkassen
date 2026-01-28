"""
Projekt: SupplyScore - Analyse der regionalen Bankenversorgung
Beschreibung: Dieses Skript analysiert sozioökonomische Daten (INKAR), berechnet
              Versorgungsindizes für ausgewählte Städte in Nordbayern und visualisiert
              Marktpotenziale sowie Sättigungseffekte.
Output: Generiert 5 Abbildungen im Ordner 'figures/'.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from matplotlib.lines import Line2D
from adjustText import adjust_text

# ==========================================
# 1. KONFIGURATION UND DESIGN-SETUP
# ==========================================
output_dir = Path("figures")
output_dir.mkdir(parents=True, exist_ok=True)

# Globales Design-Thema für Plots setzen
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 11,
    'font.weight': 'bold',
    'axes.labelweight': 'bold',
    'axes.titleweight': 'bold',
    'figure.titleweight': 'bold',
    'text.color': '#222222',
    'axes.labelcolor': '#444444',
    'xtick.color': '#444444',
    'ytick.color': '#444444'
})

# ==========================================
# 2. DATENBASIS (CACHE)
# ==========================================
# Manuelle Hinterlegung von Einwohnerzahlen für spezifische Gebietskörperschaften
# (Fallback für fehlende aktuelle CSV-Daten)
einwohner_cache = {
    "Nürnberg": 540000, "Erlangen": 117000, "Fürth": 132000, "Regensburg": 159000,
    "Würzburg": 128000, "Schweinfurt": 55000, "Bamberg": 80000, "Bayreuth": 75000,
    "Coburg": 42000, "Hof": 47000, "Aschaffenburg": 73000, "Ansbach": 43000,
    "Schwabach": 41000, "Amberg": 42000, "Weiden": 43000,
    "Erlangen-Höchstadt": 141000, "Nürnberger Land": 173000, "Fürth, Landkreis": 120000,
    "Main-Spessart": 126000, "Roth": 129000, "Forchheim": 118000, "Haßberge": 85000,
    "Kitzingen": 94000, "Kronach": 66000, "Tirschenreuth": 72000, "Wunsiedel": 71000,
    "Lichtenfels": 67000, "Kulmbach": 72000, "Regensburg, Landkreis": 200000,
    "Würzburg, Landkreis": 166000, "Bamberg, Landkreis": 150000
}

# Manuelle Erfassung der Wettbewerbssituation (Anzahl Filialen)
wettbewerb_cache = {
    "Nürnberg": 190, "Erlangen": 50, "Fürth": 45, "Regensburg": 70, "Würzburg": 65,
    "Schweinfurt": 40, "Bamberg": 42, "Bayreuth": 38, "Coburg": 30, "Hof": 25,
    "Aschaffenburg": 40, "Ansbach": 25, "Schwabach": 20,
    "Erlangen-Höchstadt": 30, "Nürnberger Land": 40, "Fürth, Landkreis": 20,
    "Main-Spessart": 25, "Roth": 30, "Forchheim": 25, "Haßberge": 15,
    "Kitzingen": 20, "Kronach": 15, "Tirschenreuth": 12
}


def get_manual_data(name, cache, default):
    """
    Hilfsfunktion zum Abruf manueller Daten aus dem Cache.
    Bereinigt Ortsnamen um Zusätze wie ', Stadt' oder ', Landkreis'.
    """
    clean = str(name).replace(", Stadt", "").replace(", Landkreis", "").strip()
    if clean in cache: return cache[clean]
    for k, v in cache.items():
        if k in clean: return v
    return default


# ==========================================
# 3. DATENIMPORT UND -AUFBEREITUNG
# ==========================================
csv_file_path = Path("data/inkar_bayern_nordbayern.csv")
if not csv_file_path.exists(): csv_file_path = Path("inkar_bayern_nordbayern.csv")

df_raw = pd.read_csv(csv_file_path, sep=",", dtype={"Kennziffer": str})
df_raw["Wert"] = pd.to_numeric(df_raw["Wert"], errors="coerce")

# Definition der relevanten Indikatoren für die Analyse
indikatoren = [
    "Einzelhandelsrelevante Kaufkraft", "Haushalte mit hohem Einkommen", "Medianeinkommen",
    "Einwohnerdichte", "Beschäftigtendichte (AO)", "Bruttoinlandsprodukt je Einwohner in Kaufkraftstandards (KKS)",
    "Pkw-Dichte",
    "Arbeitslosenquote", "Haushalte mit niedrigem Einkommen"
]

# Filterung auf Nordbayern und gewählte Indikatoren
mask = (df_raw["Nordbayern"] == True) & (df_raw["Indikator"].isin(indikatoren))
df = df_raw[mask].copy()

# Ermittlung des Zeitbezugs (Vergleich Aktuell vs. Historisch)
years = sorted(df["Zeitbezug"].unique())
latest_year = years[-1]
past_year = years[0] if len(years) > 5 else years[0]

# Pivotierung der Datenstruktur für Trendanalyse
df_now = df[df["Zeitbezug"] == latest_year].pivot_table(index="Name", columns="Indikator", values="Wert").reset_index()
df_past = df[df["Zeitbezug"] == past_year].pivot_table(index="Name", columns="Indikator", values="Wert").reset_index()
df_trend = pd.merge(df_now, df_past, on="Name", suffixes=("", "_OLD"))

# Berechnung des prozentualen Wachstums (Basis: Medianeinkommen)
if "Medianeinkommen" in df_trend.columns and "Medianeinkommen_OLD" in df_trend.columns:
    df_trend["Wachstum_Prozent"] = ((df_trend["Medianeinkommen"] - df_trend["Medianeinkommen_OLD"]) / df_trend[
        "Medianeinkommen_OLD"]) * 100
else:
    df_trend["Wachstum_Prozent"] = 0

df_trend = df_trend.fillna(0)
# Ergänzung der manuellen Daten aus dem Cache
df_trend["Einwohner"] = df_trend["Name"].apply(lambda x: get_manual_data(x, einwohner_cache, 50000))
df_trend["Filialen"] = df_trend["Name"].apply(lambda x: get_manual_data(x, wettbewerb_cache, 20))


# ==========================================
# 4. SCORING-MODELL UND INDEXIERUNG
# ==========================================
def norm(s, invert=False):
    """
    Min-Max-Normalisierung einer Datenserie auf eine Skala von 0 bis 100.
    Parameter 'invert' kehrt die Logik um (niedriger Wert = hoher Score).
    """
    if s.max() == s.min(): return 0
    if invert: return (s.max() - s) / (s.max() - s.min()) * 100
    return (s - s.min()) / (s.max() - s.min()) * 100


# Normalisierung aller Indikatoren
for col in indikatoren:
    if col in df_trend.columns:
        # Bei Arbeitslosenquote und niedrigen Einkommen ist ein niedriger Wert besser (Invertierung)
        invert = col in ["Arbeitslosenquote", "Haushalte mit niedrigem Einkommen"]
        df_trend[f"S_{col}"] = norm(df_trend[col], invert=invert)


def calc_cat(df, cols):
    """Berechnet den Durchschnittsscore für eine Kategorie basierend auf Indikatoren."""
    valid = [f"S_{c}" for c in cols if f"S_{c}" in df.columns]
    return df[valid].mean(axis=1) if valid else 0


# Aggregation der Indikatoren zu vier Hauptkategorien
df_trend["Cat_Wohlstand"] = calc_cat(df_trend, ["Einzelhandelsrelevante Kaufkraft", "Haushalte mit hohem Einkommen",
                                                "Medianeinkommen"])
df_trend["Cat_Wirtschaft"] = calc_cat(df_trend, ["Einwohnerdichte", "Beschäftigtendichte (AO)",
                                                 "Bruttoinlandsprodukt je Einwohner in Kaufkraftstandards (KKS)"])
df_trend["Cat_Mobilitaet"] = calc_cat(df_trend, ["Pkw-Dichte"])
df_trend["Cat_Stabilitaet"] = calc_cat(df_trend, ["Arbeitslosenquote", "Haushalte mit niedrigem Einkommen"])

# Berechnung spezifischer KPIs für das Marktmodell
df_trend["Versorgung"] = df_trend["Einwohner"] / df_trend["Filialen"]  # Einwohner pro Filiale
if "Einzelhandelsrelevante Kaufkraft" in df_trend.columns:
    df_trend["Marktvolumen_Mio"] = (df_trend["Einzelhandelsrelevante Kaufkraft"] * df_trend["Einwohner"]) / 1_000_000
else:
    df_trend["Marktvolumen_Mio"] = df_trend["Einwohner"] * 25000 / 1_000_000
df_trend["Risiko"] = df_trend["Arbeitslosenquote"] if "Arbeitslosenquote" in df_trend.columns else 3.0

# Sub-Scores für den Hunter-Index
df_trend["Score_Hunger"] = norm(df_trend["Versorgung"])
df_trend["Score_Geld"] = norm(df_trend["Marktvolumen_Mio"])
df_trend["Score_Security"] = norm(df_trend["Risiko"], invert=True)
df_trend["Score_Trend"] = norm(df_trend["Wachstum_Prozent"])

# Gesamtberechnung Hunter-Index (gewichteter Durchschnitt)
df_trend["Hunter_Index"] = (
                                   df_trend["Score_Hunger"] * 2.0 +
                                   df_trend["Score_Trend"] * 1.5 +
                                   df_trend["Score_Security"] * 1.0 +
                                   df_trend["Score_Geld"] * 0.5
                           ) / 5.0

# --- Index Vorher (Strukturelles Potenzial) ---
df_trend["Index_Vorher"] = (df_trend["Cat_Wohlstand"] + df_trend["Cat_Wirtschaft"] + df_trend["Cat_Mobilitaet"] +
                            df_trend["Cat_Stabilitaet"]) / 4

# --- Index Nachher (Einbeziehung Sättigung/Bankdichte) ---
df_trend["Dichte"] = df_trend["Filialen"] / df_trend["Einwohner"]
df_trend["Score_Penalty"] = norm(df_trend["Dichte"])
straf_faktor = 0.25
df_trend["Index_Nachher"] = df_trend["Index_Vorher"] - (df_trend["Score_Penalty"] * straf_faktor)

# ==========================================
# 5. GLOBALE DATENSELEKTION
# ==========================================
# Ausschluss definierter Städte (Blacklist)
blacklist = ["Schweinfurt, Stadt"]
df_clean = df_trend[~df_trend["Name"].isin(blacklist)].copy()

# Selektion der Top 8 Städte basierend auf dem strukturellen Index
# Diese Auswahl dient als konsistente Basis für alle Visualisierungen
top_8_global = df_clean.sort_values(by="Index_Vorher", ascending=False).head(8).copy()

# =============================================================================
# VISUALISIERUNG 1: ANALYSE DER BANKDICHTE (LOLLIPOP CHART)
# =============================================================================
plt.figure(figsize=(14, 9))

# Datenvorbereitung
plot_radar = top_8_global.copy()

# Metrik: Einwohner pro Bank (Hoher Wert = Unterversorgung/Potenzial)
plot_radar["Ew_pro_Bank"] = plot_radar["Einwohner"] / plot_radar["Filialen"]

# Berechnung des Durchschnitts als Referenzlinie
avg_ew_pro_bank = plot_radar["Ew_pro_Bank"].mean()

# Sortierung für treppenförmige Darstellung
plot_radar = plot_radar.sort_values("Ew_pro_Bank", ascending=True)

# Farbkodierung basierend auf Durchschnitt:
# Grün = Überdurchschnittlich viele Einwohner/Filiale (Potenzial)
# Rot = Unterdurchschnittlich viele Einwohner/Filiale (Sättigung)
colors = ['#2ca02c' if x < avg_ew_pro_bank else '#d62728' for x in plot_radar["Ew_pro_Bank"]]

# Plot erstellen (Lollipop Style)
plt.hlines(y=plot_radar["Name"], xmin=avg_ew_pro_bank, xmax=plot_radar["Ew_pro_Bank"], color=colors, alpha=0.8,
           linewidth=6)
plt.scatter(plot_radar["Ew_pro_Bank"], plot_radar["Name"], color=colors, s=150, alpha=1, zorder=3)

# Referenzlinie Durchschnitt
plt.axvline(x=avg_ew_pro_bank, color='#333333', linestyle='-', linewidth=2)

# Beschriftung der Datenpunkte
for i, row in plot_radar.iterrows():
    val = row["Ew_pro_Bank"]
    offset = 100  # Textabstand

    if val < avg_ew_pro_bank:  # Beschriftung links (Rot)
        ha = 'right'
        txt_pos = val - offset
    else:  # Beschriftung rechts (Grün)
        ha = 'left'
        txt_pos = val + offset

# Layout und Labels
plt.title(f"BANKDICHTE", pad=25, fontsize=20)
plt.xlabel("← NIEDRIGE BANKDICHTE (HUNGRIG/GRÜN)        |       HOHE BANKDICHTE (GESÄTTIGT/ROT) →",
           fontweight='bold', fontsize=14, labelpad=15, ha='right', x=0.96, y=-0.7)

# Fußnote zur Einheit
plt.gca().text(
    x=-0.13, y=-0.12,
    s="Einheit: Einwohner pro Bankfiliale",
    transform=plt.gca().transAxes,
    ha='left', fontsize=15, color='#333333'
)

plt.yticks(fontsize=14, fontweight='bold', color='#222222')
# Durchschnittswert annotieren
plt.text(avg_ew_pro_bank, -0.8, f"Ø {int(avg_ew_pro_bank)}", ha='center', fontweight='bold', color='#3a2a22', fontsize=18)

plt.grid(axis='x', alpha=0.5, linestyle='--')
plt.tight_layout()
plt.savefig(output_dir / "1_Bankdichte.png", dpi=300)

# =============================================================================
# VISUALISIERUNG 2: MARKTMATRIX (BUBBLE PLOT)
# =============================================================================
plt.figure(figsize=(14, 10))

plot_data = top_8_global.copy()


def get_color_group(name):
    """Weist Städten basierend auf Namen eine Farbgruppe zu (Highlight vs. Rest)."""
    name_lower = str(name).lower()
    if "aschaffenburg" in name_lower or "miltenberg" in name_lower or "fürth" in name_lower:
        return "Highlight"  # Grün
    return "Rest"  # Rot


plot_data["ColorGroup"] = plot_data["Name"].apply(get_color_group)
custom_palette = {"Highlight": "#2ca02c", "Rest": "#d62728"}

# Bubble Plot erstellen
sns.scatterplot(
    data=plot_data,
    x="Score_Security", y="Marktvolumen_Mio",
    size="Versorgung", sizes=(300, 3000),
    hue="ColorGroup", palette=custom_palette, legend=False,
    alpha=0.75, edgecolor="black"
)

# Intelligente Beschriftung (Vermeidung von Überlappungen)
sorted_points = plot_data.sort_values("Marktvolumen_Mio")
occupied_y = []

for i, row in sorted_points.iterrows():
    x, y = row.Score_Security, row.Marktvolumen_Mio
    name = row.Name
    text_x = x + (plot_data["Score_Security"].max() - plot_data["Score_Security"].min()) * 0.02
    text_y = 0.5 * y + 0.3 * plot_data["Marktvolumen_Mio"].max()

    # Kollisionsprüfung für Y-Positionen
    collision = True
    while collision:
        collision = False
        for occ in occupied_y:
            if abs(text_y - occ) < (plot_data["Marktvolumen_Mio"].max() * 0.05):
                text_y += (plot_data["Marktvolumen_Mio"].max() * 0.06)
                collision = True
    occupied_y.append(text_y)

    plt.annotate(
        name, xy=(x, y), xytext=(text_x, text_y), textcoords='data',
        fontsize=18, weight='bold', color='#222222',
        arrowprops=dict(arrowstyle="-|>", color='#444444', lw=1.5, connectionstyle="arc3,rad=0.1"),
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#cccccc", alpha=0.9)
    )

plt.title("Marktvolumen & Soziale Sicherheit", pad=20, fontsize=22)
plt.xlabel("Soziale Sicherheit", fontsize=16, weight='bold')
plt.ylabel("Marktvolumen (Mio. €)", fontsize=16, weight='bold')
plt.grid(True, linestyle='--', alpha=0.5)

# Legenden-Box im Plot
plt.text(plot_data["Score_Security"].min(), plot_data["Marktvolumen_Mio"].max(),
         "Grün = Niedrige Konkurrenz\nRot = Hohe Konkurrenz",
         ha='left', va='top', fontsize=15, bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray'))

plt.tight_layout()
plt.savefig(output_dir / "2_Markvolumen_Sicherheit.png", dpi=300)

# =============================================================================
# VISUALISIERUNG 3: STÄRKEN- UND SCHWÄCHENPROFIL (HEATMAP)
# =============================================================================
from matplotlib.colors import LinearSegmentedColormap

plt.figure(figsize=(14, 9))

plot_heatmap = top_8_global.sort_values(by="Index_Vorher", ascending=False).copy()
plot_heatmap = plot_heatmap.set_index("Name")

# Datenselektion und Umbenennung für Anzeige
hm_data = plot_heatmap[["Cat_Mobilitaet", "Cat_Stabilitaet", "Cat_Wirtschaft", "Cat_Wohlstand"]]
hm_data.columns = ["Mobilität & Infra", "Soziale Stabilität", "Wirtschaftsaktivität", "Finanzkraft & Wohlstand"]

# Definition der Kategorie-Farben (analog zu Plot 4a)
column_colors = ["#3498db", "#9b59b6", "#f1c40f", "#2ecc71"]

# Technische Umsetzung: Überlagerung von vier separaten Heatmaps
ax = plt.gca()

for i, col_name in enumerate(hm_data.columns):
    # Erstellung einer benutzerdefinierten Colormap (Weiß -> Zielfarbe)
    cmap = LinearSegmentedColormap.from_list(f"custom_{i}", ["white", column_colors[i]])

    # Maskierung aller anderen Spalten
    mask = pd.DataFrame(True, index=hm_data.index, columns=hm_data.columns)
    mask[col_name] = False

    # Plot der Einzelspalte
    sns.heatmap(
        hm_data,
        mask=mask,
        cmap=cmap,
        ax=ax,
        annot=True,
        fmt=".0f",
        linewidths=2,
        linecolor='white',
        cbar=False,
        annot_kws={"size": 13, "weight": "bold"}
    )

plt.title("STÄRKEN-PROFILE NACH KATEGORIEN", pad=20, fontsize=18)
plt.ylabel("")
plt.xticks(fontsize=16, weight='bold')
plt.yticks(fontsize=16, weight='bold', rotation=0)
plt.tight_layout()
plt.savefig(output_dir / "3_Stärken_Profil.png", dpi=300)

# =============================================================================
# VISUALISIERUNG 4a: ZUSAMMENSETZUNG DES GESAMT-SCORES (STACKED BAR)
# =============================================================================
plt.figure(figsize=(14, 9))

# Datenvorbereitung
plot_data_4a = top_8_global.sort_values(by="Index_Vorher", ascending=True).copy()

# Definition der Kategorien und Farben
cols_heatmap = ["Cat_Mobilitaet", "Cat_Stabilitaet", "Cat_Wirtschaft", "Cat_Wohlstand"]
labels = ["Mobilität", "Stabilität", "Wirtschaft", "Finanzkraft"]
colors = ["#3498db", "#9b59b6", "#f1c40f", "#2ecc71"]

df_raw_scores = plot_data_4a[cols_heatmap].copy()
df_raw_scores.columns = labels

# Skalierung für Plot (Durchschnittsbildung statt Summe)
df_plot = df_raw_scores / 4

# Erstellung des Stacked Bar Charts
ax = df_plot.plot(
    kind='barh',
    stacked=True,
    figsize=(14, 9),
    color=colors,
    width=0.75,
    edgecolor='white',
    linewidth=1
)

# Beschriftung der Segmente (Prozente und absolute Scores)
for col_idx, container in enumerate(ax.containers):
    cat_name = labels[col_idx]

    for i, rect in enumerate(container):
        city_name = df_plot.index[i]
        real_score = df_raw_scores.loc[city_name, cat_name]
        total_sum = df_raw_scores.loc[city_name].sum()

        # Prozentanteil berechnen
        if total_sum > 0:
            pct = (real_score / total_sum) * 100
        else:
            pct = 0

        # Beschriftung nur bei ausreichender Balkenbreite
        if pct > 4:
            face_color = rect.get_facecolor()
            r, g, b = face_color[:3]
            luminance = (0.299 * r + 0.587 * g + 0.114 * b)
            # Automatische Kontrastfarbe für Text
            if luminance > 0.55:
                text_color = '#222222'
            else:
                text_color = 'white'

            label_text = f"{int(round(pct))}%"

            ax.text(
                rect.get_x() + rect.get_width() / 2,
                rect.get_y() + rect.get_height() / 2,
                label_text,
                ha='center', va='center',
                color=text_color, fontweight='bold', fontsize=15
            )

plt.title("Der Gesamt-Score: Zusammensetzung nach Kategorien", pad=20, fontsize=20, color='#333333')
plt.xlabel("Index-Punkte (Durchschnitt aller Kategorien)", fontsize=18, fontweight='bold', color='#555555')
plt.ylabel("")

sns.despine(left=True, bottom=False)
plt.grid(axis='x', linestyle='-', alpha=0.15, color='black')
plt.grid(visible=False, axis='y')
plt.yticks(ticks=range(len(plot_data_4a)), labels=plot_data_4a["Name"], fontsize=18, fontweight='bold', color='#222222')
plt.xticks(color='#555555')

plt.legend(
    labels,
    loc='upper center',
    bbox_to_anchor=(0.5, -0.12),
    ncol=4,
    frameon=False,
    fontsize=15,
    handlelength=3,
    handleheight=2
)

plt.tight_layout()
plt.savefig(output_dir / "4a_Gesamt_Score_Kateg.png", dpi=300)

# =============================================================================
# VISUALISIERUNG 4b: EINFLUSS DER VERSORGUNGSDICHTE (VORHER/NACHHER)
# =============================================================================
plt.figure(figsize=(14, 9))

plot_data_4b = top_8_global.copy()

# Berechnung der Abweichung vom Referenzwert
plot_data_4b["Ew_pro_Bank"] = plot_data_4b["Einwohner"] / plot_data_4b["Filialen"]
ref_avg = 3792  # Referenzwert (Durchschnitt)
plot_data_4b["Abweichung"] = plot_data_4b["Ew_pro_Bank"] - ref_avg

# Anpassung des Scores basierend auf der Abweichung
# Logik: Hohe Einwohnerzahl pro Bank = Unterversorgung = Bonus (Potenzial)
#        Niedrige Einwohnerzahl pro Bank = Überversorgung = Malus (Sättigung)
scaling_factor = 0.004
plot_data_4b["Index_Nachher"] = plot_data_4b["Index_Vorher"] - (plot_data_4b["Abweichung"] * scaling_factor)

plot_data_4b = plot_data_4b.sort_values(by="Index_Nachher", ascending=True)
my_range = range(1, len(plot_data_4b.index) + 1)

# Farbzuweisung für Verbesserung (Grün) vs. Verschlechterung (Rot)
colors_nachher = []
for i, row in plot_data_4b.iterrows():
    if row["Index_Nachher"] > row["Index_Vorher"]:
        colors_nachher.append('#2ca02c') # Grün (Bonus)
    else:
        colors_nachher.append('#d62728') # Rot (Abzug)

# Plotten der Rangveränderung
plt.hlines(y=my_range, xmin=plot_data_4b['Index_Nachher'], xmax=plot_data_4b['Index_Vorher'],
           color='grey', alpha=0.4, linewidth=2.5)
plt.scatter(plot_data_4b['Index_Vorher'], my_range, color='grey', alpha=0.65, s=200,
            label='Score ohne Einberechnung', zorder=4)
plt.scatter(plot_data_4b['Index_Nachher'], my_range, c=colors_nachher, alpha=0.65, s=200, zorder=5)

# Legende für den Plot
plt.scatter([], [], c='#2ca02c', s=200, label='Bonus (Schlechte Versorgung / Wenig Banken)')
plt.scatter([], [], c='#d62728', s=200, label='Strafe (Gute Versorgung / Viele Banken)')

# Indikatorpfeile für Score-Veränderung
for i in range(len(plot_data_4b)):
    row = plot_data_4b.iloc[i]
    if abs(row['Index_Vorher'] - row['Index_Nachher']) > 0.5:
        plt.annotate('',
                     xy=(row['Index_Nachher'], i+1),
                     xytext=(row['Index_Vorher'], i+1),
                     arrowprops=dict(arrowstyle='-> ', color='black', lw=2.5))

plt.yticks(my_range, plot_data_4b['Name'], fontsize=16, fontweight='bold', color='#222222')
plt.title("FINALES ERGEBNIS: PUNKTZAHL NACH INTEGRIERUNG DER BANKDICHTE", pad=20, fontsize=18)
plt.xlabel("Gesamt-Score ", fontsize=15, fontweight='bold')
plt.legend(loc='lower right', frameon=True, fontsize=15)
plt.grid(axis='x', linestyle='--', alpha=0.5)

# Erläuterungsbox zur Methodik
plt.text(
    x=0.02, y=0.98,
    s=f"Referenz: Ø {ref_avg} Einwohner pro Bank.\n• (< {ref_avg}) = Hohe Dichte = Bonus (Grün)"
      f"\n• (> {ref_avg}) = Niedrige Dichte = Strafe (Rot)",
    transform=plt.gca().transAxes,
    ha='left', va='top',
    fontsize=16,
    bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'),
    zorder=20
)

plt.tight_layout()
plt.savefig(output_dir / "4b_Finaler_Score_Bankdichte.png", dpi=300)