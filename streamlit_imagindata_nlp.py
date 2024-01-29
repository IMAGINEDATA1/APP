import streamlit as st
import pandas as pd
import nltk
from nltk.corpus import stopwords
import re
import string
from sklearn.feature_extraction.text import CountVectorizer
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')
nltk.download('stopwords')

    # Charger les DataFrames depuis l'URL
    df_actors = pd.read_csv("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/t_algo_actors")
    df_directors = pd.read_csv("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/t_algo_directors")
    df_NLP = pd.read_csv("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/t_mainNLP")
    df_prod = pd.read_csv("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/t_algo_prod")
    df_matrice = pd.read_pickle("https://raw.githubusercontent.com/IMAGINEDATA1/APP/main/df_matrice.pkl")

# Fonction de nettoyage
def clean(text):
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
    return cleaned_text

# Fonction de stemming
def stem(text):
def stem(text):
   y=[]
   for i in text.split():
       y.append(ps.stem(i))
   return " ".join(y)
df_NLP['tags_NLP'] = df_NLP['tags_NLP'].apply(stem)
    return " ".join(y)

def main():
    st.title("App de Recommandation de Films")

    # Ajoutez les composants Streamlit pour la recherche et l'affichage des résultats
    user_input = st.text_input("Rechercher des films similaires", "indiana")
    if st.button("Rechercher"):
        # Nettoyage et stemming du texte d'entrée
        cleaned_input = stem(clean(user_input))

        # Mesure de la similarité avec les films existants
        matching_movies = df_NLP[df_NLP['primaryTitle'].str.contains(cleaned_input, case=False, na=False)]
        if not matching_movies.empty:
            movie_indices = matching_movies.index
            distances = np.median(similarity[movie_indices], axis=0)
            sorted_indices = np.argsort(distances)[::-1]
            num_recommendations = min(5, len(sorted_indices))
            movies_list = sorted_indices[1:num_recommendations + 1]

            # Affichage des résultats
            st.subheader("Films recommandés:")
            for i in movies_list:
                st.write(df_NLP.iloc[i].primaryTitle)
        else:
            st.warning(f"Aucun film trouvé avec le mot-clé '{cleaned_input}'.")

if __name__ == "__main__":
    main()
