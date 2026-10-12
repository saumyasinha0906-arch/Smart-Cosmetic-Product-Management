from pathlib import Path
import pandas as pd


# ============================================================
# SMART COSMETIC PRODUCT MANAGEMENT
# FULL DATASET PREPARATION + CATEGORY INTEGRATION
# ============================================================

print("\n" + "=" * 75)
print("SMART COSMETIC PRODUCT MANAGEMENT")
print("FULL DATASET PREPARATION")
print("REVIEW + PRODUCT CATEGORY INTEGRATION")
print("=" * 75)


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_DIR = BASE_DIR / "dataset"

PRODUCT_FILE = DATASET_DIR / "product_info.csv"

OUTPUT_FILE = DATASET_DIR / "cosmetic_reviews.csv"


print("\nDataset folder:")
print(DATASET_DIR)


# ============================================================
# 2. CHECK PRODUCT FILE
# ============================================================

if not PRODUCT_FILE.exists():

    print("\n❌ ERROR: product_info.csv not found.")

    print("\nExpected location:")
    print(PRODUCT_FILE)

    exit()


print("\n✓ product_info.csv found")


# ============================================================
# 3. FIND ALL REVIEW FILES
# ============================================================

review_files = sorted(
    DATASET_DIR.glob("reviews_*.csv")
)


if not review_files:

    print("\n❌ ERROR: No review CSV files found.")

    exit()


print("\n" + "-" * 75)
print("REVIEW FILES FOUND")
print("-" * 75)


for file in review_files:

    print("✓", file.name)


# ============================================================
# 4. LOAD ALL REVIEW FILES
# ============================================================

dataframes = []

total_loaded = 0


print("\n" + "-" * 75)
print("LOADING ALL REVIEWS")
print("-" * 75)


for file in review_files:

    print(f"\nLoading: {file.name}")

    try:

        df = pd.read_csv(
            file,
            low_memory=False
        )

        print(
            f"Rows loaded: {len(df):,}"
        )

        total_loaded += len(df)

        dataframes.append(df)

    except Exception as error:

        print(
            f"❌ Error loading {file.name}"
        )

        print(error)


if not dataframes:

    print("\n❌ No review data could be loaded.")

    exit()


# ============================================================
# 5. COMBINE REVIEWS
# ============================================================

print("\n" + "-" * 75)
print("COMBINING REVIEW FILES")
print("-" * 75)


reviews = pd.concat(
    dataframes,
    ignore_index=True
)


print(
    f"Total review rows loaded: {len(reviews):,}"
)


# ============================================================
# 6. CHECK REQUIRED REVIEW COLUMNS
# ============================================================

required_review_columns = [
    "review_text",
    "rating",
    "product_name",
    "brand_name",
    "product_id"
]


missing_columns = [
    column
    for column in required_review_columns
    if column not in reviews.columns
]


if missing_columns:

    print("\n❌ Missing review columns:")

    for column in missing_columns:

        print("-", column)

    exit()


print("\n✓ Required review columns found")


# ============================================================
# 7. LOAD PRODUCT INFORMATION
# ============================================================

print("\n" + "-" * 75)
print("LOADING PRODUCT INFORMATION")
print("-" * 75)


try:

    products = pd.read_csv(
        PRODUCT_FILE,
        low_memory=False
    )

except Exception as error:

    print("\n❌ Error loading product_info.csv")
    print(error)

    exit()


print(
    f"Products loaded: {len(products):,}"
)


# ============================================================
# 8. CHECK PRODUCT COLUMNS
# ============================================================

required_product_columns = [
    "product_id",
    "primary_category",
    "secondary_category",
    "tertiary_category"
]


missing_product_columns = [
    column
    for column in required_product_columns
    if column not in products.columns
]


if missing_product_columns:

    print("\n❌ Missing product columns:")

    for column in missing_product_columns:

        print("-", column)

    exit()


print("\n✓ Required product category columns found")


# ============================================================
# 9. KEEP ONLY REQUIRED PRODUCT INFORMATION
# ============================================================

product_categories = products[
    [
        "product_id",
        "primary_category",
        "secondary_category",
        "tertiary_category"
    ]
].copy()


# ============================================================
# 10. REMOVE DUPLICATE PRODUCT IDs
# ============================================================

product_categories = product_categories.drop_duplicates(
    subset=["product_id"],
    keep="first"
)


# ============================================================
# 11. MERGE CATEGORY INFORMATION
# ============================================================

print("\n" + "-" * 75)
print("MATCHING REVIEWS WITH PRODUCT CATEGORIES")
print("-" * 75)


reviews["product_id"] = (
    reviews["product_id"]
    .astype(str)
    .str.strip()
)


product_categories["product_id"] = (
    product_categories["product_id"]
    .astype(str)
    .str.strip()
)


reviews = reviews.merge(
    product_categories,
    on="product_id",
    how="left"
)


print(
    "✓ Product category information merged"
)


# ============================================================
# 12. CREATE STANDARDIZED DATASET
# ============================================================

print("\n" + "-" * 75)
print("CREATING STANDARDIZED DATASET")
print("-" * 75)


final_data = pd.DataFrame()


# ============================================================
# REVIEW ID
# ============================================================

final_data["review_id"] = range(
    1,
    len(reviews) + 1
)


# ============================================================
# PRODUCT ID
# ============================================================

final_data["product_id"] = (
    reviews["product_id"]
    .fillna("Unknown")
    .astype(str)
)


# ============================================================
# PRODUCT NAME
# ============================================================

final_data["product_name"] = (
    reviews["product_name"]
    .fillna("Unknown Product")
    .astype(str)
    .str.strip()
)


# ============================================================
# BRAND
# ============================================================

final_data["brand"] = (
    reviews["brand_name"]
    .fillna("Unknown Brand")
    .astype(str)
    .str.strip()
)


# ============================================================
# PRIMARY CATEGORY
# ============================================================

final_data["primary_category"] = (
    reviews["primary_category"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)


# ============================================================
# SECONDARY CATEGORY
# ============================================================

final_data["secondary_category"] = (
    reviews["secondary_category"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)


# ============================================================
# TERTIARY CATEGORY
# ============================================================

final_data["tertiary_category"] = (
    reviews["tertiary_category"]
    .fillna("Unknown")
    .astype(str)
    .str.strip()
)


# ============================================================
# RATING
# ============================================================

final_data["rating"] = pd.to_numeric(
    reviews["rating"],
    errors="coerce"
)


# ============================================================
# REVIEW TEXT
# ============================================================

final_data["review"] = (
    reviews["review_text"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# 13. CLEAN DATA
# ============================================================

print("\n" + "-" * 75)
print("CLEANING DATA")
print("-" * 75)


original_count = len(final_data)


# ------------------------------------------------------------
# Remove empty reviews
# ------------------------------------------------------------

before = len(final_data)


final_data = final_data[
    final_data["review"] != ""
]


removed_empty = before - len(final_data)


print(
    f"Empty reviews removed: {removed_empty:,}"
)


# ------------------------------------------------------------
# Remove invalid ratings
# ------------------------------------------------------------

before = len(final_data)


final_data = final_data[
    final_data["rating"].between(1, 5)
]


removed_invalid = before - len(final_data)


print(
    f"Invalid ratings removed: {removed_invalid:,}"
)


# ------------------------------------------------------------
# Remove duplicate reviews
# ------------------------------------------------------------

before = len(final_data)


final_data = final_data.drop_duplicates(
    subset=["review"],
    keep="first"
)


removed_duplicates = before - len(final_data)


print(
    f"Duplicate reviews removed: {removed_duplicates:,}"
)


# ============================================================
# 14. RESET INDEX
# ============================================================

final_data = final_data.reset_index(
    drop=True
)


# ============================================================
# 15. RECREATE REVIEW IDs
# ============================================================

final_data["review_id"] = range(
    1,
    len(final_data) + 1
)


# ============================================================
# 16. CONVERT RATING TO INTEGER
# ============================================================

final_data["rating"] = (
    final_data["rating"]
    .astype(int)
)


# ============================================================
# 17. FINAL COLUMN ORDER
# ============================================================

final_data = final_data[
    [
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
]


# ============================================================
# 18. SAVE FINAL CSV
# ============================================================

print("\n" + "-" * 75)
print("SAVING FINAL DATASET")
print("-" * 75)


final_data.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)


# ============================================================
# 19. DATASET SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("✅ DATASET PREPARATION COMPLETED")
print("=" * 75)


print(
    f"\nOriginal review rows: {original_count:,}"
)


print(
    f"Final usable reviews: {len(final_data):,}"
)


print(
    f"\nUnique products: "
    f"{final_data['product_name'].nunique():,}"
)


print(
    f"Unique brands: "
    f"{final_data['brand'].nunique():,}"
)


print(
    f"Primary categories: "
    f"{final_data['primary_category'].nunique():,}"
)


# ============================================================
# 20. CATEGORY DISTRIBUTION
# ============================================================

print("\n" + "-" * 75)
print("PRIMARY CATEGORY DISTRIBUTION")
print("-" * 75)


category_counts = (
    final_data["primary_category"]
    .value_counts()
)


print(
    category_counts.to_string()
)


# ============================================================
# 21. RATING DISTRIBUTION
# ============================================================

print("\n" + "-" * 75)
print("RATING DISTRIBUTION")
print("-" * 75)


rating_counts = (
    final_data["rating"]
    .value_counts()
    .sort_index()
)


for rating, count in rating_counts.items():

    print(
        f"{rating} ⭐ : {count:,} reviews"
    )


# ============================================================
# 22. DATASET SIZE
# ============================================================

file_size_mb = (
    OUTPUT_FILE.stat().st_size
    / (1024 * 1024)
)


print("\n" + "-" * 75)
print("DATASET FILE")
print("-" * 75)


print(
    f"CSV size: {file_size_mb:.2f} MB"
)


print(
    f"Location: {OUTPUT_FILE}"
)


# ============================================================
# 23. FIRST 5 ROWS
# ============================================================

print("\n" + "-" * 75)
print("FIRST 5 ROWS")
print("-" * 75)


print(
    final_data.head(5).to_string(
        index=False
    )
)


# ============================================================
# 24. COMPLETION
# ============================================================

print("\n" + "=" * 75)

print("🎉 FULL DATASET READY")

print("=" * 75)

print(
    "\nFinal dataset:"
)

print(
    "dataset\\cosmetic_reviews.csv"
)

print(
    "\nThe dataset now contains:"
)

print("✓ All available reviews")
print("✓ Product information")
print("✓ Brand information")
print("✓ Primary category")
print("✓ Secondary category")
print("✓ Tertiary category")
print("✓ Ratings")
print("✓ Review text")

print("\nNext step:")
print("We will optimize sentiment analysis before processing all 969K+ reviews.")

print("=" * 75)