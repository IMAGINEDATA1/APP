import streamlit as st
import numpy as np
import pickle
import requests
import random

# Charger les données
movies = pickle.load(open("movies_list_tuto.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# Fonction pour récupérer les posters à partir de l'API TMDb
def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=db38952c66997974559ef641200fc25e&append_to_response=credits".format(movie_id)
    data = requests.get(url).json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

# Fonction de recommandation générique
def recommend_similar_movies(data_column, query, column_name, result_limit=5):
    matching_movies = movies[movies[data_column].str.contains(query, case=False, na=False)]

    if not matching_movies.empty:
        index = matching_movies.index
        distances = np.median(similarity[index], axis=0)
        sorted_indices = np.argsort(distances)[::-1]
        num_recommendations = min(result_limit, len(sorted_indices))
        movies_list = sorted_indices[1:num_recommendations + 1]

        recommend_movie = []
        recommend_poster = []
        for i in movies_list:
            movie_id = movies.iloc[i].tconst
            recommend_movie.append(movies.iloc[i].primaryTitle)
            recommend_poster.append(fetch_poster(movie_id))
        return recommend_movie, recommend_poster
    else:
        st.warning(f"Aucun film trouvé avec le '{column_name}' '{query}'.")

# Fonction de recommandation par titre de film
def recommend_similar_movies_by_title(title):
    return recommend_similar_movies('primaryTitle', title, 'titre')

# Fonction de recommandation par genre
def recommend_similar_movies_by_genre(genre):
    return recommend_similar_movies('genres', genre, 'genre')

# Fonction de recommandation par acteur
def recommend_similar_movies_by_actor(actor):
    return recommend_similar_movies('actors', actor, 'acteur')

# Fonction de recommandation par directeur
def recommend_similar_movies_by_director(director):
    return recommend_similar_movies('directors', director, 'directeur')

# Affichage des détails du film
def display_movie_popup(title):
    matching_movies = movies[movies['primaryTitle'].str.contains(title, case=False, na=False)]

    if not matching_movies.empty:
        index = matching_movies.index
        distances = np.median(similarity[index], axis=0)
        sorted_indices = np.argsort(distances)[::-1]
        num_recommendations = min(1, len(sorted_indices))
        movies_list = sorted_indices[1:num_recommendations + 1]

        for i in movies_list:
            movie_id = movies.iloc[i].tconst
            movie = movies.iloc[i]
            st.markdown(f"**Titre:** {movie['primaryTitle']}")
            st.markdown(f"**Tagline:** {movie['tagline']}")
            st.markdown(f"**Aperçu:** {movie['overview']}")
            st.write(f"**Note IMDb:** {movie['vote_average']}")
            st.write(f"**Durée:** {movie['runtimeMinutes']}")
            st.write(f"**Genre:** {movie['genres']}")
            st.write(f"**Acteurs:** {movie['actors']}")
            st.write(f"**Directeurs:** {movie['directors']}")
            st.write(f"**Société de production:** {movie['prod_name']}")
    else:
        st.warning(f"Aucun film trouvé avec le titre '{title}'.")

# Titre de la page
st.header("Movie Recommender System")

# Options de recherche
search_options = ["Titre", "Genre", "Acteur"]
search_option = st.selectbox("Choisir une option de recherche", search_options)

# Champ de saisie en fonction de l'option choisie
user_input = st.text_input(f"Ecrivez votre mot clé {search_option.lower()}", "")

# Bouton de recherche
if st.button("Rechercher"):
    if user_input:
        recommend_function = None
        if search_option == "Titre":
            recommend_function = recommend_similar_movies_by_title
        elif search_option == "Genre":
            recommend_function = recommend_similar_movies_by_genre
        elif search_option == "Acteur":
            recommend_function = recommend_similar_movies_by_actor

        if recommend_function:
            movie_name, movie_poster = recommend_function(user_input)

            if movie_name:
                st.text(movie_name[0])
                st.image(movie_poster[0], width=300, use_column_width=False)

                st.title("Recommandations :")

                # Affichage des recommandations
                col1, col2, col3, col4, col5 = st.columns(5)
                for i in range(min(5, len(movie_name))):
                    with col1 if i == 0 else col2 if i == 1 else col3 if i == 2 else col4 if i == 3 else col5:
                        st.image(movie_poster[i])
                        st.button(movie_name[i], on_click=display_movie_popup(movie_name[i]))
            else:
                st.warning("Aucun résultat trouvé.")
else: 
    st.warning("Aucun résultat trouvé.")

# Display other recommendations
random_recos = random.sample(movies['primaryTitle'].tolist(), 4)
display_recommandations(random_recos, movies)

# Function to display recommendations
def display_recommandations(random_recos, movies):
    st.subheader("Autres films recommandés:")

    # Utiliser des colonnes pour afficher les recommandations en ligne
    cols = st.columns(len(random_recos))

    # Afficher les informations sur chaque recommandation
    for col, index in zip(cols, random_recos):
        movie_title = movies.loc[index, 'primaryTitle']
        movie_details = fetch_poster(movies.loc[index, 'tconst'])
        col.image(f"https://image.tmdb.org/t/p/w200/{movie_details.get('poster_path')}", width=150, use_column_width=False)
        col.button(movie_title, key=f"button_{index}", on_click=display_movie_popup, args=(movie_details,))
