import osmnx as ox
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter

# Define the location (you can specify a city or bounding box)
location = 'Erlangen'

# Fetch the data
tags = {'amenity': 'atm'}
atm_gdf = ox.features_from_place(location, tags)
anzahl_atm = atm_gdf.shape[0]
# Display ATM locations
print(anzahl_atm)


import pandas as pd

# Initial DataFrame
data = {
    'Region': ['Test'],
    'ATM-Anzahl': [0]
}

atm_df = pd.DataFrame(data)





csv_file_path = Path(r"data/inkar_bayern_nordbayern.csv")

if csv_file_path.exists():
    # --- 2. DATEN LADEN & FILTERN ---
    df_raw = pd.read_csv(csv_file_path, sep=",", dtype={"Kennziffer": str})

    # Filter auf Nordbayern und Indikatoren
    mask = (df_raw["Nordbayern"] == True)
    df_filtered = df_raw[mask].copy()
    df_filtered["Wert"] = pd.to_numeric(df_filtered["Wert"], errors="coerce")

    latest_year = df_filtered["Zeitbezug"].max()

    df_pivot = df_filtered[df_filtered["Zeitbezug"] == latest_year].pivot_table(
        index=["Name"], columns="Indikator", values="Wert"
    ).reset_index()

    # --- Calculate Gesamt_Index without pos and neg indicators ---
    df_ranking = df_pivot.copy()

    # Directly compute a Overall Index based only on available columns, if needed
    # Here we simply calculate the mean score of the indicators available; adjust as necessary.
    df_ranking["Gesamt_Index"] = df_ranking.mean(axis=1, numeric_only=True)

    alle_regionen = df_ranking.sort_values(by="Gesamt_Index", ascending=False).head(264).copy()


    # Print the names of the best indicators

    regionen = []
    for name in alle_regionen["Name"]:
        regionen.append(name)

    regionen = np.array(regionen)
    regionen_datei = open("./data/regionen_in_nordbayern/regionenpur.npy", "wb")
    np.save("./data/regionen_in_nordbayern/regionenpur.npy", regionen)
    regionen_datei.close()


    #----------------------------------CLEANUP----------------------------------
    regionen = np.load("./data/regionen_in_nordbayern/regionenpur.npy")
    print(len(regionen))
    print(regionen)


    values_to_delete = ['Erlangen-Höchstadt', 'Unterfranken', 'Neustadt a.d.Aisch-Bad Windsheim', 'Kronach', 'Oberpfalz',
                        'Oberfranken', 'Würzburg, Stadt', 'Weißenburg-Gunzenhausen', 'Mittelfranken', 'Bamberg, Stadt',
                        'Regensburg, Stadt', 'Wunsiedel i.Fichtelgebirge', 'Coburg, Stadt', 'Fürth, Stadt',
                        'Bayreuth, Stadt', 'Ansbach, Stadt', 'Nürnberg', #Nuremberg
                        'Amberg', 'Weiden i.d.OPf.', 'Hof, Stadt', 'Schweinfurt, Stadt']

    # Create a boolean mask to identify elements to keep
    mask = ~np.isin(regionen, values_to_delete)

    regionen = regionen[mask]

    print(regionen)

    regionen_datei = open("./data/regionen_in_nordbayern/regionenpur.npy", "wb")
    np.save("./data/regionen_in_nordbayern/regionenpur.npy", regionen)
    regionen_datei.close()

    # ---------------------------------- ----------------------------------
    print("Top 10 Indicators:")
    for name in regionen:
        print(name)
        tags = {'amenity': 'atm'}
        atm_gdf = ox.features_from_place(name, tags)
        anzahl_atm = atm_gdf.shape[0]
        # Display ATM locations

        print(anzahl_atm)

        # New row as a dictionary
        new_row = pd.DataFrame({'Region': [name], 'ATM-Anzahl': [anzahl_atm]})

        print(new_row)
        # Appending the new row
        # Concatenating the new row to the existing DataFrame
        atm_df = pd.concat([atm_df, new_row], ignore_index=True)

    print(atm_df)



else:
    print(f"Datei nicht gefunden: {csv_file_path}")


#SCRAPE ALL LOCATIONS ------------------------------------------------------
