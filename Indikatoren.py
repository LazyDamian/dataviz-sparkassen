import pandas as pd
from pathlib import Path

# Pfad zu deiner Datei (bitte ggf. anpassen)
inkar_path = Path(r"data/inkar/inkar_2025.csv")

if inkar_path.exists():
    # Wir lesen nur die Spalte 'Indikator' ein, um Speicherplatz zu sparen
    # Da die Datei sehr groß sein kann, ist usecols hier effizient
    df_indikator = pd.read_csv(inkar_path, sep=";", usecols=["Indikator"])

    # Alle einzigartigen Indikatoren sortiert auflisten
    alle_indikatoren = sorted(df_indikator["Indikator"].dropna().unique())

    print(f"Anzahl der gefundenen Indikatoren: {len(alle_indikatoren)}")
    print("-" * 50)

    # Optional: Gezielte Suche nach bankrelevanten Schlagworten
    suchbegriffe = ["Einkommen", "Kaufkraft", "BIP", "Dichte", "Arbeitslos"]

    print("Gefundene Treffer für deine Analyse:")
    for name in alle_indikatoren:
        if any(wort.lower() in str(name).lower() for wort in suchbegriffe):
            print(f" - {name}")

    # Falls du die komplette Liste sehen willst, kommentiere die nächste Zeile ein:
    # print(alle_indikatoren)
else:
    print(f"Datei nicht gefunden unter: {inkar_path}")