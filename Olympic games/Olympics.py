import pandas as pd
import matplotlib.pyplot as plt
olympic_games = pd.read_excel('olympics-data.xlsx')
# utilizamos esta función para leer un excel donde se encuentra un DataFrame ya creado

Titulos_columnas = {
    "athlete_id": "ID",
    "name": "Name",
    "born_country": "Country",
    "born_region": "Region",
    "born_city": "City",
    "born_date": "Born Date",
    "died_date": "Decease Date",
    "height_cm": "Height (Cm)",
    "weight_kg": "Weight (Kg)",
}

# cambiamos el título de las columnas para que sea más claro
olympic_games.rename(columns=Titulos_columnas, inplace=True)

Noc = pd.read_csv('noc_regions.csv')

olympic_games_new = pd.merge(
    olympic_games, Noc, left_on="Country", right_on="NOC", how="left")

# en la columna Country relacionamos las siglas de cada país que aparecen en NOC + la región del CSV para poder más adelante eliminar la columna de NOC que no es tan útil y que aparezca la información completa en Country
olympic_games_new["Country"] = olympic_games_new["region"] + \
    " (" + olympic_games_new["NOC_y"] + ")"
olympic_games_new.drop(
    columns=["NOC_x", "NOC_y", "region", "notes"], inplace=True, errors="ignore")

# cambiamos el orden de las columnas para que quede más claro
olympic_games_new = olympic_games_new[[
    "ID", "Name", "Country", "Region", "City",
    "Born Date", "Decease Date", "Height (Cm)", "Weight (Kg)"
]]

# para que el DataFrame al imprimirlo quede más humano rellenamos NaN de las columnas que ofrecen texto o fechas con "Sin Datos"
columnas_texto = ["Country", "Region", "City", "Born Date", "Decease Date"]
olympic_games_new[columnas_texto] = olympic_games_new[columnas_texto].fillna(
    "Sin Datos")


# esta función la utilizamos para pasar a numérico para que NaN se muestre en estas columnas como valores faltantes reales y que al realizar después un sort_values el código no se rompa
olympic_games_new["Height (Cm)"] = pd.to_numeric(
    olympic_games_new["Height (Cm)"], errors="coerce"
)
olympic_games_new["Weight (Kg)"] = pd.to_numeric(
    olympic_games_new["Weight (Kg)"], errors="coerce"
)

# utilizamos esta función para filtrar entre aquellos atletas que han nacido en Inglaterra
print(olympic_games_new.query('Country == "UK (GBR)"'))

# esta función es útil para filtrar directamente por string para mirar datos que poseen información específica, en este caso aquellos atletas que de apellido tienen Watson
filtro_apellido = olympic_games_new[olympic_games_new['Name'].str.contains(
    "Watson")]
print(filtro_apellido.head(10))

# esta función comprueba en orden ascendente los atletas con mayor altura en cm, no obstante para que funcione, las filas sin información deben contener NaN
personas_altas = olympic_games_new = olympic_games_new.sort_values(
    "Height (Cm)", ascending=False)
print(personas_altas.head(5))

# al importar matplotlib.pylot generamos un gráfico con la columna altura que nos permita visualizar la distribución de atletas según la altura
distribución_altura = olympic_games_new["Height (Cm)"].dropna()

plt.figure(figsize=(10, 6))
plt.hist(distribución_altura, bins=30, color="skyblue", edgecolor="black")
plt.title("Distribución de altura de los atletas")
plt.xlabel("Altura (cm)")
plt.ylabel("Número de Atletas")
# sirve para mostrar la cuadrícula en el gráfico (líneas de fondo) y leer mejor los valores
plt.grid(True,  axis='y')
# convertimos el eje Y en una escala logarítmica para una mejor distribución de las barras y hacer el gráfico se vuelve más legible
plt.yscale("log")
plt.show()

# creamos un gráfico de barras apiladas donde se muestra la distribución de atletas por país y eliminamos aquellas líneas donde pone "Sin Datos"
atletas_pais = olympic_games_new["Country"]
atletas_pais = atletas_pais[atletas_pais !=
                            "Sin Datos"].value_counts().head(20)
plt.figure(figsize=(12, 6))
atletas_pais.plot(kind="bar", color="navy", edgecolor="black")
plt.title("Distribución de atletas por país")
plt.xlabel("País")
plt.ylabel("Número de atletas")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.show()

# creamos un filtro que muestre las personas pertenecientes a la Región de Madrid que pesan menos de 70 kilos
filtro_ciudad = olympic_games_new[
    (olympic_games_new["Weight (Kg)"] < 70) &
    (olympic_games_new["Region"] == "Madrid")
]
print(filtro_ciudad.head(15))
