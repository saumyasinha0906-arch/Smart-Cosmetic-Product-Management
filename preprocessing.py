import re
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Load English stopwords
STOP_WORDS = set(stopwords.words("english"))

# Create lemmatizer
lemmatizer = WordNetLemmatizer()


def clean_text(text):
    """
    Cleans a customer review before sentiment/opinion analysis.
    """

    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove special characters and numbers
    text = re.sub(r"[^a-zA-Z\s]", "", text)

    # Split into words
    words = text.split()

    # Remove stopwords and lemmatize
    words = [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in STOP_WORDS
    ]

    # Join words again
    cleaned_text = " ".join(words)

    return cleaned_text


if __name__ == "__main__":

    review = "The lipstick has amazing pigmentation, but it makes my lips very dry!"

    print("Original Review:")
    print(review)

    print("\nCleaned Review:")
    print(clean_text(review))