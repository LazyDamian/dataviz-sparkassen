# dataviz-sparkassen
# Visualisierung für den besten Sprkassenstandort



import plotly.express as px
import geopandas as gpd
import requests


url = 'https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/refs/heads/main/4_kreise/1_sehr_hoch.geo.json'
response = requests.get(url)

# Save the file locally
with open("deutschland.geo.json", "wb") as file:
    file.write(response.content)



# Load your GeoJSON file
geojson_file = 'deutschland.geo.json'  # Replace with your GeoJSON file path

# Use GeoPandas to read the GeoJSON
gdf = gpd.read_file(geojson_file)

# Plot the GeoJSON using Plotly Express
fig = px.choropleth_mapbox(
    gdf,
    geojson=gdf.geometry.__geo_interface__,  # Use the GeoJSON geometries directly
    locations=gdf.index,  # Using the index to link the geometries
    color=gdf.index,  # You can specify a column here for coloring
    title="GeoJSON Plot",
    color_continuous_scale="Viridis",  # You can change the color scale
    mapbox_style="carto-positron",  # Use a different map style here if needed
    center={"lat": 51, "lon": 10},  # Adjust this if you need to center the map
    zoom=3  # Adjust the zoom level as per your needs
)

# Show the plot
fig.show()
