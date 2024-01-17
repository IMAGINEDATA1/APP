import streamlit as st
from streamlit.components.v1 import components
from googletrans import Translator
import pandas as pd
from sklearn.neighbors import NearestNeighbors
import requests
import random

# Définir le thème personnalisé
st.set_page_config(
    page_title="🎥 App de Recommandation de films",
    page_icon=":🎞️:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction pour traduire le texte
def translate_page(page_content, target_language='en'):
    translator = Translator()
    translated_content = translator.translate(page_content, dest=target_language)
    return translated_content.text

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

# Fonction pour afficher les résultats de recommandation de manière structurée
def display_recommendations(neighbors_names):
    st.subheader(f"Résultats de recommandation:")
    for i, movie_title in enumerate(neighbors_names, start=1):
        st.write(f"{i}. {movie_title}")

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

def main():
    st.title("App de Recommandation de films")

    # Contenu initial
    page_content = """
    Bienvenue dans cette application de recommandation de films.
    Essayez de cliquer sur le bouton de traduction pour voir le contenu dans une autre langue!
    """

    # Affichage du contenu initial
    st.markdown(page_content)

    # Bouton de traduction
    if st.button("Traduire en anglais"):
        translated_content = translate_page(page_content, target_language='en')
        st.markdown(translated_content)

    # Charger le DataFrame depuis l'URL
    df_KNN = pd.read_csv("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/t_KNN")

    # Barre de recherche avec autocomplétion
    user_input_film = st.text_input("Tapez votre recherche", " ")
    selected_movie = st.selectbox("Résultats de recherche", df_KNN['primaryTitle'].unique(), key='search_results')

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

        # Exclusion du film saisi par l'utilisateur de la liste des recommandations
        filtered_neighbors_indices = [index for index in filtered_neighbors_indices if index != df_KNN[df_KNN['primaryTitle'] == user_input_film].index[0]]

        # Résultats recommandations
        neighbors_names = df_KNN['primaryTitle'].iloc[filtered_neighbors_indices]
        display_recommendations(neighbors_names)

        # Requête API pour obtenir les détails du film sélectionné
        movie_details = get_movie_details(df_KNN.loc[df_KNN['primaryTitle'] == user_input_film, 'tconst'].values[0])
        display_movie_details(movie_details)

    else:
        # Si le film n'a pas été trouvé
        st.write(f"\nLe film '{user_input_film}' n'a pas été trouvé dans la base de données.")

        # 4 films choisis aléatoirement comme recommandations
        random_recos = random.sample(df_KNN['primaryTitle'].tolist(), 4)

        st.write("Vous ne trouvez pas ? Voici quelques unes de mes idées :")
        for i, movie_title in enumerate(random_recos, start=1):
            st.write(f"{i}. {movie_title}")

    # SOUS-TITRE
    st.subheader("Bonne séance ! 🍿🍿🍿 ")

if __name__ == "__main__":
    main()
