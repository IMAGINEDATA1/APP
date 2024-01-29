import streamlit as st
import numpy as np
import pandas as pd
import pickle
import requests

# Charger les données
movies = pickle.load(open("df_NLP.pkl", "rb"))
similarity = pickle.load(open("df_matrice.pkl", "rb"))

# Fonction pour récupérer les posters à partir de l'API TMDb
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=db38952c66997974559ef641200fc25e&append_to_response=credits".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path
# Fonction de recommandation par titre de film
def recommend_similar_movies_by_title(title):
    matching_movies = movies[movies['primaryTitle'].str.contains(title, case=False, na=False)]
    if not matching_movies.empty:
        index = matching_movies.index
        distances = np.median(similarity[index], axis=0)
        sorted_indices = np.argsort(distances)[::-1]
        num_recommendations = min(5, len(sorted_indices))
        movies_list = sorted_indices[1:num_recommendations + 1]
        recommend_movie = []
        recommend_poster = []
        for i in movies_list:
            movie_id = movies.iloc[i].tconst
            recommend_movie.append(movies.iloc[i].primaryTitle)
            recommend_poster.append(fetch_poster(movie_id))
        return recommend_movie, recommend_poster
    else:
        st.warning(f"Aucun film trouvé avec le titre '{title}'.")
# Fonction de recommandation par genre
def recommend_similar_movies_by_genre(genre):
    matching_movies_genre = movies[movies['genres'].str.contains(genre, case=False, na=False)]
    if not matching_movies_genre.empty:
        index = matching_movies_genre.index
        distances = np.median(similarity[index], axis=0)
        sorted_indices = np.argsort(distances)[::-1]
        num_recommendations = min(5, len(sorted_indices))
        movies_list = sorted_indices[1:num_recommendations + 1]
        recommend_movie = []
        recommend_poster = []
        for i in movies_list:
            movie_id = movies.iloc[i].tconst
            recommend_movie.append(movies.iloc[i].genres)
            recommend_poster.append(fetch_poster(movie_id))
        return recommend_movie, recommend_poster
    else:
        st.warning(f"Aucun film trouvé avec le genre '{genre}'.")
# Fonction de recommandation par acteur
def recommend_similar_movies_by_actor(actor):
    matching_movies_actor = movies[movies['actors'].str.contains(actor, case=False, na=False)]
    if not matching_movies_actor.empty:
        index = matching_movies_actor.index
        distances = np.median(similarity[index], axis=0)
        sorted_indices = np.argsort(distances)[::-1]
        num_recommendations = min(5, len(sorted_indices))
        movies_list = sorted_indices[1:num_recommendations + 1]
        recommend_movie = []
        recommend_poster = []
        for i in movies_list:
            movie_id = movies.iloc[i].tconst
            recommend_movie.append(movies.iloc[i].genres)
            recommend_poster.append(fetch_poster(movie_id))
        return recommend_movie, recommend_poster
    else:
        st.warning(f"Aucun film trouvé avec le genre '{actor}'.")
# Titre de la page
st.header("Movie Recommender System")
# Options de recherche
search_options = ["Titre", "Genre", "Acteur"]
search_option = st.selectbox("Choisir une option de recherche", search_options)
# Champ de saisie en fonction de l'option choisie
user_input = st.text_input(f"Entrez le {search_option.lower()}", "")
# Bouton de recherche
if st.button("Rechercher"):
    if user_input:
        if search_option == "Titre":
            movie_name, movie_poster = recommend_similar_movies_by_title(user_input)
        elif search_option == "Genre":
            movie_name, movie_poster = recommend_similar_movies_by_genre(user_input)
        elif search_option == "Acteur":
            movie_name, movie_poster = recommend_similar_movies_by_actor(user_input)
        # Affichage des recommandations
        col1, col2, col3, col4, col5 = st.columns(5)
        for i in range(min(5, len(movie_name))):
            with col1:
                st.text(movie_name[i])
                st.image(movie_poster[i])
    else:
        st.warning("Veuillez entrer une valeur de recherche.")
