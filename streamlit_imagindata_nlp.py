import streamlit as st
import requests
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
import re
import string
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import cosine_similarity
import random
import base64
import pickle

nltk.download('punkt')
nltk.download('stopwords')

def main():
    st.set_page_config(page_title="🎥 App de Recommandation de films", page_icon=":🎞️:", layout="wide", initial_sidebar_state="expanded")
    st.title("App de Recommandation de films")

    # Charger les DataFrames depuis l'URL
    df_actors = pd.read_csv("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/t_algo_actors")
    df_directors = pd.read_csv("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/t_algo_directors")
    df_NLP = pd.read_csv("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/t_mainNLP")
    df_prod = pd.read_csv("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/t_algo_prod")
    df_matrice = pd.read_pickle("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/df_matrice.pkl")

    # Barre de recherche pour la recommandation
    search_option_mapping = {"Titre": "primaryTitle", "Acteur": "primaryName", "Réalisateur": "primaryName", "Genre": "genres", "Année": "startYear", "Société de production": "prod_name"}
    search_option = st.selectbox("Choisir une option de recherche", list(search_option_mapping.keys()))
    user_input_film = None

    if search_option in search_option_mapping:
        column_name = search_option_mapping[search_option]
        default_value = df_actors[column_name].iloc[0] + df_directors[column_name].iloc[0] + df_prod[column_name].iloc[0] + df_NLP[column_name].iloc[0]
        user_input_film = st.text_input(f"Choisir un(e) {search_option.lower()}", default_value)

    if st.button("Rechercher"):
        if user_input_film:

            similarity = pickle.load(open("df_matrice.pkl", 'rb'))
            movie_list = df_NLP['primaryTitle'].values

            # Appeler la fonction pour obtenir les films similaires
            similar_movies = get_similar_movies(user_input_film, similarity, df_NLP)

            # Affichage des recommandations avec boutons
            display_recommandations(similar_movies, df_NLP, user_input_film, search_option)

        else:
            st.warning("Aucun résultat trouvé.")

            # 4 films choisis aléatoirement comme recommandations
            random_recos = random.sample(df_NLP['primaryTitle'].tolist(), 4)
            display_recommandations(random_recos, df_NLP, user_input_film, search_option)

# Fonction pour obtenir les films similaires en fonction du mot-clé
def get_similar_movies(user_input_film, similarity, df_NLP):
    # Recherche films avec mot-cle
    user_input_film = df_NLP[df_NLP['primaryTitle'].str.contains(user_input_film, case=False, na=False)]
    st.subheader("Votre choix :")
    
    if not user_input_film.empty:
        # Obtenir indices films corresp.
        movie_indices = user_input_film.index
        st.write(f"Indices des films : {movie_indices}")
        
        # Sélectionner les vecteurs de similarité correspondants aux films choisis
        selected_similarity = similarity.iloc[movie_indices]
        
        # Calculer la similarité cosinus pour tous les films
        distances = cosine_similarity(selected_similarity, similarity)
        st.write(f"Distances : {distances}")
        
        # Tri + obtenir indices des films reco
        sorted_indices = np.argsort(distances[0])[::-1]
        st.write(f"Indices triés : {sorted_indices}")
        
        # Sélection des 5 premiers indices
        num_recommendations = min(5, len(sorted_indices))
        movies_list = [(index, distances[0][index]) for index in sorted_indices[:num_recommendations]]
        return movies_list
    else:
        return []

# Fonction pour Affichage des recommandations
def display_recommandations(movies_list, df_NLP, user_input_film, search_option):
    st.subheader("Autres films recommandés:")

    # Utiliser des colonnes pour afficher les recommandations en ligne
    cols = st.columns(len(movies_list))

    # Afficher les informations sur chaque recommandation
    for col, (index, similarity_score) in zip(cols, movies_list):
        movie_title = df_NLP.loc[index, 'primaryTitle']
        col.image(f"https://image.tmdb.org/t/p/w200/{get_movie_details(df_NLP.loc[index, 'tconst']).get('poster_path')}", width=150, use_column_width=False)
        col.write(f"**{movie_title}**")
        col.button("Voir détails", key=f"button_{index}", on_click=display_movie_popup, args=(df_NLP.loc[index, 'tconst'],))

# Fonction pour obtenir les informations d'un film à partir de l'API TMDb
def get_movie_details(movie_id):
    api_key = "db38952c66997974559ef641200fc25e"
    base_url = "https://api.themoviedb.org/3/movie/"
    endpoint = str(movie_id)
    url = f"{base_url}{endpoint}?api_key={api_key}&append_to_response=credits"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Fonction pour afficher les détails du film dans une fenêtre pop-up
def display_movie_popup(movie_id):
    movie_details = get_movie_details(movie_id)
    st.image(f"https://image.tmdb.org/t/p/w200/{movie_details.get('poster_path')}", width=150, use_column_width=False)
    display_movie_details(movie_details)

# Fonction pour afficher les détails du film à partir de l'API TMDb
def display_movie_details(movie_details):
    if movie_details:
        st.markdown(f"**Titre:** {movie_details.get('title')}")
        st.markdown(f"**Tagline:** {movie_details.get('tagline')}")
        st.markdown(f"**Aperçu:** {movie_details.get('overview')}")
        st.write(f"**Note IMDb:** {movie_details.get('vote_average')}")
        st.write(f"**Nombre de votes:** {movie_details.get('vote_count')}")
        st.write(f"**Durée:** {movie_details.get('runtime')} minutes")
        st.write(f"**Genre:** {', '.join([genre['name'] for genre in movie_details.get('genres', [])])}")

        st.write("**Acteurs:**")
        cast_members = movie_details.get('credits', {}).get('cast', [])[:3]
        for cast_member in cast_members:
            st.write(f"- {cast_member.get('name')}")

        st.write("**Réalisateurs:**")
        crew_members = movie_details.get('credits', {}).get('crew', [])
        directors = [crew_member.get('name') for crew_member in crew_members if crew_member.get('job') == 'Director']
        for director in directors:
            st.write(f"- {director}")
    #else:
        #st.info("Film non trouvé ou erreur lors de la récupération des détails.")

if __name__ == "__main__":
    main()

st.subheader("Bonne séance ! 🍿🍿🍿 ")
