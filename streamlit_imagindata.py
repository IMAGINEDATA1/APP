# -*- coding: utf-8 -*-
"""streamlit_imagindata.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1T_P50jsy4XBqe_DMLVNmY1FoAPRNbIb9
"""


import streamlit as st
import numpy as np
import seaborn as sns
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import requests
from googletrans import Translator

#Fonction pour traduire le texte
def translate_text(text, target_lang):
    translator = Translator()
    translation = translator.translate(text, dest=target_lang)
    return translation.text

#CHARGER LES DATAFRAMES


df_KNN = pd.read_csv('C:/Users/Bolaty/Desktop/WILD CODE SCHOOL/Projet/Projet 2/STREAMLIT/PROJET2/t_KNN.csv', sep="/t")

#Définir le thème personnalisé

st.set_page_config(page_title="🎥 App de Recommandation de films", page_icon=":🎞️:", layout="wide", initial_sidebar_state="expanded")

page_bg_img = """
<style>
[data-testid = "stAppViewContainer"] {
primaryColor: "#3498db";
background-color: "#f0f0f0";
secondaryBackgroundColor: "#d3d3d3";
textColor: "#2c3e50";
font: "sans-serif";
opacity: 0.8;
background-image: radial-gradient(#444cf7 0.5px, #e5e5f7 0.5px);
background-size: 10px 10px; }
</style>
"""


# TITRE
st.title("🎥 App de Recommandation de films")

# SOUS TITRE
st.header("Dis moi quels sont tes goûts et je te ferai découvrir de nouveaux films 💡🎬")



# REQUETE API


# Fonction pour obtenir les informations d'un film à partir de l'API TMDb
def get_movie_details(movie_id):
    api_key = "db38952c66997974559ef641200fc25e"
    base_url = "https://api.themoviedb.org/3/movie/"
    endpoint = str(movie_id)
    url = f"{base_url}{endpoint}?api_key={api_key}"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


        # Obtenir les informations du film depuis l'API TMDb
        tmdb_movie_details = get_movie_details(movie_details['MovieDB_ID'])

        if tmdb_movie_details:
            # Afficher l'image du film
            st.image(f"https://image.tmdb.org/t/p/w500/{tmdb_movie_details['poster_path']}", caption=movie_title, use_column_width=True)

            # Afficher le titre, la tagline et l'aperçu en survol de la souris
            st.markdown(f"**Titre:** {tmdb_movie_details['primaryTitle']}")
            st.markdown(f"**Tagline:** {tmdb_movie_details['tagline']}")
            st.markdown(f"**Aperçu:** {tmdb_movie_details['overview']}")

            # Afficher d'autres détails du film
            st.write(f"**Note IMDb:** {movie_details['averageRating']}")
            st.write(f"**Nombre de votes:** {tmdb_movie_details['vote_count']}")
            st.write(f"**Durée:** {tmdb_movie_details['runtimeMinutes']} minutes")
            st.write(f"**Genre:** {', '.join([genre['primaryName'] for genre in tmdb_movie_details['genre1']])}")

            # Acteurs
            st.write("**Acteurs:**")
            for cast_member in tmdb_movie_details['credits']['cast'][:3]:
                st.write(f"- {cast_member['primaryName']}")

            # Réalisateurs
            st.write("**Réalisateurs:**")
            for crew_member in tmdb_movie_details['credits']['crew']:
                if crew_member['job'] == 'Director':
                    st.write(f"- {crew_member['primaryName']}")

                else:
                    st.info("Commencez à taper pour rechercher des films.")





# Création d'une barre de recherche avec autocomplétion et KNN


# Création de la recommandation basée sur KNN

X = df_KNN[['runtimeMinutes', 'original_language', 'Action', 'Adventure', 'Biography', 'Crime', 'Mystery', 'averageRating', 'numVotes', 'popularity', 'vote_average', 'vote_count', 'score_popularity_film', 'starYear']]
X = X.dropna()

# Standardisation : pour les mettre à la même échelle afin que le modèle soit plus performant
scaler = StandardScaler()
X = scaler.fit(df_KNN[['runtimeMinutes', 'original_language', 'Action', 'Adventure', 'Biography', 'Crime', 'Mystery', 'averageRating', 'numVotes', 'popularity', 'vote_average', 'vote_count', 'score_popularity_film', 'starYear']])
X = scaler.transform(df_KNN[['runtimeMinutes', 'original_language', 'Action', 'Adventure', 'Biography', 'Crime', 'Mystery', 'averageRating', 'numVotes', 'popularity', 'vote_average', 'vote_count', 'score_popularity_film','starYear']])

modelNN = NearestNeighbors(n_neighbors=5)
modelNN.fit(X)

# Créer une barre de recherche avec autocomplétion

user_input_film  = st.text_input("Tapez votre recherche", " ")

# Check si nom du film est dans le df
if user_input_film in df_KNN['primaryTitle'].values:
    # Définition des voisins les plus proches du film saisi par l'utilisateur
    neighbors = modelNN.kneighbors(df_KNN.loc[df_KNN['primaryTitle'] == user_input_film, ['runtimeMinutes', 'original_language', 'Action', 'Adventure', 'Biography', 'Crime', 'Mystery', 'averageRating', 'numVotes', 'popularity', 'vote_average', 'vote_count', 'score_popularity_film']])
    neighbors_indices = neighbors[1][0]

    # Exclusion du film saisi par l'utilisateur de la liste des recommandations
    neighbors_indices = [index for index in neighbors_indices if index != df_KNN[df_KNN['primaryTitle'] == user_input_film].index[0]]

    # Résultats recommandations
    neighbors_names = df_KNN['primaryTitle'].iloc[neighbors_indices]

    st.write(f"\nPour : {user_input_film}")
    st.write(neighbors_names)

else:
  # Si le film n'a pas été trouvé
    st.write(f"\nLe film '{user_input_film}' n'a pas été trouvé dans la base de données.")

   # 4 films choisis aléatoirement comme recommandations
    random_recos= random.sample(df_KNN['primaryTitle'].tolist(), 4)

    st.write("Vous ne trouvez pas ? Voici quelques unes de mes idées :")
    st.write(random_recos)




# SOUS-TITRE
st.subheader("Bonne séance ! 🍿🍿🍿 ")