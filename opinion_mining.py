import re

# Cosmetic product aspects
ASPECTS = {
    "price": [
        "price", "expensive", "cheap", "affordable", "cost", "value"
    ],

    "quality": [
        "quality", "good", "poor", "excellent", "amazing"
    ],

    "packaging": [
        "packaging", "package", "bottle", "container", "box"
    ],

    "texture": [
        "texture", "smooth", "sticky", "creamy", "lightweight",
        "heavy", "dry", "oily"
    ],

    "fragrance": [
        "fragrance", "smell", "scent", "odor"
    ],

    "pigmentation": [
        "pigmentation", "pigment", "color", "colour"
    ],

    "coverage": [
        "coverage", "cover"
    ],

    "moisturization": [
        "moisturizing", "moisturising", "moisturizer",
        "hydrating", "hydration"
    ],

    "skin": [
        "skin", "dry skin", "oily skin", "sensitive skin"
    ],

    "performance": [
        "works", "performance", "effective", "protection"
    ]
}


def extract_aspects(review):
    """
    Identify cosmetic-related aspects mentioned in a review.
    """

    review_lower = review.lower()

    found_aspects = []

    for aspect, keywords in ASPECTS.items():

        for keyword in keywords:

            if re.search(r"\b" + re.escape(keyword) + r"\b", review_lower):

                found_aspects.append(aspect)

                break

    return list(set(found_aspects))


def analyze_opinions(review):

    aspects = extract_aspects(review)

    return aspects


if __name__ == "__main__":

    review = (
        "The lipstick has amazing pigmentation "
        "but the texture is dry and the price is expensive."
    )

    print("Review:")
    print(review)

    print("\nDetected Aspects:")

    aspects = analyze_opinions(review)

    for aspect in aspects:
        print("-", aspect)