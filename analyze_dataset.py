from pathlib import Path
import sqlite3
import pandas as pd

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from opinion_mining import analyze_opinions


# ============================================================
# SMART COSMETIC PRODUCT MANAGEMENT
# FULL DATASET SENTIMENT + OPINION ANALYSIS
# ============================================================


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = (
    BASE_DIR
    / "dataset"
    / "cosmetic_reviews.csv"
)

DATABASE_PATH = (
    BASE_DIR
    / "cosmetic_products.db"
)


# ============================================================
# SETTINGS
# ============================================================

CHUNK_SIZE = 10000


# ============================================================
# SENTIMENT ANALYZER
# ============================================================

analyzer = SentimentIntensityAnalyzer()


# ============================================================
# SENTIMENT ANALYSIS
# ============================================================

def get_sentiment(review):

    if not isinstance(review, str):

        return "Neutral", 0.0

    review = review.strip()

    if not review:

        return "Neutral", 0.0

    scores = analyzer.polarity_scores(review)

    compound_score = scores["compound"]


    if compound_score >= 0.05:

        sentiment = "Positive"

    elif compound_score <= -0.05:

        sentiment = "Negative"

    else:

        sentiment = "Neutral"


    return sentiment, compound_score


# ============================================================
# CREATE / RESET DATABASE
# ============================================================

def create_database():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()


    # --------------------------------------------------------
    # Products table
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (

            product_id INTEGER PRIMARY KEY AUTOINCREMENT,

            product_name TEXT NOT NULL,

            brand TEXT NOT NULL,

            category TEXT,

            price REAL

        )
    """)


    # --------------------------------------------------------
    # Reviews table
    # --------------------------------------------------------

    cursor.execute("""
        DROP TABLE IF EXISTS reviews
    """)


    cursor.execute("""
        CREATE TABLE reviews (

            review_id INTEGER PRIMARY KEY,

            product_id TEXT,

            product_name TEXT,

            brand TEXT,

            primary_category TEXT,

            secondary_category TEXT,

            tertiary_category TEXT,

            rating INTEGER,

            review TEXT,

            sentiment TEXT,

            sentiment_score REAL,

            aspects TEXT

        )
    """)


    connection.commit()

    connection.close()


# ============================================================
# GET TOTAL REVIEWS
# ============================================================

def get_total_reviews():

    total = 0

    for chunk in pd.read_csv(
        DATASET_PATH,
        usecols=["review_id"],
        chunksize=CHUNK_SIZE,
        low_memory=False
    ):

        total += len(chunk)


    return total


# ============================================================
# MAIN ANALYSIS
# ============================================================

def analyze_dataset():

    print("\n" + "=" * 70)

    print(
        "SMART COSMETIC PRODUCT MANAGEMENT"
    )

    print(
        "FULL DATASET SENTIMENT & OPINION ANALYSIS"
    )

    print("=" * 70)


    # ========================================================
    # CHECK DATASET
    # ========================================================

    if not DATASET_PATH.exists():

        print("\n❌ Dataset not found:")

        print(DATASET_PATH)

        return


    print("\nDataset:")

    print(DATASET_PATH)


    # ========================================================
    # RESET DATABASE
    # ========================================================

    print("\nCreating database...")

    create_database()

    print(
        "✓ Database created with updated structure"
    )


    # ========================================================
    # COUNT REVIEWS
    # ========================================================

    print("\nCounting reviews...")

    total_reviews = get_total_reviews()


    print(
        f"Total reviews to analyze: "
        f"{total_reviews:,}"
    )


    # ========================================================
    # STATISTICS
    # ========================================================

    positive_count = 0

    negative_count = 0

    neutral_count = 0

    processed = 0


    # ========================================================
    # COLUMNS
    # ========================================================

    columns = [

        "review_id",

        "product_id",

        "product_name",

        "brand",

        "primary_category",

        "secondary_category",

        "tertiary_category",

        "rating",

        "review"

    ]


    # ========================================================
    # START PROCESSING
    # ========================================================

    print("\n" + "-" * 70)

    print("STARTING ANALYSIS")

    print("-" * 70)


    for chunk in pd.read_csv(

        DATASET_PATH,

        usecols=columns,

        chunksize=CHUNK_SIZE,

        low_memory=False

    ):


        # ----------------------------------------------------
        # Sentiment
        # ----------------------------------------------------

        sentiments = []

        sentiment_scores = []

        aspects = []


        for review in chunk["review"]:


            sentiment, score = get_sentiment(
                review
            )


            detected_aspects = analyze_opinions(
                review
            )


            sentiments.append(
                sentiment
            )


            sentiment_scores.append(
                score
            )


            aspects.append(
                ", ".join(
                    detected_aspects
                )
            )


        # ----------------------------------------------------
        # Add results
        # ----------------------------------------------------

        chunk["sentiment"] = sentiments

        chunk["sentiment_score"] = (
            sentiment_scores
        )

        chunk["aspects"] = aspects


        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        positive_count += int(
            (
                chunk["sentiment"]
                == "Positive"
            ).sum()
        )


        negative_count += int(
            (
                chunk["sentiment"]
                == "Negative"
            ).sum()
        )


        neutral_count += int(
            (
                chunk["sentiment"]
                == "Neutral"
            ).sum()
        )


        # ----------------------------------------------------
        # Update progress
        # ----------------------------------------------------

        processed += len(chunk)


        percentage = (
            processed
            / total_reviews
            * 100
        )


        print(
            f"Processed: "
            f"{processed:,} / "
            f"{total_reviews:,} "
            f"({percentage:.1f}%)"
        )


        # ----------------------------------------------------
        # Save chunk
        # ----------------------------------------------------

        connection = sqlite3.connect(
            DATABASE_PATH
        )


        chunk.to_sql(

            "reviews",

            connection,

            if_exists="append",

            index=False

        )


        connection.close()


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("\n" + "=" * 70)

    print(
        "✅ FULL DATASET ANALYSIS COMPLETED"
    )

    print("=" * 70)


    print(
        f"\nTotal reviews processed: "
        f"{processed:,}"
    )


    print(
        f"Positive reviews: "
        f"{positive_count:,}"
    )


    print(
        f"Negative reviews: "
        f"{negative_count:,}"
    )


    print(
        f"Neutral reviews: "
        f"{neutral_count:,}"
    )


    # ========================================================
    # PERCENTAGES
    # ========================================================

    if processed > 0:

        print("\nSentiment percentages:")


        print(
            f"Positive: "
            f"{positive_count / processed * 100:.2f}%"
        )


        print(
            f"Negative: "
            f"{negative_count / processed * 100:.2f}%"
        )


        print(
            f"Neutral: "
            f"{neutral_count / processed * 100:.2f}%"
        )


    # ========================================================
    # DATABASE
    # ========================================================

    print("\nDatabase:")

    print(DATABASE_PATH)


    print("\n✓ Sentiment analysis saved")

    print("✓ Opinion mining results saved")

    print("✓ Product information saved")

    print("✓ Category information saved")


    print("\n" + "=" * 70)

    print("NEXT STEP:")

    print("streamlit run app.py")

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    analyze_dataset()