import pandas as pd
import requests

URL = "https://datos.madrid.es/dataset/212841-0-oficinas-correos/resource/212841-1-oficinas-correos-json/download/212841-0-oficinas-correos.json"

peticion = requests.get(URL)
Correos_Madrid = peticion.json()
informacion_correos = Correos_Madrid["@graph"]


Oficinas = pd.json_normalize(informacion_correos)

Oficinas["Distrito"] = Oficinas["address.district.@id"].str.split("/").str[-1]
Oficinas["Area"] = Oficinas["address.area.@id"].str.split("/").str[-1]

Oficinas = Oficinas.drop(
    columns=['@id', '@type', 'relation', 'address.district.@id', 'address.area.@id', 'address.locality', 'organization.organization-name'])

Titulos_Columnas = {
    "id": "Identificacion",
    "address.postal-code": "Codigo Postal",
    "title": "Nombre de Oficina",
    "address.street-address": "Direccion",
}

Oficinas.rename(columns=Titulos_Columnas, inplace=True)

print(Oficinas)
