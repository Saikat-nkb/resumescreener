import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from app.utils import extract_keywords

nltk.download("punkt")
nltk.download("stopwords")

stop_words = set(stopwords.words("english"))

def extract_jd_keywords(text, return_vector=False):
    tokens = word_tokenize(text.lower())
    filtered = [word for word in tokens if word.isalpha() and word not in stop_words]
    
    keyword_string = " ".join(filtered)

    if return_vector:
        vectorizer = TfidfVectorizer()
        vector = vectorizer.fit_transform([keyword_string]).toarray()[0]
        return filtered, vector

    return filtered
