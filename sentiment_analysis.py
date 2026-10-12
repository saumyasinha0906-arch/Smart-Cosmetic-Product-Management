from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from preprocessing import clean_text


# Create VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(review):
    """
    Analyze the sentiment of a customer review.

    Returns:
        sentiment: Positive / Negative / Neutral
        score: Compound sentiment score
    """

    # Clean the review
    cleaned_review = clean_text(review)

    # Calculate sentiment scores
    scores = analyzer.polarity_scores(cleaned_review)

    compound_score = scores["compound"]

    # Classify sentiment
    if compound_score >= 0.05:
        sentiment = "Positive"

    elif compound_score <= -0.05:
        sentiment = "Negative"

    else:
        sentiment = "Neutral"

    return sentiment, compound_score


if __name__ == "__main__":

    reviews = [
        "Amazing lipstick with beautiful pigmentation!",
        "The product is terrible and makes my skin very dry.",
        "The product is okay, nothing special."
    ]

    for review in reviews:

        sentiment, score = analyze_sentiment(review)

        print("\nReview:", review)
        print("Sentiment:", sentiment)
        print("Score:", round(score, 3))