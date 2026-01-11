import osmnx as ox
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter


regionen = np.load("./data/regionen_in_nordbayern/regionenpur.npy")
print(len(regionen))
print(regionen)

regionen = np.delete(regionen,1)
print(regionen)

regionen_datei = open("./data/regionen_in_nordbayern/regionenpur.npy", "wb")
np.save("./data/regionen_in_nordbayern/regionenpur.npy", regionen)
regionen_datei.close()




