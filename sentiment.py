import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk import word_tokenize
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import stopwords
import string

nltk_data = ['vader_lexicon', 'punkt', 'stopwords']
for package in nltk_data:
    try:
        nltk.data.find(package)
    except LookupError:
        nltk.download(package)

sia = SentimentIntensityAnalyzer()

TRAINING_SENTENCES = [
    ('The lecturer was helpful and the exam schedule is fair.', 'positive'),
    ('I am happy with the course registration process.', 'positive'),
    ('My complaint has not been addressed and I feel ignored.', 'negative'),
    ('The lab equipment is broken and nobody responds.', 'negative'),
    ('The complaint description is okay but not urgent.', 'neutral'),
    ('I do not know if this issue will be resolved.', 'neutral'),
    ('The classroom is clean and the staff are supportive.', 'positive'),
    ('I have waited too long for academic approval.', 'negative'),
    ('The department website is fine.', 'neutral'),
    ('The response process seems slow but acceptable.', 'neutral'),
]


def extract_features(text):
    words = [w.lower() for w in word_tokenize(text) if w.isalpha()]
    stop = set(stopwords.words('english'))
    return {word: True for word in words if word not in stop}


classifier = NaiveBayesClassifier.train([(extract_features(text), label) for text, label in TRAINING_SENTENCES])


def normalize_sentiment(score):
    if score >= 0.05:
        return 'positive'
    if score <= -0.05:
        return 'negative'
    return 'neutral'


def analyze_text(text):
    if not text or not text.strip():
        return 'neutral', 0.0

    cleaned = text.strip()
    vader_scores = sia.polarity_scores(cleaned)
    sentiment = normalize_sentiment(vader_scores['compound'])
    return sentiment, round(vader_scores['compound'], 3)
