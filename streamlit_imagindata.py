#VERSION AVEC LISTE DEROULANTE

import streamlit as st
import requests
import pandas as pd
from sklearn.neighbors import NearestNeighbors

def main():
    st.set_page_config(page_title="🎥 App de Recommandation de films", page_icon=":🎞️:", layout="wide", initial_sidebar_state="expanded")
    st.title("App de Recommandation de films")

    # Charger le DataFrame depuis l'URL
    df_KNN = pd.read_csv("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/t_KNN")

    # Barre de recherche pour la recommandation
    search_option_mapping = {"Titre": "primaryTitle", "Acteur": "primaryName", "Réalisateur": "primaryName", "Genre": "genre1", "Année": "startYear"}
    search_option = st.selectbox("Choisir une option de recherche", list(search_option_mapping.keys()))
    user_input_film = None

    if search_option in search_option_mapping:
        column_name = search_option_mapping[search_option]
        user_input_film = st.text_input(f"Choisir un(e) {search_option.lower()}", df_KNN[column_name].iloc[0])

    if st.button("Rechercher"):
        if user_input_film:
            # Utiliser user_input_film et search_option pour filtrer le DataFrame
            filtered_df = filter_dataframe(df_KNN, search_option, user_input_film)

            if not filtered_df.empty:
                user_film_features = filtered_df[['startYear', 'original_language', 'Action', 'Adventure', 'Biography', 'Crime', 'Mystery']]

                # Entraîner le modèle sur les caractéristiques filtrées
                X_filtered = filtered_df[['startYear', 'original_language', 'Action', 'Adventure', 'Biography', 'Crime', 'Mystery']].values
                modelNN = NearestNeighbors(n_neighbors=5)
                modelNN.fit(X_filtered)

                # Définition des voisins les plus proches du film saisi par l'utilisateur
                neighbors = modelNN.kneighbors(user_film_features.values)
                neighbors_indices = neighbors[1][0]

                # Filtrer les voisins pour ne prendre que ceux avec le même 'original_language'
                user_language = user_film_features['original_language'].values[0]
                filtered_neighbors_indices = [index for index in neighbors_indices if filtered_df.loc[index, 'original_language'] == user_language]

                # Exclusion du film saisi par l'utilisateur de la liste des recommandations
                filtered_neighbors_indices = [index for index in filtered_neighbors_indices if index != filtered_df[filtered_df[column_name] == user_input_film].index[0]]

                # Affichage du choix de l'utilisateur
                display_user_choice(user_input_film, search_option, df_KNN)

                # Affichage des recommandations avec boutons
                display_recommandations(filtered_neighbors_indices, df_KNN)

            else:
                st.warning("Aucun résultat trouvé.")

        else:
            st.warning("Veuillez saisir une valeur.")


# Fonction pour filtrer le DataFrame en fonction de l'option de recherche
def filter_dataframe(df_KNN, search_option, user_input_film):
    if search_option in ["Acteur", "Réalisateur"]:
        return df_KNN[df_KNN['primaryName'] == user_input_film]

    elif search_option == "Titre":
        return df_KNN[df_KNN['primaryTitle'] == user_input_film]

    elif search_option == "Genre":
        return df_KNN[df_KNN['genre1'] == user_input_film]

    elif search_option == "Année":
        return df_KNN[df_KNN['startYear'] == int(user_input_film)]

    # elif search_option == "Société de production":
    #     return df[df['prod_name'] == user_input_film]

    return df_KNN


# Fonction pour Affichage du choix de l'utilisateur
def display_user_choice(user_input_film, search_option, df_KNN):
    st.subheader("Votre choix:")
    if not df_KNN.empty:
        if search_option in ["Acteur", "Réalisateur", "Titre"]:
            selected_movie = df_KNN[df_KNN[search_option.lower()] == user_input_film].iloc[0]
            user_movie_details = get_movie_details(selected_movie['tconst'])
        elif search_option == "Genre":
            selected_movie = df_KNN[df_KNN['genre1'] == user_input_film].iloc[0]
            user_movie_details = get_movie_details(selected_movie['tconst'])
        elif search_option == "Année":
            selected_movie = df_KNN[df_KNN['startYear'] == int(user_input_film)].iloc[0]
            user_movie_details = get_movie_details(selected_movie['tconst'])
        # elif search_option == "Société de production":
        #     selected_movie = df_KNN[df_KNN['prod_name'] == user_input_film].iloc[0]
        #     user_movie_details = get_movie_details(selected_movie['tconst'])
        else:
            user_movie_details = None

        if user_movie_details:
            display_movie_details(user_movie_details)
        else:
            st.info("Film non trouvé ou erreur lors de la récupération des détails.")
    else:
        st.info("Aucun résultat trouvé.")

# Fonction pour Affichage des recommandations

def display_recommandations(filtered_neighbors_indices, df_KNN):
    st.subheader("Autres films recommandés:")

    # Utiliser des colonnes pour afficher les recommandations en ligne
    cols = st.columns(len(filtered_neighbors_indices))

    # Afficher les informations sur chaque recommandation
    for col, index in zip(cols, filtered_neighbors_indices):
        movie_title = df_KNN.loc[index, 'primaryTitle']
        movie_details = get_movie_details(df_KNN.loc[index, 'tconst'])
        col.image(f"https://image.tmdb.org/t/p/w200/{movie_details.get('poster_path')}", width=150, use_column_width=False)
        col.button(movie_title, key=f"button_{index}", on_click=display_movie_popup, args=(movie_details,))


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
def display_movie_popup(movie_details):
    st.image(f"https://image.tmdb.org/t/p/w200/{movie_details.get('poster_path')}", width=150, use_column_width=False)
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

# Fonction pour afficher les détails du film à partir de l'API TMDb
def display_movie_details(movie_details):
    if movie_details:
        st.image(f"https://image.tmdb.org/t/p/w200/{movie_details.get('poster_path')}", width=150, use_column_width=False)
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

if __name__ == "__main__":
    main()

st.subheader("Bonne séance ! 🍿🍿🍿 ")
