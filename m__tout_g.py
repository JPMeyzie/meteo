import plotly.express as px
from babel.dates import format_date
import pandas as pd
import webbrowser
import os
from git import Repo

# DataFrame à partir du Google sheet
url = 'https://docs.google.com/spreadsheets/d/1HL-9V6yhFDP1BtO7AaqcHWNaeueUyEVq5LSaoEYWQyk/export?format=csv'
df = pd.read_csv(url, parse_dates=['DateR'], dayfirst=True)
df['DateR'] = pd.to_datetime(df['DateR'])

df['Mm'] = pd.to_numeric(df['Mm'], errors='coerce')
df = df.dropna(subset=['Mm'])

# Grouper par mois et faire la somme des Mm
df_grouped_m = df.groupby(df['DateR'].dt.to_period('M')).agg({'Mm': 'sum'}).reset_index()
df_grouped_m['DateR'] = df_grouped_m['DateR'].dt.to_timestamp()

# Convertir les dates en noms de mois en français pour les étiquettes
df['Mois'] = df['DateR'].apply(lambda x: format_date(x, format='MMM YY', locale='fr'))
df_grouped_m['Month'] = df_grouped_m['DateR'].apply(lambda x: format_date(x, format='MMM YY', locale='fr'))

# Grouper par trimestre et faire la somme des Mm
df_grouped_t = df.groupby(df['DateR'].dt.to_period('Q')).agg({'Mm': 'sum'}).reset_index()
df_grouped_t['DateR'] = df_grouped_t['DateR'].dt.to_timestamp()

# Créer une nouvelle colonne pour les trimestres formatés
df_grouped_t['Trimestre'] = df_grouped_t['DateR'].dt.year.astype(str) + ' T' + df_grouped_t['DateR'].dt.quarter.astype(str)

### J O U R
# Créer le graphique interactif avec plotly
fig_jour = px.line(df, x='DateR', y='Mm', title='Relevès pluviométriques - AUREIL - 71, route de Saint-Antoine',
              markers='^')

# Supprimer le titre de l'axe des x
fig_jour.update_xaxes(title='')

# Supprimer l'axe des y
fig_jour.update_yaxes(title='', showticklabels=False)

# Remplacer les étiquettes de l'axe des x par les noms des mois en français
# fig_jour.update_layout(
#     xaxis=dict(
#         tickmode='array',
#         tickvals=df['DateR'],
#         ticktext=df['Mois']
#     )
# )
# Ajouter des boutons pour faire défiler les mois
fig_jour.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=3,
                     label="3 derniers mois",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6 derniers mois",
                     step="month",
                     stepmode="backward"),
                dict(count=9,
                     label="9 derniers mois",
                     step="month",
                     stepmode="backward"),
                dict(count=12,
                     label="12 derniers mois",
                     step="month",
                     stepmode="backward"),
                dict(count=24,
                     label="2 dernières années",
                     step="month",
                     stepmode="backward"),
                dict(step="all",
                     label="Tout")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    )
)

### M O I S
# Créer le graphique interactif avec plotly
fig_mois = px.bar(df_grouped_m, x='DateR', y='Mm', title='Pluviométrie mensuelle - AUREIL - 71, route de Saint-Antoine', color='Mm',
             color_continuous_scale='haline_r')

# Supprimer le titre de l'axe des x
fig_mois.update_xaxes(title='', tickformat='%b %Y')

# Supprimer l'axe des y
fig_mois.update_yaxes(title='', showticklabels=False)

# Ajouter des étiquettes de données
fig_mois.update_traces(text=df_grouped_m['Mm'], textposition='inside')

# Remplacer les étiquettes de l'axe des x par les noms des mois en français
fig_mois.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=df_grouped_m['DateR'],
        ticktext=df_grouped_m['Month']
    )
)

# Ajouter des boutons pour faire défiler les mois
fig_mois.update_layout(
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=3,
                     label="3 derniers mois",
                     step="month",
                     stepmode="backward"),
                dict(count=6,
                     label="6 derniers mois",
                     step="month",
                     stepmode="backward"),
                dict(count=9,
                     label="9 derniers mois",
                     step="month",
                     stepmode="backward"),
                dict(count=12,
                     label="12 derniers mois",
                     step="month",
                     stepmode="backward"),
                dict(step="all",
                     label="Tout")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    )
)

### T R I M E S T R E
# Créer un graphique simplifié
fig_trim = px.bar(df_grouped_t, x='Trimestre', y='Mm', title='Pluviométrie trimestrielle - AUREIL - 71, route de Saint-Antoine',
             color='Mm', color_continuous_scale='haline_r')

fig_trim.update_traces(text=df_grouped_t['Mm'], textposition='inside')
# Supprimer le titre de l'axe des x
fig_trim.update_xaxes(title='')


# Créer des boutons personnalisés pour filtrer les données
years = df_grouped_t['DateR'].dt.year.unique()
buttons = []
for year in years:
    buttons.append(dict(
        args=[{'x': [df_grouped_t[df_grouped_t['DateR'].dt.year == year]['Trimestre']],
               'y': [df_grouped_t[df_grouped_t['DateR'].dt.year == year]['Mm']],
               'text': [df_grouped_t[df_grouped_t['DateR'].dt.year == year]['Mm']]}],
        label=str(year),
        method='update'
        ))

# Ajouter un bouton "Tout"
buttons.append(dict(
    args=[{'x': [df_grouped_t['Trimestre']],
           'y': [df_grouped_t['Mm']],
           'text': [df_grouped_t['Mm']]}],
    label='Tout',
    method='update'
))

# Ajouter les boutons au layout
fig_trim.update_layout(
    updatemenus=[dict(
        buttons=buttons,
        direction='down',
        showactive=True,
        )]
)

# Sauvegarder chaque graphique dans un fichier HTML
fig_jour.write_html("graphique_par_jour.html")
fig_mois.write_html("graphique_par_mois.html")
fig_trim.write_html("graphique_par_trimestre.html")

# Créer un fichier HTML principal qui inclut les autres
with open("index.html", "w") as f:
    f.write("<html><body>\n")
    #f.write("<h2>Graphiques</h2>\n")
    f.write('<iframe src="graphique_par_jour.html" width="100%" height="700px"></iframe>\n')
    f.write('<iframe src="graphique_par_mois.html" width="100%" height="700px"></iframe>\n')
    f.write('<iframe src="graphique_par_trimestre.html" width="100%" height="700px"></iframe>\n')
    f.write("</body></html>\n")

print("Les graphiques ont été sauvegardés et le fichier index.html a été créé.")

# Chemin vers le dépôt Git
repo_path = "c:\\Users\\meyzi\\Python\\meteo"

# Initialisr les fichiers au dépôt
repo = Repo(repo_path)

# Initialiser le dépôt Git
repo.git.add("graphique_par_jour.html")
repo.git.add("graphique_par_mois.html")
repo.git.add("graphique_par_trimestre.html")
repo.git.add("index.html")

# Vérifier le statut après avoir ajouté les fichiers
print("Statut après avoir ajouté les fichiers :")
print(repo.git.status())

# Commit les changements
repo.index.commit("Mise à jour des graphiques")

# Vérifier le dernier commit
print("Dernier commit :")
print(repo.git.log(-1))

# Pousser les changements vers GitHub
origin = repo.remote(name='origin')
origin.push()

print("les fichiers ont été poussés vers GitHub.")

# Ouvrir automatiquement le fichier index.html dans le navigateur par défaut
webbrowser.open('file://' + os.path.realpath("index.html"))