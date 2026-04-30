import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Environment, FileSystemLoader

Pokemon_df = pd.read_csv('pokemon_data.csv').fillna("-")
Pokemon_df.head()
Pokemon_df.columns


color_type = {
    'Normal': '#A8A77A',
    'Fire': '#EE8130',
    'Water': '#6390F0',
    'Electric': '#F7D02C',
    'Grass': '#7AC74C',
    'Ice': '#96D9D6',
    'Fighting': '#C22E28',
    'Poison': '#A33EA1',
    'Ground': '#E2BF65',
    'Flying': '#A98FF3',
    'Psychic': '#F95587',
    'Bug': '#A6B91A',
    'Rock': '#B6A136',
    'Ghost': '#735797',
    'Dragon': '#6F35FC',
    'Dark': '#705746',
    'Steel': '#B7B7CE',
    'Fairy': '#D685AD'
}

Pokemon_df['Total'] = Pokemon_df[['HP', 'Attack', 'Defense',
                                  'Sp. Atk', 'Sp. Def', 'Speed']].sum(axis=1)
Pokemon_no_mega = Pokemon_df[
    ~Pokemon_df['Name'].str.contains(
        r'Mega|Primal|Forme|White|Black|Kyurem|Altered|Origin',
        case=False,
        na=False,
        regex=True
    )
].copy()


type_counts = Pokemon_df['Type 1'].value_counts()
colors = [color_type[tipo] for tipo in type_counts.index]

plt.figure(figsize=(10, 10))

wedges, texts, autotexts = plt.pie(
    type_counts,
    labels=type_counts.index,
    colors=colors,
    autopct='%1.1f%%',
    pctdistance=0.75,
    labeldistance=1.08,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
    textprops={'fontsize': 11}
)

plt.title('Distribution of Pokémon Types',
          fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('Pokemon Types.png')


Pokemon_ATK = Pokemon_no_mega.loc[Pokemon_no_mega['Attack'] >= 125].sort_values(
    "Attack", ascending=False)
Pokemon_ATK_plot = Pokemon_ATK.set_index("Name").head(
    20).sort_values("Attack", ascending=True)

bar_colors = Pokemon_ATK_plot['Type 1'].map(color_type)

plt.figure(figsize=(10, 8))

bars = plt.barh(Pokemon_ATK_plot.index, Pokemon_ATK_plot["Attack"],
                color=bar_colors, edgecolor="black")

for bar in bars:
    width = bar.get_width()
    plt.text(width + 1, bar.get_y() + bar.get_height()/2,
             f'{width}', va='center', fontsize=10)


plt.title("Top 20 Pokemon with highest base attack",
          fontsize=16, fontweight='bold')
plt.xlabel("Attack points")
plt.ylabel("Pokemon Name")
plt.grid(True, axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('High Attack.png')


Pokemon_DEF = Pokemon_no_mega.loc[Pokemon_no_mega['Defense'] >= 125].sort_values(
    "Defense", ascending=False)
Pokemon_DEF_plot = Pokemon_DEF.set_index("Name").head(
    20).sort_values("Defense", ascending=True)

bar_colors = Pokemon_DEF_plot['Type 1'].map(color_type)

plt.figure(figsize=(10, 8))

bars = plt.barh(Pokemon_DEF_plot.index, Pokemon_DEF_plot["Defense"],
                color=bar_colors, edgecolor="black")

for bar in bars:
    width = bar.get_width()
    plt.text(width + 1, bar.get_y() + bar.get_height()/2,
             f'{width}', va='center', fontsize=10)


plt.title("Top 20 Pokemon with highest base defense",
          fontsize=16, fontweight='bold')
plt.xlabel("Defense points")
plt.ylabel("Pokemon Name")
plt.grid(True, axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('High Defense.png')


Pokemon_LEGEN = Pokemon_df[Pokemon_df['Legendary'] == True]

legend_counts = Pokemon_df['Legendary'].value_counts()

plt.figure(figsize=(8, 8))

wedges, texts, autotexts = plt.pie(
    legend_counts,
    labels=['Non legendary', 'Legendary'],
    colors=plt.cm.Pastel2.colors[1:3],
    autopct='%1.1f%%',
    pctdistance=0.75,
    labeldistance=1.08,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1.5},
    textprops={'fontsize': 11}
)

plt.title('Distribution of Legendary and Non Legendary Pokemon',
          fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('Legendary and Non Legendary.png')


sns.set_theme(style="whitegrid")


Attack_Defense = sns.lmplot(
    data=Pokemon_df,
    x="Attack",
    y="Defense",
    hue="Legendary",
    height=7,
    aspect=1.2,
    scatter_kws={"s": 50, "alpha": 0.6},
    line_kws={"linewidth": 3}
)

Attack_Defense.set_axis_labels("Attack Power", "Defense Power")
plt.title("Relationship between Attack and Defense: Does more attack imply more defense?",
          fontsize=16, fontweight='bold', pad=20)
plt.savefig('Relation Attack-Defense.png')

Pokemon_LEGEN = (Pokemon_df[Pokemon_df['Legendary']
                            == True].groupby('Type 1').size().sort_values(ascending=False))


bar_colors = [color_type.get(tipo, '#2c3e50') for tipo in Pokemon_LEGEN.index]

plt.figure(figsize=(10, 8))

bars = plt.barh(Pokemon_LEGEN.index, Pokemon_LEGEN.values,
                color=bar_colors, edgecolor="black")

for bar in bars:
    width = bar.get_width()
    plt.text(width + 1, bar.get_y() + bar.get_height()/2,
             f'{width}', va='center', fontsize=10)


plt.title("Most common Type within Legendary Pokemon",
          fontsize=16, fontweight='bold')
plt.xlabel("Number of Pokemon")
plt.ylabel("Pokemon Type")
plt.grid(True, axis='x', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('Legendary Type.png')


Flying_Fire = ((Pokemon_no_mega['Type 1'] == 'Fire') & (
    Pokemon_no_mega['Type 2'] == 'Flying')).sum()
Flying_Fire = Pokemon_no_mega.loc[(Pokemon_no_mega['Type 1'] == 'Fire') & (
    Pokemon_no_mega['Type 2'] == 'Flying')]
print(Flying_Fire)

Total_poison = ((Pokemon_df['Type 1'] == 'Poison') | (
    Pokemon_df['Type 2'] == 'Poison')).sum()
print(Total_poison)


Pokemon_total_no_mega = Pokemon_no_mega.loc[Pokemon_df['Generation'].isin([3, 4, 5]),
                                            ['Name', 'Total']].sort_values(by='Total', ascending=False)

Pokemon_total = Pokemon_df.loc[
    Pokemon_df['Generation'].isin([3, 4, 5]),
    ['Name', 'Total']
].sort_values(by='Total', ascending=False)


print(Pokemon_total.head(10))
print(Pokemon_total_no_mega.head(10))


Dragon_df = Pokemon_no_mega.loc[
    ((Pokemon_no_mega['Type 1'] == "Dragon") | (Pokemon_no_mega['Type 2'] == "Dragon")) & (
        Pokemon_no_mega['Generation'].isin([5, 6]))].sort_values(by='Total', ascending=False)

print(Dragon_df.head())

Powerful_fire_df = Pokemon_no_mega.loc[
    ((Pokemon_no_mega['Type 1'] == "Fire") | (Pokemon_no_mega['Type 2'] == "Fire")) &
    (Pokemon_no_mega['Legendary']), ['Name', 'Attack', 'Generation']].sort_values(by='Attack', ascending=False)
print(Powerful_fire_df)


Slow_Pokemon = Pokemon_no_mega.nsmallest(5, 'Speed')[['Name', 'Speed']]
Fast_Pokemon = Pokemon_no_mega.nlargest(5, 'Speed')[['Name', 'Speed']]
sns.set_theme(style="whitegrid")

plt.figure(figsize=(10, 6))


sns.histplot(Pokemon_no_mega['Speed'], bins=20,
             color='#6390F0',
             edgecolor='white',
             kde=True)

plt.title("Pokemon Distribution by Speed Stat",
          fontsize=16, fontweight='bold', pad=15)
plt.xlabel("Speed stat", fontsize=12)
plt.ylabel("Frequency", fontsize=12)

sns.despine()

plt.tight_layout()
plt.savefig('Speed stat.png')


env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('Pokemon.j2')

total_table = Pokemon_total.head(10).to_html(
    index=False, classes='pokemon-table', border=0, justify='left')

total_no_mega_table = Pokemon_total_no_mega.head(10).to_html(
    index=False, classes='pokemon-table', border=0, justify='left')

dragon_table = Dragon_df.head(10).to_html(
    index=False, classes='pokemon-table', border=0, justify='left')

fire_table = Powerful_fire_df.head(10).to_html(
    index=False, classes='pokemon-table', border=0, justify='left')

html = template.render(
    total_pokemon=len(Pokemon_df),
    legendary_count=int(Pokemon_df['Legendary'].sum()),
    max_attack=int(Pokemon_df['Attack'].max()),
    max_speed=int(Pokemon_df['Speed'].max()),
    total_poison=int(((Pokemon_df['Type 1'] == 'Poison') | (
        Pokemon_df['Type 2'] == 'Poison')).sum()),
    flying_fire=int(((Pokemon_no_mega['Type 1'] == 'Fire') & (
        Pokemon_no_mega['Type 2'] == 'Flying')).sum()),
    top_attack_name=Pokemon_ATK_plot.sort_values(
        "Attack", ascending=False).index[0] if 'Pokemon_ATK_plot' in globals() else '',
    top_defense_name=Pokemon_DEF_plot.sort_values(
        "Defense", ascending=False).index[0] if 'Pokemon_DEF_plot' in globals() else '',
    type_pie_path='Pokemon Types.png',
    attack_bar_path='High Attack.png',
    defense_bar_path='High Defense.png',
    legendary_type_path='Legendary Type.png',
    attack_defense_path='Relation Attack-Defense.png',
    speed_hist_path='Speed stat.png',
    legendary_path='Legendary and Non Legendary.png',
    total_table=total_table,
    total_no_mega_table=total_no_mega_table,
    dragon_table=dragon_table,
    fire_table=fire_table
)

with open('pokemon_report.html', 'w', encoding='utf-8') as f:
    f.write(html)
