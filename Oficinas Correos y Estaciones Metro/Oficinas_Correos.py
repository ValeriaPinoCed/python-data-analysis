import pandas as pd
import requests
import folium
import json
from folium.plugins import FeatureGroupSubGroup, GroupedLayerControl

URL = "https://datos.madrid.es/dataset/212841-0-oficinas-correos/resource/212841-1-oficinas-correos-json/download/212841-0-oficinas-correos.json"

peticion = requests.get(URL)
Correos_Madrid = peticion.json()
informacion_correos = Correos_Madrid["@graph"]

# hay muchas definiciones anidadas por lo que es necesario normalizar el json para poder utilizarlas
Oficinas = pd.json_normalize(informacion_correos)

Oficinas["Distrito"] = Oficinas["address.district.@id"].str.split("/").str[-1]
Oficinas["Area"] = Oficinas["address.area.@id"].str.split("/").str[-1]

# divide en tres partes la información de la columna organization.organization-name en Oficina de Correos [0], Sucursal [1] y Nombre de Oficina [2]
partes = Oficinas["organization.organization-name"].str.split(
    r"\.\s*", expand=True)
# Toma el tipo de sucursal completo
Oficinas["Numero de Sucursal"] = partes[1].str.strip()

# Toma el nombre real de la oficina
Oficinas["Nombre de Oficina"] = partes[2].str.strip()


Oficinas = Oficinas.drop(
    columns=['@id', '@type', 'relation', 'address.district.@id', 'address.area.@id', 'address.locality', 'organization.organization-name', 'organization.services', 'organization.accesibility'])

Titulos_Columnas = {
    "id": "Identificacion",
    "address.postal-code": "Codigo Postal",
    "address.street-address": "Direccion",
    "organization.schedule": "Horario",
    "organization.organization-desc": 'Estacion de Metro Cercana',
    "location.latitude": "Latitud",
    "location.longitude": "Longitud"}


Oficinas.rename(columns=Titulos_Columnas, inplace=True)

# cogemos la latitud y longitud en numérico para poder representar en un mapa su localización exacta
Oficinas["Latitud"] = pd.to_numeric(Oficinas["Latitud"], errors="coerce")
Oficinas["Longitud"] = pd.to_numeric(Oficinas["Longitud"], errors="coerce")

# hacemos un par de splits para ignorar información que no es necesaria
Oficinas["Horario"] = Oficinas["Horario"].str.split(
    "Consultar").str[0].str.strip()
Oficinas["Estacion de Metro Cercana"] = Oficinas["Estacion de Metro Cercana"].str.split(
    ":").str[-1].str.strip()

Oficinas = Oficinas[[
    "Identificacion", "Numero de Sucursal", "Nombre de Oficina", "Codigo Postal", "Distrito", "Area",
    "Direccion", "Horario", "Estacion de Metro Cercana", "Latitud", "Longitud"
]
].dropna(subset=["Latitud", "Longitud"])


# generamos otro DataFrame a partir de un archivo geojson sin importar geopandas para poder añadir al mapa las localizaciones de las Estaciones de Metro
with open("M4_Estaciones.geojson", "r", encoding="utf-8") as f:
    datos_metro = json.load(f)
Estaciones_Metro = pd.DataFrame([feat["properties"]
                                 for feat in datos_metro["features"]])

# nos quedamos con los datos importantes en este caso la longitud, latitud, codigo de la estación, nombre y las líneas con las que conecta
Estaciones_Metro = pd.DataFrame([
    {
        "Longitud": feat["geometry"]["coordinates"][0],
        "Latitud": feat["geometry"]["coordinates"][1],
        "Codigo Estacion": feat["properties"].get("CODIGOESTACION"),
        "Nombre": feat["properties"].get("DENOMINACION"),
        "Lineas": feat["properties"].get("LINEAS"),
    }
    for feat in datos_metro["features"]
])

# asociamos un color a cada linea
Mapa_linea_color = [
    {"Linea": "1", "color": "lightblue"},
    {"Linea": "2", "color": "red"},
    {"Linea": "3", "color": "lightred"},
    {"Linea": "4", "color": "beige"},
    {"Linea": "5", "color": "lightgreen"},
    {"Linea": "6", "color": "lightgray"},
    {"Linea": "7", "color": "orange"},
    {"Linea": "8", "color": "pink"},
    {"Linea": "9", "color": "darkpurple"},
    {"Linea": "10", "color": "darkblue"},
    {"Linea": "11", "color": "darkgreen"},
    {"Linea": "12", "color": "green"}
]


colores_linea = {x["Linea"]: x["color"] for x in Mapa_linea_color}


# Centramos el mapa en la media de todos los puntos con folium (se utilizará como alternativa si hay valores NaN)
center_lat = Oficinas["Latitud"].mean()
center_lon = Oficinas["Longitud"].mean()
Mapa_Oficinas = folium.Map(location=[center_lat, center_lon], zoom_start=13)

# generamos con folium dos capas a las que se pueda hacer toggle según sean oficinas de correos o estaciones de metro
capa_correos = folium.FeatureGroup(name="Oficinas de Correos", show=True)
capa_metro = folium.FeatureGroup(name="Estaciones de Metro", show=True)

Mapa_Oficinas.add_child(capa_correos)
Mapa_Oficinas.add_child(capa_metro)

#  creamos un diccionario vacío para guardar una subcapa por cada línea de metro y construir esas subcapas una a una
subcapas_metro = {}
for linea in colores_linea.keys():
    subcapas_metro[linea] = FeatureGroupSubGroup(capa_metro, f"Línea {linea}")
    Mapa_Oficinas.add_child(subcapas_metro[linea])

# le damos forma y color a las Oficinas de Correos y las situamos en el mapa según su longitud y latitud
for _, row in Oficinas.dropna(subset=["Latitud", "Longitud"]).iterrows():
    popup_text = f"{row['Direccion']}<br>{row['Codigo Postal']}<br>{row['Distrito']}<br>{row['Area']}<br>{row['Horario']}"
    folium.Marker(
        location=[row["Latitud"], row["Longitud"]],
        popup=popup_text,
        tooltip="Oficina de Correos",
        icon=folium.Icon(
            color="blue",
            icon="building",
            prefix="fa"
        )
    ).add_to(capa_correos)


# le damos forma y color a las Estaciones de Metro y las situamos en el mapa según su longitud y latitud y en caso de que las estaciones tengan más de una linea se le asocia el color negro
for _, row in Estaciones_Metro.dropna(subset=["Latitud", "Longitud"]).iterrows():
    lineas_estacion = [x.strip() for x in str(row["Lineas"]).split(",")]
    popup_text = f"{row['Codigo Estacion']}<br>{row['Nombre']}<br>{row['Lineas']}"

    for linea in lineas_estacion:
        if linea in subcapas_metro:
            folium.Marker(
                location=[row["Latitud"], row["Longitud"]],
                popup=popup_text,
                tooltip=f"Metro Línea {linea}",
                icon=folium.Icon(
                    color=colores_linea.get(linea, "black"),
                    icon="train",
                    prefix="fa"
                )
            ).add_to(subcapas_metro[linea])

# añadimos un control de capas al mapa para plegar y desplegar grupos desde la interfaz del propio Folium y con collapsed=False evitamos que aparezcan plegadas
folium.LayerControl(collapsed=False).add_to(Mapa_Oficinas)

GroupedLayerControl(
    groups={
        "Metro": list(subcapas_metro.values())
    },
    exclusive_groups=False,
    collapsed=False
).add_to(Mapa_Oficinas)


Mapa_Oficinas.save("Mapa_Oficinas_Correos.html")
print("Mapa de Oficinas de Correos y Estaciones de Metro generado correctamente")
