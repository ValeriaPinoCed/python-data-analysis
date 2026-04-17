from jinja2 import Environment, FileSystemLoader
import pandas as pd
import requests

URL = "https://ddragon.leagueoflegends.com/cdn/12.23.1/data/en_US/champion.json"

peticion = requests.get(URL)
datos_campeones = peticion.json()
# transformamos en diccionario la información que hay en la URL
informacion_campeones = datos_campeones["data"]
# la tabla no sale del JSON completo, sino de la parte "data"

df = pd.DataFrame.from_dict(datos_campeones["data"], orient="index")
# utilizamos este comando para intercambiar las columnas por las filas dado que antes Pandas detectaba el nombre de los campeones como columnas
tabla_nueva = pd.json_normalize(df["info"])
# sacamos una tabla nueva donde desanidamos las estadisticas de "ataque", "defensa", "magic" y "difficulty" que estaban dentro de "info" para que aparezcan en la tabla de forma separada
tabla_stats = pd.json_normalize(df["stats"])
# sacamos una tabla nueva donde desanidamos las estadisticas de que estaban dentro de "stats" para que aparezcan en la tabla de forma separada
tabla_stats.drop(columns=['hpperlevel', 'mpperlevel', 'armorperlevel', 'spellblockperlevel',
                 'hpregenperlevel', 'mpregenperlevel', 'critperlevel', 'attackdamageperlevel', 'attackspeedperlevel'], inplace=True)


# cambiamos con el Diccionario de la URL los títulos de las columnas
campeones = {
    "key": "Codigo",
    "name": "Nombre",
    "title": "Titulo",
    "blurb": "Lore",
    "attack": "Ataque",
    "defense": "Defensa",
    "magic": "Poder de Habilidad",
    "difficulty": "Dificultad",
    "tags": "Etiqueta",
    "partype": "Tipo de recurso",
    "hp": "Vida",
    "mp": "Mana",
    "armor": "Armadura",
    "spellblock": "Resistencia Magica",
    "attackrange": "Rango",
    "hpregen": "Regeneracion de Vida",
    "mpregen": "Regeneracion de Mana",
    "crit": "Critico",
    "attackdamage": "Daño de Ataque",
    "attackspeed": "Velocidad de Ataque",
    "movespeed": "Velocidad de Movimiento"
}


df_final = pd.concat([df, tabla_nueva, tabla_stats], axis=1)
# para mostrar un dataframe completo con la información tanto de tabla_nueva como df utilizamos el comando concat para fusionar ambas estructuras en una sola tabla
df_final.drop(columns=['version', 'id', 'image',
              'info', 'stats'], inplace=True)
# eliminamos las columnas que no son importantes o repiten datos
df_final.rename(columns=campeones, inplace=True)

df_filtro = df_final[df_final['Etiqueta'].apply(
    lambda x: 'Fighter' in x and 'Tank' in x)]
# utilizamos esta funcion para filtrar solo los campeones que utilizan las etiquetas de 'Fighter' o 'Tank'

Juggernaut = df_final.loc[df_final['Etiqueta'].apply(
    lambda x: x == ['Fighter', 'Tank']), 'Etiqueta'] = '[Juggernaut]'
# esta función sirve para sustituir por 'Juggernaut' las etiquetas de 'Fighter' y 'Tank' independientemente del orden


base = "https://opgg-static.akamaized.net/meta/images/lol/16.8.1/champion/"
tail = ".png"

df_final["Icono_campeon"] = (
    base
    + df_final["Nombre"].astype(str).str.replace(" ",
                                                 "", regex=False).str.replace(".", "", regex=False)
    + tail
)


def arreglar_nombre(x):
    if "'" in x:
        izquierda, derecha = x.split("'", 1)
        x = izquierda + derecha.lower()

    x = x.replace("LeBlanc", "Leblanc")
    x = x.replace("RenataGlasc", "Renata")
    return x


df_final['Icono_campeon'] = df_final['Icono_campeon'].apply(arreglar_nombre)


rows = df_final.to_dict(orient="records")

env = Environment(loader=FileSystemLoader("."))
template = env.get_template("template_campeones.j2")


html_rendered = template.render(rows=rows)

with open("campeones.html", "w", encoding="utf-8") as f:
    f.write(html_rendered)


URL = "https://ddragon.leagueoflegends.com/cdn/12.23.1/data/en_US/item.json"

peticion = requests.get(URL)
datos_objetos = peticion.json()
# transformamos en diccionario la información que hay en la URL
informacion_objetos = datos_objetos["data"]

df_item = pd.DataFrame.from_dict(informacion_objetos, orient="index")
df_item_limpio = df_item.drop(columns=["description", "gold", "colloq", "into", "image", "stacks", "hideFromAll",
                                       "consumeOnFull", "specialRecipe", "requiredChampion", "requiredAlly",
                                       "maps", "from", "depth", "inStore", "consumed", "effect"
                                       ])

df_item_limpio[df_item_limpio["name"]
               != "Gangplank Placeholder"]

info_oro = pd.json_normalize(df_item["gold"])
info_oro = info_oro.drop(columns=['base', 'purchasable', 'sell'])
info_oro = info_oro.add_prefix('gold_')

info_stats = pd.json_normalize(df_item["stats"])
info_stats = info_stats.drop(columns=[
    'PercentAttackSpeedMod',
    'PercentLifeStealMod',
    'PercentLifeStealMod',  'FlatHPRegenMod',  'PercentMovementSpeedMod'])

objetos = {
    "name": "Nombre",
    "plaintext": "Descripcion",
    "tags": "Tipo de Item",
    "gold_total": "Precio",
    "FlatMovementSpeedMod": "Velocidad de Movimiento",
    "FlatHPPoolMod": "Vida",
    "FlatCritChanceMod": "Critico",
    "FlatMagicDamageMod": "Poder de Habilidad",
    "FlatMPPoolMod": "Mana",
    "FlatArmorMod": "Armadura",
    "FlatSpellBlockMod": "Resistencia Magica",
    "FlatPhysicalDamageMod": "Daño de Ataque"
}


df_final_item = pd.concat([df_item_limpio, info_oro, info_stats], axis=1)
df_final_item.rename(columns=objetos, inplace=True)
df_final_item = df_final_item.sort_values("Precio", ascending=False)
df_final_item.dropna(subset=['Nombre'], inplace=True)
df_final_item.drop(columns=['stats'], inplace=True)
df_final_item[~df_final_item['Tipo de Item'].astype(
    str).str.contains('Trinket', na=False)]
df_final_item = df_final_item.fillna('0')

df_final_item.to_html("items.html", index=False)
print(f"Archivos HTML creados con la información de campeones e items")


# este comando lo utilizamos para crear una nueva llamada de datos que recoge las columnas comunes de ambos dataFrames de objetos y campeones
columnas_stats = [
    'Vida', 'Mana', 'Armadura', 'Resistencia Magica',
    'Daño de Ataque', 'Poder de Habilidad', 'Critico', 'Velocidad de Movimiento'
]

nombre_campeon = input("Introduce el nombre del campeón: ").strip()
# filtramos para que en caso de que el usuario escriba el nombre mal salte un aviso
campeon_filtrado = df_final[df_final['Nombre'] == nombre_campeon]
if campeon_filtrado.empty:
    print("Ese campeón no existe en la tabla.")
else:
    campeon = campeon_filtrado.iloc[0]

    items_input = input("Introduce los objetos separados por comas: ").strip()
    lista_items = [item.strip() for item in items_input.split(",")]

# con esto definimos el campeon que elegimos al igual que los objetos
    objetos_elegidos = df_final_item[df_final_item['Nombre'].isin(lista_items)]
    # filtramos para que en caso de que el usuario escriba el nombre mal salte un aviso y se encuentra anidado dentro del else para que si falla el primer input no continúe preguntando por los objetos
    if objetos_elegidos.empty:
        print("Ese item no existe en la tabla.")
    else:

        columnas_comunes = [
            c for c in columnas_stats
            if c in df_final.columns and c in df_final_item.columns
        ]


# recogemos los stats tanto de los campeones como de los items de la columna stats
        stats_campeon = campeon_filtrado[columnas_stats].astype(float)
        stats_objetos = objetos_elegidos[columnas_stats].astype(float).sum()

# sumamos a los stats base del campeon los stats que le da cada item
        stats_totales = stats_campeon + stats_objetos

        print("\nCampeón elegido:", campeon["Nombre"])
        print("\nObjetos elegidos:", ", ".join(lista_items))
        print("\n", stats_totales)
