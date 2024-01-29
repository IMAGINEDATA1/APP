#VERSION AVEC LISTE DEROULANTE VF

import streamlit as st
import requests
import pandas as pd
import nltk
from nltk.corpus import stopwords
import re
import string
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import cosine_similarity
import random



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
            # Conversion en str des colonnes
            columns_to_convert = ['primaryTitle', 'overview', 'tagline', 'actors', 'directors', 'prod_name', 'tags_NLP']
            df_NLP[columns_to_convert] = df_NLP[columns_to_convert].astype(str)

            # Fonction nettoyage
            def clean(text):
                tokens = nltk.word_tokenize(text.lower())
                tokens_clean = []
                additional_stopwords = ["'s", "ca", "n't"]
                stopwordsenglish = set(stopwords.words('english') + additional_stopwords)

                for word in tokens:
                    word = word.strip(string.punctuation)
                    if word and word not in stopwordsenglish and not re.match(r'^\W+$', word):
                        tokens_clean.append(word)
                cleaned_text = ' '.join(tokens_clean)
                return cleaned_text

            df_NLP['tags_NLP'] = df_NLP['tags_NLP'].apply(clean)

            # Transforme un texte en vecteur sur la base du comptage de la fréquence de chaque mot.
            cv = CountVectorizer(stop_words='english')
            cv.fit_transform(df_NLP['tags_NLP']).toarray().shape
            vectors = cv.fit_transform(df_NLP['tags_NLP']).toarray()

            # Choix Stemming
            ps = SnowballStemmer("english")

            def stem(text):
                y = []
                for i in text.split():
                    y.append(ps.stem(i))
                return " ".join(y)

            df_NLP['tags_NLP'] = df_NLP['tags_NLP'].apply(stem)

            similarity = cosine_similarity(vectors)
            movies_list = sorted(list(enumerate(similarity[0])), reverse=True, key=lambda x: x[1])[1:6]

            # Affichage du choix de l'utilisateur
            recommend_similar_movies(user_input_film, search_option, df_NLP)

            # Affichage des recommandations avec boutons
            display_recommandations(movies_list, df_NLP)

        else:
            st.warning("Aucun résultat trouvé.")

            # 4 films choisis aléatoirement comme recommandations
            random_recos = random.sample(df_NLP['primaryTitle'].tolist(), 4)
            display_recommandations(random_recos, df_NLP)

# NLP Fonction pour filtrer le DataFrame en fonction de l'option de recherche





# Fonction pour Affichage des recommandations
# calcul recos
def recommend_similar_movies(keyword):
    # Recherche films avec mot-cle
    user_input_film = df_NLP[df_NLP['primaryTitle'].str.contains(keyword, case=False, na=False)]
    if not user_input_film.empty:
        # Obtenir indices films corresp.
        movie_indices = user_input_film.index
        user_movie_details = get_movie_details(movie_indices['tconst'])
        # Calcul similarite cosinus pour films corresp
        distances = np.median(similarity[movie_indices], axis=0)
        # Tri + obtenir indices des films reco
        sorted_indices = np.argsort(distances)[::-1]
        # Sélection des 5 premiers indices
        num_recommendations = min(5, len(sorted_indices))
        movies_list = sorted_indices[1:num_recommendations + 1]
        user_movie_details = get_movie_details(movies_list['tconst'])

        # Affichage
        for i in user_movie_details:
            st.write(df_NLP.iloc[i].primaryTitle)
    else:
        st.write(f"Aucun film trouvé avec le mot-clé '{keyword}'.")



def display_recommandations(random_recos, df_NLP):
    st.subheader("Autres films recommandés:")

    # Utiliser des colonnes pour afficher les recommandations en ligne
    cols = st.columns(len(random_recos))

    # Afficher les informations sur chaque recommandation
    for col, index in zip(cols, random_recos):
        movie_title = df_NLP.loc[index, 'primaryTitle']
        movie_details = get_movie_details(df_NLP.loc[index, 'tconst'])
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
