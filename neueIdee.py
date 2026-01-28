import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from matplotlib.lines import Line2D
from adjustText import adjust_text  # Importieren

# --- 1. SETUP & DESIGN ---
output_dir = Path("figures_final_consistent_top8")
output_dir.mkdir(parents=True, exist_ok=True)

# Design
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

# --- DATENBANKEN ---
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

wettbewerb_cache = {
    "Nürnberg": 190, "Erlangen": 50, "Fürth": 45, "Regensburg": 70, "Würzburg": 65,
    "Schweinfurt": 40, "Bamberg": 42, "Bayreuth": 38, "Coburg": 30, "Hof": 25,
    "Aschaffenburg": 40, "Ansbach": 25, "Schwabach": 20,
    "Erlangen-Höchstadt": 30, "Nürnberger Land": 40, "Fürth, Landkreis": 20,
    "Main-Spessart": 25, "Roth": 30, "Forchheim": 25, "Haßberge": 15,
    "Kitzingen": 20, "Kronach": 15, "Tirschenreuth": 12
}


def get_manual_data(name, cache, default):
    clean = str(name).replace(", Stadt", "").replace(", Landkreis", "").strip()
    if clean in cache: return cache[clean]
    for k, v in cache.items():
        if k in clean: return v
    return default


# --- 2. DATEN LADEN ---
csv_file_path = Path("data/inkar_bayern_nordbayern.csv")
if not csv_file_path.exists(): csv_file_path = Path("inkar_bayern_nordbayern.csv")

df_raw = pd.read_csv(csv_file_path, sep=",", dtype={"Kennziffer": str})
df_raw["Wert"] = pd.to_numeric(df_raw["Wert"], errors="coerce")

indikatoren = [
    "Einzelhandelsrelevante Kaufkraft", "Haushalte mit hohem Einkommen", "Medianeinkommen",
    "Einwohnerdichte", "Beschäftigtendichte (AO)", "Bruttoinlandsprodukt je Einwohner in Kaufkraftstandards (KKS)",
    "Pkw-Dichte",
    "Arbeitslosenquote", "Haushalte mit niedrigem Einkommen"
]

mask = (df_raw["Nordbayern"] == True) & (df_raw["Indikator"].isin(indikatoren))
df = df_raw[mask].copy()

# Zeitbezug
years = sorted(df["Zeitbezug"].unique())
latest_year = years[-1]
past_year = years[0] if len(years) > 5 else years[0]

# Pivot
df_now = df[df["Zeitbezug"] == latest_year].pivot_table(index="Name", columns="Indikator", values="Wert").reset_index()
df_past = df[df["Zeitbezug"] == past_year].pivot_table(index="Name", columns="Indikator", values="Wert").reset_index()
df_trend = pd.merge(df_now, df_past, on="Name", suffixes=("", "_OLD"))

# Wachstum
if "Medianeinkommen" in df_trend.columns and "Medianeinkommen_OLD" in df_trend.columns:
    df_trend["Wachstum_Prozent"] = ((df_trend["Medianeinkommen"] - df_trend["Medianeinkommen_OLD"]) / df_trend[
        "Medianeinkommen_OLD"]) * 100
else:
    df_trend["Wachstum_Prozent"] = 0

df_trend = df_trend.fillna(0)
df_trend["Einwohner"] = df_trend["Name"].apply(lambda x: get_manual_data(x, einwohner_cache, 50000))
df_trend["Filialen"] = df_trend["Name"].apply(lambda x: get_manual_data(x, wettbewerb_cache, 20))


# --- BERECHNUNG SCORES ---
def norm(s, invert=False):
    if s.max() == s.min(): return 0
    if invert: return (s.max() - s) / (s.max() - s.min()) * 100
    return (s - s.min()) / (s.max() - s.min()) * 100


for col in indikatoren:
    if col in df_trend.columns:
        invert = col in ["Arbeitslosenquote", "Haushalte mit niedrigem Einkommen"]
        df_trend[f"S_{col}"] = norm(df_trend[col], invert=invert)


def calc_cat(df, cols):
    valid = [f"S_{c}" for c in cols if f"S_{c}" in df.columns]
    return df[valid].mean(axis=1) if valid else 0


# 4 Kategorien
df_trend["Cat_Wohlstand"] = calc_cat(df_trend, ["Einzelhandelsrelevante Kaufkraft", "Haushalte mit hohem Einkommen",
                                                "Medianeinkommen"])
df_trend["Cat_Wirtschaft"] = calc_cat(df_trend, ["Einwohnerdichte", "Beschäftigtendichte (AO)",
                                                 "Bruttoinlandsprodukt je Einwohner in Kaufkraftstandards (KKS)"])
df_trend["Cat_Mobilitaet"] = calc_cat(df_trend, ["Pkw-Dichte"])
df_trend["Cat_Stabilitaet"] = calc_cat(df_trend, ["Arbeitslosenquote", "Haushalte mit niedrigem Einkommen"])

# Hunter Index
df_trend["Versorgung"] = df_trend["Einwohner"] / df_trend["Filialen"]
if "Einzelhandelsrelevante Kaufkraft" in df_trend.columns:
    df_trend["Marktvolumen_Mio"] = (df_trend["Einzelhandelsrelevante Kaufkraft"] * df_trend["Einwohner"]) / 1_000_000
else:
    df_trend["Marktvolumen_Mio"] = df_trend["Einwohner"] * 25000 / 1_000_000
df_trend["Risiko"] = df_trend["Arbeitslosenquote"] if "Arbeitslosenquote" in df_trend.columns else 3.0

df_trend["Score_Hunger"] = norm(df_trend["Versorgung"])
df_trend["Score_Geld"] = norm(df_trend["Marktvolumen_Mio"])
df_trend["Score_Security"] = norm(df_trend["Risiko"], invert=True)
df_trend["Score_Trend"] = norm(df_trend["Wachstum_Prozent"])

df_trend["Hunter_Index"] = (
                                   df_trend["Score_Hunger"] * 2.0 +
                                   df_trend["Score_Trend"] * 1.5 +
                                   df_trend["Score_Security"] * 1.0 +
                                   df_trend["Score_Geld"] * 0.5
                           ) / 5.0

# --- RANGLISTE (VORHER / NACHHER) ---
df_trend["Index_Vorher"] = (df_trend["Cat_Wohlstand"] + df_trend["Cat_Wirtschaft"] + df_trend["Cat_Mobilitaet"] +
                            df_trend["Cat_Stabilitaet"]) / 4

# Sättigungs-Strafe
df_trend["Dichte"] = df_trend["Filialen"] / df_trend["Einwohner"]
df_trend["Score_Penalty"] = norm(df_trend["Dichte"])
straf_faktor = 0.25
df_trend["Index_Nachher"] = df_trend["Index_Vorher"] - (df_trend["Score_Penalty"] * straf_faktor)

# --- GLOBALE AUSWAHL: DIE TOP 8 STÄDTE ---
# 1. Wir filtern erst die Blacklist ("Schweinfurt, Stadt")
blacklist = ["Schweinfurt, Stadt"]
df_clean = df_trend[~df_trend["Name"].isin(blacklist)].copy()

# 2. Wir wählen die Top 8 basierend auf dem Potenzial (Index_Vorher)
# Das ist unsere "Master-Liste" für ALLE Plots
top_8_global = df_clean.sort_values(by="Index_Vorher", ascending=False).head(8).copy()

# === PLOT 1: SÄTTIGUNGS-RADAR (ABSOLUTE ZAHLEN: EINWOHNER PRO BANK) ===
plt.figure(figsize=(14, 9))

# 1. Datenbasis: Top 8
plot_radar = top_8_global.copy()

# METRIK: EINWOHNER PRO BANK (Je höher, desto besser/hungriger)
plot_radar["Ew_pro_Bank"] = plot_radar["Einwohner"] / plot_radar["Filialen"]

# Durchschnitt berechnen (als Referenzlinie)
avg_ew_pro_bank = plot_radar["Ew_pro_Bank"].mean()

# Sortieren: Damit die Linie schön treppenförmig ist
plot_radar = plot_radar.sort_values("Ew_pro_Bank", ascending=True)

# 2. Farben bestimmen
# Niedrige Zahl (wenig Einwohner pro Bank) = SATT = ROT
# Hohe Zahl (viele Einwohner müssen sich eine Bank teilen) = HUNGRIG = GRÜN
colors = ['#2ca02c' if x < avg_ew_pro_bank else '#d62728' for x in plot_radar["Ew_pro_Bank"]]

# 3. Plotten (Lollipop)
# Linie vom Durchschnittswert zum echten Wert
plt.hlines(y=plot_radar["Name"], xmin=avg_ew_pro_bank, xmax=plot_radar["Ew_pro_Bank"], color=colors, alpha=0.8,
           linewidth=6)
plt.scatter(plot_radar["Ew_pro_Bank"], plot_radar["Name"], color=colors, s=150, alpha=1, zorder=3)

# Durchschnittslinie
plt.axvline(x=avg_ew_pro_bank, color='#333333', linestyle='-', linewidth=2)

# 4. Beschriftung der Werte
for i, row in plot_radar.iterrows():
    val = row["Ew_pro_Bank"]
    # Textpositionierung: Immer etwas außen neben dem Punkt
    offset = 100  # Abstand für Text

    if val < avg_ew_pro_bank:  # Links (Rot)
        ha = 'right'
        txt_pos = val - offset
    else:  # Rechts (Grün)
        ha = 'left'
        txt_pos = val + offset



# 5. Titel & Achsen
plt.title(f"BANKDICHTE", pad=25, fontsize=20)

# Beschriftung oben/unten
plt.xlabel("← NIEDRIGE BANKDICHTE (HUNGRIG/GRÜN)        |       HOHE BANKDICHTE (GESÄTTIGT/ROT) →",
           fontweight='bold', fontsize=14, labelpad=15, ha='right', x=0.96, y=-0.7)

# Zusätzliche Info rechts unten
plt.gca().text(
    x=-0.13, y=-0.12,
    s="Einheit: Einwohner pro Bankfiliale",
    transform=plt.gca().transAxes,
    ha='left', fontsize=15, color='#333333'
)

plt.yticks(fontsize=14, fontweight='bold', color='#222222')
# Durchschnittswert als Text an die Linie schreiben
plt.text(avg_ew_pro_bank, -0.8, f"Ø {int(avg_ew_pro_bank)}", ha='center', fontweight='bold', color='#3a2a22', fontsize=18)

plt.grid(axis='x', alpha=0.5, linestyle='--')
plt.tight_layout()
plt.savefig(output_dir / "1_Bankdichte.png", dpi=300)

# === PLOT 2: GOLDADER-BUBBLES (CUSTOM FARBEN: GRÜN/ROT) ===
plt.figure(figsize=(14, 10))

# Wir nutzen dieselben Daten
plot_data = top_8_global.copy()


# Farbe definieren: Grün für Aschaffenburg/Miltenberg, Rot für den Rest
def get_color_group(name):
    name_lower = str(name).lower()
    # Prüfen auf Aschaffenburg oder Miltenberg (auch mit Tippfehler-Toleranz für "mitten berg")
    if "aschaffenburg" in name_lower or "miltenberg" in name_lower or "fürth" in name_lower:
        return "Highlight"  # Grün
    return "Rest"  # Rot


plot_data["ColorGroup"] = plot_data["Name"].apply(get_color_group)

# Palette festlegen
custom_palette = {"Highlight": "#2ca02c", "Rest": "#d62728"}

# Plotten
sns.scatterplot(
    data=plot_data,
    x="Score_Security", y="Marktvolumen_Mio",
    size="Versorgung", sizes=(300, 3000),
    hue="ColorGroup", palette=custom_palette, legend=False,
    alpha=0.75, edgecolor="black"
)

# --- Beschriftung  ---
sorted_points = plot_data.sort_values("Marktvolumen_Mio")
occupied_y = []

for i, row in sorted_points.iterrows():
    x, y = row.Score_Security, row.Marktvolumen_Mio
    name = row.Name
    text_x = x + (plot_data["Score_Security"].max() - plot_data["Score_Security"].min()) * 0.02
    text_y = 0.5 * y + 0.3 * plot_data["Marktvolumen_Mio"].max()

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

# Kleiner Hinweis zur Legende im Plot
plt.text(plot_data["Score_Security"].min(), plot_data["Marktvolumen_Mio"].max(),
         "Grün = Niedrige Konkurrenz\nRot = Hohe Konkurrenz",
         ha='left', va='top', fontsize=15, bbox=dict(facecolor='white', alpha=0.9, edgecolor='gray'))



plt.tight_layout()
plt.savefig(output_dir / "2_Markvolumen_Sicherheit.png", dpi=300)

# === PLOT 3: HEATMAP (MIT FARBEN AUS PLOT 4a) ===
from matplotlib.colors import LinearSegmentedColormap

plt.figure(figsize=(14, 9))

# Wir nutzen exakt dieselben Top 8, sortiert nach Gesamt-Index (Vorher)
plot_heatmap = top_8_global.sort_values(by="Index_Vorher", ascending=False).copy()
plot_heatmap = plot_heatmap.set_index("Name")

# Spalten auswählen und umbenennen (Reihenfolge merken!)
hm_data = plot_heatmap[["Cat_Mobilitaet", "Cat_Stabilitaet", "Cat_Wirtschaft", "Cat_Wohlstand"]]
hm_data.columns = ["Mobilität & Infra", "Soziale Stabilität", "Wirtschaftsaktivität", "Finanzkraft & Wohlstand"]

# Farben exakt passend zu Plot 4a zuordnen
# Mobilität=Grün, Stabilität=Gelb, Wirtschaft=Lila, Finanzkraft=Blau
column_colors = ["#3498db", "#9b59b6", "#f1c40f", "#2ecc71"]


# Trick: Wir zeichnen 4 Heatmaps übereinander auf dieselbe Achse
ax = plt.gca()

for i, col_name in enumerate(hm_data.columns):
    # 1. Eigene Colormap für diese Spalte erstellen (Weiß -> Ziel-Farbe)
    # Wir nehmen "white" als Start, damit niedrige Werte hell sind
    cmap = LinearSegmentedColormap.from_list(f"custom_{i}", ["white", column_colors[i]])

    # 2. Maske erstellen: Alles maskieren (True) AUẞER der aktuellen Spalte (False)
    # Maskierte Bereiche sind transparent
    mask = pd.DataFrame(True, index=hm_data.index, columns=hm_data.columns)
    mask[col_name] = False

    # 3. Heatmap für diese eine Spalte plotten
    sns.heatmap(
        hm_data,
        mask=mask,  # Nur diese Spalte sichtbar machen
        cmap=cmap,  # Die passende Farbe zur Kategorie
        ax=ax,  # Auf dasselbe Bild zeichnen
        annot=True,  # Zahlen anzeigen
        fmt=".0f",
        linewidths=2,
        linecolor='white',
        cbar=False,  # Keine Farbskala (würde verwirren)
        annot_kws={"size": 13, "weight": "bold"}
    )

plt.title("STÄRKEN-PROFILE NACH KATEGORIEN", pad=20, fontsize=18)
plt.ylabel("")
plt.xticks(fontsize=16, weight='bold')
plt.yticks(fontsize=16, weight='bold', rotation=0)
plt.tight_layout()
plt.savefig(output_dir / "3_Stärken_Profil.png", dpi=300)

# === PLOT 4a: DNA DES ERFOLGS (SYNCHRON MIT HEATMAP) ===
plt.figure(figsize=(14, 9))

# 1. DATEN VORBEREITEN
# Wir nehmen exakt die Top 8 Liste
plot_data_4a = top_8_global.sort_values(by="Index_Vorher", ascending=True).copy()

# Wir definieren die Spalten exakt wie in Plot 3 (Heatmap)
# Reihenfolge: Wohlstand, Wirtschaft, Mobilität, Stabilität
cols_heatmap = ["Cat_Mobilitaet", "Cat_Stabilitaet", "Cat_Wirtschaft", "Cat_Wohlstand"]
labels = ["Mobilität", "Stabilität", "Wirtschaft", "Finanzkraft"]
colors = ["#3498db", "#9b59b6", "#f1c40f", "#2ecc71"]

# Wir erstellen ein DataFrame NUR mit diesen rohen Scores (0-100)
# Das sind exakt die Zahlen, die in der Heatmap stehen.
df_raw_scores = plot_data_4a[cols_heatmap].copy()
df_raw_scores.columns = labels

# 2. PLOT-DATEN BERECHNEN
# Damit der Balken auf der X-Achse den "Durchschnitts-Index" (0-100) anzeigt und nicht die Summe (0-400),
# teilen wir die Werte für die *Darstellung* durch 4.
# Das ändert NICHT die Proportionen (Prozente bleiben gleich).
df_plot = df_raw_scores / 4

# 3. PLOTTEN
ax = df_plot.plot(
    kind='barh',
    stacked=True,
    figsize=(14, 9),
    color=colors,
    width=0.75,
    edgecolor='white',
    linewidth=1
)

# 4. BESCHRIFTUNG (DAS HERZSTÜCK)
# Wir beschriften die Balken basierend auf den ECHTEN Rohdaten (df_raw_scores)
# und der ECHTEN Summe.

for col_idx, container in enumerate(ax.containers):
    # Name der aktuellen Kategorie (z.B. "Wirtschaft")
    cat_name = labels[col_idx]

    for i, rect in enumerate(container):
        # Stadtname holen
        city_name = df_plot.index[i]

        # 1. Den echten Score aus der Heatmap-Datenbasis holen (z.B. 94)
        real_score = df_raw_scores.loc[city_name, cat_name]

        # 2. Die Summe aller 4 Kategorien für diese Stadt berechnen
        total_sum = df_raw_scores.loc[city_name].sum()

        # 3. Prozent berechnen: Anteil am Gesamtkuchen
        if total_sum > 0:
            pct = (real_score / total_sum) * 100
        else:
            pct = 0

        # Nur beschriften, wenn der Balken breit genug ist
        if pct > 4:
            face_color = rect.get_facecolor()  # Gibt (R, G, B, Alpha) von 0.0 bis 1.0 zurück
            r, g, b = face_color[:3]
            luminance = (0.299 * r + 0.587 * g + 0.114 * b)
            # Textfarbe Logik (Dunkel auf Gelb/Hellgrün, Weiß auf Blau/Lila)
            if luminance > 0.55:
                text_color = '#222222'  # Schwarz/Dunkelgrau
            else:
                text_color = 'white'  # Weiß


            # Text: "25%\n(94)" -> Prozent und in Klammern der Heatmap-Wert
            label_text = f"{int(round(pct))}%"


            ax.text(
                rect.get_x() + rect.get_width() / 2,
                rect.get_y() + rect.get_height() / 2,
                label_text,
                ha='center', va='center',
                color=text_color, fontweight='bold', fontsize=15
            )

# 5. STYLING
plt.title("Der Gesamt-Score: Zusammensetzung nach Kategorien", pad=20, fontsize=20, color='#333333')
plt.xlabel("Index-Punkte (Durchschnitt aller Kategorien)", fontsize=18, fontweight='bold', color='#555555')
plt.ylabel("")

sns.despine(left=True, bottom=False)
plt.grid(axis='x', linestyle='-', alpha=0.15, color='black')
plt.grid(visible=False, axis='y')

plt.yticks(ticks=range(len(plot_data_4a)), labels=plot_data_4a["Name"], fontsize=18, fontweight='bold', color='#222222')
plt.xticks(color='#555555')

# Legende
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

# === PLOT 4b: REALITÄTS-CHECK (LOGIK GEDREHT: VIEL SERVICE = GUT) ===
plt.figure(figsize=(14, 9))

# 1. BERECHNUNG
plot_data_4b = top_8_global.copy()

# Echte Daten: Einwohner pro Bank
plot_data_4b["Ew_pro_Bank"] = plot_data_4b["Einwohner"] / plot_data_4b["Filialen"]

# Referenz: 3.792
ref_avg = 3792

# Abweichung berechnen
plot_data_4b["Abweichung"] = plot_data_4b["Ew_pro_Bank"] - ref_avg

# SCORE BERECHNUNG (UMGEDREHT)
# Wir ziehen die Abweichung ab!
# Fall A: Stadt hat 2.000 Ew/Bank (Super Service).
#         2.000 - 3.792 = -1.792.
#         Score - (-1.792 * Faktor) = Score + Bonus. -> GRÜN
# Fall B: Stadt hat 6.000 Ew/Bank (Schlechter Service).
#         6.000 - 3.792 = +2.208.
#         Score - (+2.208 * Faktor) = Score - Abzug. -> ROT

scaling_factor = 0.004
plot_data_4b["Index_Nachher"] = plot_data_4b["Index_Vorher"] - (plot_data_4b["Abweichung"] * scaling_factor)

# Sortieren für den Plot
plot_data_4b = plot_data_4b.sort_values(by="Index_Nachher", ascending=True)
my_range = range(1, len(plot_data_4b.index) + 1)

# 2. FARBEN: Grün = Verbesserung, Rot = Verschlechterung
colors_nachher = []
for i, row in plot_data_4b.iterrows():
    if row["Index_Nachher"] > row["Index_Vorher"]:
        colors_nachher.append('#2ca02c') # Grün (Bonus)
    else:
        colors_nachher.append('#d62728') # Rot (Abzug)

# 3. PLOTTEN
plt.hlines(y=my_range, xmin=plot_data_4b['Index_Nachher'], xmax=plot_data_4b['Index_Vorher'],
           color='grey', alpha=0.4, linewidth=2.5)
plt.scatter(plot_data_4b['Index_Vorher'], my_range, color='grey', alpha=0.65, s=200,
            label='Score ohne Einberechnung', zorder=4)
plt.scatter(plot_data_4b['Index_Nachher'], my_range, c=colors_nachher, alpha=0.65, s=200, zorder=5)

# Legende (angepasst an neue Logik)
plt.scatter([], [], c='#2ca02c', s=200, label='Bonus (Schlechte Versorgung / Wenig Banken)')
plt.scatter([], [], c='#d62728', s=200, label='Strafe (Gute Versorgung / Viele Banken)')

# Pfeile
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

# Text unten
plt.text(
    x=0.02, y=0.98,  # Position: 2% von links, 98% von unten
    s=f"Referenz: Ø {ref_avg} Einwohner pro Bank.\n• (< {ref_avg}) = Hohe Dichte = Bonus (Grün)"
      f"\n• (> {ref_avg}) = Niedrige Dichte = Strafe (Rot)",
    transform=plt.gca().transAxes,  # WICHTIG: Bezieht sich auf den Rahmen des Diagramms
    ha='left', va='top',            # Ankerpunkt der Box ist oben links
    fontsize=16,
    bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'),
    zorder=20                       # Stellt sicher, dass es über den Linien liegt
)

plt.tight_layout()
plt.savefig(output_dir / "4b_Finaler_Score_Bankdichte.png", dpi=300)