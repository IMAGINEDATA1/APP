import streamlit as st
import requests
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import random

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

# Fonction pour afficher les détails du film à partir de l'API TMDb
def display_movie_details(movie_details):
    if movie_details:
        st.image(f"https://image.tmdb.org/t/p/w500/{movie_details.get('poster_path')}", caption=movie_details.get('title'), use_column_width=True)
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
    else:
        st.info("Film non trouvé ou erreur lors de la récupération des détails.")


# Fonction pour afficher le choix de l'utilisateur
def display_user_choice(user_film):
    st.subheader("Votre choix:")
    user_movie_details = get_movie_details(user_film['tconst'].values[0])
    display_movie_details(user_movie_details)

# Fonction pour afficher les recommandations
def display_recommendations(neighbors_indices, df_KNN):
    st.subheader("Autres films recommandés:")
    for index in neighbors_indices:
        movie_title = df_KNN.loc[index, 'primaryTitle']
        st.write(f"- {movie_title}")
        # Affichage réduit de l'image
        st.image(f"https://image.tmdb.org/t/p/w200/{df_KNN.loc[index, 'poster_path']}", use_column_width=False)

# Fonction principale
def main():
    st.set_page_config(page_title="🎥 App de Recommandation de films", page_icon=":🎞️:", layout="wide", initial_sidebar_state="expanded")
    st.title("App de Recommandation de films")

    # Charger le DataFrame depuis l'URL
    df_KNN = pd.read_csv("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/t_KNN")

    # Barre de recherche pour la recommandation
    user_input_film = st.text_input("Recherchez par titre, acteur ou réalisateur", df_KNN['primaryTitle'].iloc[0])

    if user_input_film:
        user_film_features = df_KNN.loc[df_KNN['primaryTitle'] == user_input_film, ['startYear', 'original_language', 'Action', 'Adventure', 'Biography', 'Crime', 'Mystery']]

        # Entraîner le modèle sur l'ensemble complet des caractéristiques
        X_all = df_KNN[['startYear', 'original_language', 'Action', 'Adventure', 'Biography', 'Crime', 'Mystery']].values
        modelNN = NearestNeighbors(n_neighbors=5)
        modelNN.fit(X_all)

        # Définition des voisins les plus proches du film saisi par l'utilisateur
        neighbors = modelNN.kneighbors(user_film_features.values)
        neighbors_indices = neighbors[1][0]

        # Filtrer les voisins pour ne prendre que ceux avec le même 'original_language'
        user_language = user_film_features['original_language'].values[0]
        filtered_neighbors_indices = [index for index in neighbors_indices if df_KNN.loc[index, 'original_language'] == user_language]

        # Affichage du choix de l'utilisateur et des recommandations
        display_user_choice(user_film_features)
        display_recommendations(filtered_neighbors_indices, df_KNN)

    else:
        st.warning("Aucun résultat trouvé pour la recherche spécifiée.")

        # 4 films choisis aléatoirement comme recommandations
        random_recos_indices = random.sample(range(len(df_KNN['primaryTitle'])), 4)
        display_recommendations(random_recos_indices, df_KNN)

    st.subheader("Bonne séance ! 🍿🍿🍿 ")

if __name__ == "__main__":
    main()
