import pandas as pd
import altair as alt
import os
from datetime import datetime


#fonction pour charger tous les données
def load_covid_data(folder_path):
    """Charge tous les fichiers CSV du dossier"""
    all_data = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            df['Date'] = pd.to_datetime(datetime.strptime(filename.split('.')[0], '%m-%d-%Y').date())
            all_data.append(df)
    
    return pd.concat(all_data, ignore_index=True)
#fonction pour sélectionner les données de l'Union européenne
def prepare_eu_data(df):
    """Prépare les données pour l'Union européenne"""
    eu_countries = [
        'Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 
        'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 
        'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 
        'Netherlands', 'Poland', 'Portugal', 'Romania', 'Slovakia', 'Slovenia', 
        'Spain', 'Sweden'
    ]
    
    #filtrer pour les pays de l'UE
    eu_data = df[df['Country_Region'].isin(eu_countries)]
    
    #ajouter des colonnes pour le filtrage
    eu_data['Mois'] = eu_data['Date'].dt.month
    eu_data['Annee'] = eu_data['Date'].dt.year
    
    #grouper par date et pays et les cas confirmés
    grouped_data = eu_data.groupby(['Date', 'Country_Region', 'Mois', 'Annee'])['Confirmed'].sum().reset_index()
    
    #calculer le total pour l'Europe
    total_europe = eu_data.groupby(['Date', 'Mois', 'Annee'])['Confirmed'].sum().reset_index()
    total_europe['Country_Region'] = 'Total Europe'
    
    #combiner les données
    combined_data = pd.concat([grouped_data, total_europe], ignore_index=True)
    
    return combined_data

def create_interactive_dashboard(grouped_data):
    """Crée un tableau de bord interactif avec Altair"""
    #convertir "Annee" en chaînes de caractères
    # grouped_data['Mois_str'] = grouped_data['Mois'].astype(str)
    grouped_data['Annee_str'] = grouped_data['Annee'].astype(str)
    
    #créer le graphique de base
    countries = sorted(grouped_data['Country_Region'].unique())
    
    #sélecteurs interactifs avec alt.param
    # month_options = ['All'] + [str(m) for m in range(1,12)]
    # month_param = alt.param(
    #     name='Mois',
    #     bind=alt.binding_select(options=month_options, name='Mois'),
    #     value='All'
    # )
    
    year_options = ['All'] + [str(y) for y in sorted(grouped_data['Annee'].unique())]
    year_param = alt.param(
        name='Annee',
        bind=alt.binding_select(options=year_options, name='Année'),
        value='All'
    )
    
    # #filtre pour le mois
    # month_filter = (month_param == 'All') | (alt.datum.Mois_str == month_param)
    
    #filtre pour l'année
    year_filter = (year_param == 'All') | (alt.datum.Annee_str == year_param)
    
    #sélection des pays via la légende
    selection = alt.selection_point(fields=['Country_Region'], bind='legend')
    
    base = alt.Chart(grouped_data).encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Confirmed:Q', title='Nombre de cas confirmés'),
        color='Country_Region:N'
    ).add_params(
        year_param, selection #month_param, 
    ).transform_filter(
    #     month_filter
    # ).transform_filter(
        year_filter
    ).transform_filter(
        selection
    )
    
    #courbe des cas confirmés
    confirmed_line = base.mark_line(opacity=0.8).encode(
        tooltip=['Country_Region', 'Date', 'Confirmed']
    )
    
    #créer le graphique final
    chart = confirmed_line.properties(
        title='Évolution des cas COVID-19 dans l\'Union Européenne',
        width=800,
        height=500
    )
    
    #sauvegarder le graphique
    chart.save('covid_altair.html')
    
    return chart

def main():
    folder_path = r'C:\Users'
    
    #charger les données
    df = load_covid_data(folder_path)
    
    #préparer les données de l'UE
    eu_data = prepare_eu_data(df)
    
    #créer le tableau de bord
    dashboard = create_interactive_dashboard(eu_data)
    
    print("Graphique généré avec succès : covid_altair.html")

if __name__ == "__main__":
    main()
