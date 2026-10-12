import sqlite3
import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path

from sentiment_analysis import analyze_sentiment
from opinion_mining import analyze_opinions

from project_management import (
    get_wbs,
    get_schedule,
    get_milestones,
    get_resources,
    get_cost_estimation,
    get_risks,
    get_project_summary
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "cosmetic_products.db"


st.set_page_config(
    page_title="Smart Cosmetic Product Management",
    page_icon="💄",
    layout="wide"
)


# ============================================================
# LOGIN / LOGOUT
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""


def login_page():

    st.title("💄 Smart Cosmetic Product Management")

    st.subheader("🔐 Login")

    st.markdown(
        """
        Please enter your username and password to access
        the Cosmetic Analytics System.
        """
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "🔐 Login",
        use_container_width=True
    ):

        if username == "admin" and password == "admin123":

            st.session_state.logged_in = True
            st.session_state.username = username

            st.success(
                "✅ Login successful!"
            )

            st.rerun()

        else:

            st.error(
                "❌ Invalid username or password."
            )


# ------------------------------------------------------------
# SHOW LOGIN PAGE IF NOT LOGGED IN
# ------------------------------------------------------------

if not st.session_state.logged_in:

    login_page()

    st.stop()


# ============================================================
# DATABASE FUNCTIONS
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def database_exists():
    return DATABASE_PATH.exists()


def reviews_table_exists():

    if not database_exists():
        return False

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='reviews'
    """)

    result = cursor.fetchone()

    connection.close()

    return result is not None


def products_table_exists():

    if not database_exists():
        return False

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='products'
    """)

    result = cursor.fetchone()

    connection.close()

    return result is not None


# ============================================================
# DATABASE INDEXES
# ============================================================

def create_indexes():

    if not reviews_table_exists():
        return

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reviews_sentiment
        ON reviews(sentiment)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reviews_brand
        ON reviews(brand)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reviews_primary_category
        ON reviews(primary_category)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reviews_rating
        ON reviews(rating)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reviews_product_name
        ON reviews(product_name)
    """)

    connection.commit()
    connection.close()


# ============================================================
# BASIC DATABASE STATISTICS
# ============================================================

@st.cache_data(ttl=300)
def get_total_reviews():

    if not reviews_table_exists():
        return 0

    connection = get_connection()

    query = """
        SELECT COUNT(*)
        FROM reviews
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return int(result.iloc[0, 0])


@st.cache_data(ttl=300)
def get_total_products():

    if not reviews_table_exists():
        return 0

    connection = get_connection()

    query = """
        SELECT COUNT(DISTINCT product_id)
        FROM reviews
        WHERE product_id IS NOT NULL
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return int(result.iloc[0, 0])


@st.cache_data(ttl=300)
def get_total_brands():

    if not reviews_table_exists():
        return 0

    connection = get_connection()

    query = """
        SELECT COUNT(DISTINCT brand)
        FROM reviews
        WHERE brand IS NOT NULL
        AND brand != ''
    """

    result = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return int(result.iloc[0, 0])


# ============================================================
# FILTER OPTIONS
# ============================================================

@st.cache_data(ttl=300)
def get_brands():

    connection = get_connection()

    query = """
        SELECT DISTINCT brand
        FROM reviews
        WHERE brand IS NOT NULL
        AND brand != ''
        ORDER BY brand
    """

    data = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return data["brand"].tolist()


@st.cache_data(ttl=300)
def get_primary_categories():

    connection = get_connection()

    query = """
        SELECT DISTINCT primary_category
        FROM reviews
        WHERE primary_category IS NOT NULL
        AND primary_category != ''
        ORDER BY primary_category
    """

    data = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return data["primary_category"].tolist()


@st.cache_data(ttl=300)
def get_secondary_categories():

    connection = get_connection()

    query = """
        SELECT DISTINCT secondary_category
        FROM reviews
        WHERE secondary_category IS NOT NULL
        AND secondary_category != ''
        ORDER BY secondary_category
    """

    data = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return data["secondary_category"].tolist()


# ============================================================
# FILTER BUILDER
# ============================================================

def build_filter_query(
    brand=None,
    primary_category=None,
    secondary_category=None
):

    conditions = []
    parameters = []

    if brand and brand != "All":

        conditions.append(
            "brand = ?"
        )

        parameters.append(brand)

    if primary_category and primary_category != "All":

        conditions.append(
            "primary_category = ?"
        )

        parameters.append(primary_category)

    if secondary_category and secondary_category != "All":

        conditions.append(
            "secondary_category = ?"
        )

        parameters.append(secondary_category)

    if conditions:

        where_clause = (
            " WHERE "
            + " AND ".join(conditions)
        )

    else:

        where_clause = ""

    return where_clause, parameters


# ============================================================
# FILTERED KPIs
# ============================================================

@st.cache_data(ttl=300)
def get_filtered_statistics(
    brand,
    primary_category,
    secondary_category
):

    connection = get_connection()

    where_clause, parameters = build_filter_query(
        brand,
        primary_category,
        secondary_category
    )

    query = f"""
        SELECT
            COUNT(*) AS total_reviews,

            SUM(
                CASE
                    WHEN sentiment = 'Positive'
                    THEN 1
                    ELSE 0
                END
            ) AS positive_reviews,

            SUM(
                CASE
                    WHEN sentiment = 'Negative'
                    THEN 1
                    ELSE 0
                END
            ) AS negative_reviews,

            SUM(
                CASE
                    WHEN sentiment = 'Neutral'
                    THEN 1
                    ELSE 0
                END
            ) AS neutral_reviews,

            AVG(rating) AS average_rating

        FROM reviews
        {where_clause}
    """

    data = pd.read_sql_query(
        query,
        connection,
        params=parameters
    )

    connection.close()

    row = data.iloc[0]

    return {
        "total": int(row["total_reviews"] or 0),
        "positive": int(row["positive_reviews"] or 0),
        "negative": int(row["negative_reviews"] or 0),
        "neutral": int(row["neutral_reviews"] or 0),
        "average_rating": float(row["average_rating"] or 0)
    }


# ============================================================
# SENTIMENT DISTRIBUTION
# ============================================================

@st.cache_data(ttl=300)
def get_sentiment_distribution(
    brand,
    primary_category,
    secondary_category
):

    connection = get_connection()

    where_clause, parameters = build_filter_query(
        brand,
        primary_category,
        secondary_category
    )

    query = f"""
        SELECT
            sentiment,
            COUNT(*) AS count

        FROM reviews

        {where_clause}

        GROUP BY sentiment
        ORDER BY count DESC
    """

    data = pd.read_sql_query(
        query,
        connection,
        params=parameters
    )

    connection.close()

    return data


# ============================================================
# RATING DISTRIBUTION
# ============================================================

@st.cache_data(ttl=300)
def get_rating_distribution(
    brand,
    primary_category,
    secondary_category
):

    connection = get_connection()

    where_clause, parameters = build_filter_query(
        brand,
        primary_category,
        secondary_category
    )

    query = f"""
        SELECT
            rating,
            COUNT(*) AS count

        FROM reviews

        {where_clause}

        GROUP BY rating
        ORDER BY rating
    """

    data = pd.read_sql_query(
        query,
        connection,
        params=parameters
    )

    connection.close()

    return data


# ============================================================
# PRODUCT SENTIMENT
# ============================================================

@st.cache_data(ttl=300)
def get_product_sentiment(
    brand,
    primary_category,
    secondary_category
):

    connection = get_connection()

    where_clause, parameters = build_filter_query(
        brand,
        primary_category,
        secondary_category
    )

    query = f"""
        SELECT
            product_name,
            sentiment,
            COUNT(*) AS count

        FROM reviews

        {where_clause}

        AND product_name IS NOT NULL
        AND product_name != ''

        GROUP BY
            product_name,
            sentiment

        ORDER BY count DESC

        LIMIT 30
    """

    # Fix query when there is no existing WHERE clause
    if not where_clause:

        query = """
            SELECT
                product_name,
                sentiment,
                COUNT(*) AS count

            FROM reviews

            WHERE product_name IS NOT NULL
            AND product_name != ''

            GROUP BY
                product_name,
                sentiment

            ORDER BY count DESC

            LIMIT 30
        """

    data = pd.read_sql_query(
        query,
        connection,
        params=parameters
    )

    connection.close()

    return data


# ============================================================
# RECENT REVIEWS
# ============================================================

@st.cache_data(ttl=300)
def get_recent_reviews(
    brand,
    primary_category,
    secondary_category,
    limit=100
):

    connection = get_connection()

    where_clause, parameters = build_filter_query(
        brand,
        primary_category,
        secondary_category
    )

    query = f"""
        SELECT
            review_id,
            product_name,
            brand,
            primary_category,
            secondary_category,
            rating,
            review,
            sentiment,
            sentiment_score,
            aspects

        FROM reviews

        {where_clause}

        ORDER BY review_id DESC

        LIMIT {limit}
    """

    data = pd.read_sql_query(
        query,
        connection,
        params=parameters
    )

    connection.close()

    return data


# ============================================================
# ASPECT ANALYSIS
# ============================================================

ASPECT_LIST = [
    "price",
    "quality",
    "packaging",
    "texture",
    "fragrance",
    "pigmentation",
    "coverage",
    "moisturization",
    "skin",
    "performance"
]


@st.cache_data(ttl=300)
def get_aspect_counts(
    brand,
    primary_category,
    secondary_category
):

    connection = get_connection()

    where_clause, parameters = build_filter_query(
        brand,
        primary_category,
        secondary_category
    )

    # If no filters are selected
    if not where_clause:

        where_clause = " WHERE 1=1 "

    aspect_counts = []

    for aspect in ASPECT_LIST:

        query = f"""
            SELECT COUNT(*)
            FROM reviews

            {where_clause}

            AND LOWER(aspects)
            LIKE ?
        """

        search_term = f"%{aspect}%"

        result = pd.read_sql_query(
            query,
            connection,
            params=parameters + [search_term]
        )

        count = int(
            result.iloc[0, 0]
        )

        aspect_counts.append(
            {
                "Aspect": aspect.title(),
                "Reviews": count
            }
        )

    connection.close()

    return pd.DataFrame(
        aspect_counts
    )


# ============================================================
# PRODUCT MANAGEMENT
# ============================================================

def add_product_to_database(
    product_name,
    brand,
    category,
    price
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO products
        (
            product_name,
            brand,
            category,
            price
        )

        VALUES (?, ?, ?, ?)
    """, (
        product_name,
        brand,
        category,
        price
    ))

    connection.commit()
    connection.close()


def load_product_catalogue(
    search_text=""
):

    connection = get_connection()

    if search_text:

        query = """
            SELECT
                product_id,
                product_name,
                brand,
                category,
                price

            FROM products

            WHERE
                product_name LIKE ?
                OR brand LIKE ?

            ORDER BY product_id DESC

            LIMIT 100
        """

        search_pattern = (
            f"%{search_text}%"
        )

        data = pd.read_sql_query(
            query,
            connection,
            params=[
                search_pattern,
                search_pattern
            ]
        )

    else:

        query = """
            SELECT
                product_id,
                product_name,
                brand,
                category,
                price

            FROM products

            ORDER BY product_id DESC

            LIMIT 100
        """

        data = pd.read_sql_query(
            query,
            connection
        )

    connection.close()

    return data


# ============================================================
# ADD MANUAL REVIEW
# ============================================================

def save_manual_review(
    product_id,
    product_name,
    brand,
    primary_category,
    secondary_category,
    tertiary_category,
    rating,
    review,
    sentiment,
    sentiment_score,
    aspects
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COALESCE(
                MAX(review_id),
                0
            ) + 1

        FROM reviews
    """)

    next_review_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO reviews
        (
            review_id,
            product_id,
            product_name,
            brand,
            primary_category,
            secondary_category,
            tertiary_category,
            rating,
            review,
            sentiment,
            sentiment_score,
            aspects
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        next_review_id,
        product_id,
        product_name,
        brand,
        primary_category,
        secondary_category,
        tertiary_category,
        rating,
        review,
        sentiment,
        sentiment_score,
        aspects
    ))

    connection.commit()
    connection.close()

    return next_review_id


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("💄 Cosmetic Analytics")

st.sidebar.markdown(
    """
    ### Smart Cosmetic Product Management

    **Integrated Modules**

    🔹 ASTMA  
    🔹 Enterprise Systems  
    🔹 ITPM
    """
)

# ============================================================
# LOGIN USER INFORMATION + LOGOUT
# ============================================================

st.sidebar.divider()

st.sidebar.write(
    f"👤 **Logged in as:** {st.session_state.username}"
)

if st.sidebar.button(
    "🚪 Logout",
    use_container_width=True
):

    st.session_state.logged_in = False
    st.session_state.username = ""

    st.rerun()


page = st.sidebar.radio(
    "Select Module",
    [
        "📊 Analytics Dashboard",
        "🛍️ Product Management",
        "📝 Review Management",
        "📅 ITPM Project Management"
    ]
)


# ============================================================
# DATABASE CHECK
# ============================================================

if not database_exists():

    st.error(
        "❌ Database not found."
    )

    st.info(
        "Please run `python analyze_dataset.py` first."
    )

    st.stop()


if not reviews_table_exists():

    st.error(
        "❌ Reviews table not found."
    )

    st.info(
        "Please run `python analyze_dataset.py` first."
    )

    st.stop()


# Create indexes
create_indexes()


# ============================================================
# PAGE 1 — ANALYTICS DASHBOARD
# ============================================================

if page == "📊 Analytics Dashboard":

    st.title(
        "💄 Smart Cosmetic Product Management & Customer Opinion Analytics"
    )

    st.markdown(
        """
        ### Customer Opinion Analytics Dashboard

        This dashboard integrates **ASTMA + Enterprise Systems**
        to analyze customer reviews and support business decisions.
        """
    )

    st.divider()

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    st.subheader("🔎 Analytics Filters")

    col1, col2, col3 = st.columns(3)

    brands = get_brands()
    categories = get_primary_categories()
    secondary_categories = get_secondary_categories()

    with col1:

        selected_brand = st.selectbox(
            "Brand",
            ["All"] + brands
        )

    with col2:

        selected_primary_category = st.selectbox(
            "Primary Category",
            ["All"] + categories
        )

    with col3:

        selected_secondary_category = st.selectbox(
            "Secondary Category",
            ["All"] + secondary_categories
        )

    # --------------------------------------------------------
    # KPIs
    # --------------------------------------------------------

    stats = get_filtered_statistics(
        selected_brand,
        selected_primary_category,
        selected_secondary_category
    )

    st.divider()

    st.subheader("📈 Key Performance Indicators")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "Total Reviews",
            f"{stats['total']:,}"
        )

    with col2:

        st.metric(
            "Positive",
            f"{stats['positive']:,}"
        )

    with col3:

        st.metric(
            "Negative",
            f"{stats['negative']:,}"
        )

    with col4:

        st.metric(
            "Neutral",
            f"{stats['neutral']:,}"
        )

    with col5:

        st.metric(
            "Average Rating",
            f"{stats['average_rating']:.2f} ⭐"
        )

    # --------------------------------------------------------
    # SENTIMENT ANALYSIS
    # --------------------------------------------------------

    st.divider()

    st.subheader("😊 Customer Sentiment Analysis")

    sentiment_data = get_sentiment_distribution(
        selected_brand,
        selected_primary_category,
        selected_secondary_category
    )

    if not sentiment_data.empty:

        col1, col2 = st.columns(2)

        with col1:

            fig = px.pie(
                sentiment_data,
                names="sentiment",
                values="count",
                title="Sentiment Distribution",
                hole=0.4
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:

            fig = px.bar(
                sentiment_data,
                x="sentiment",
                y="count",
                title="Sentiment Count",
                text="count"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:

        st.warning(
            "No sentiment data available for the selected filters."
        )

    # --------------------------------------------------------
    # RATING DISTRIBUTION
    # --------------------------------------------------------

    st.divider()

    st.subheader("⭐ Rating Analysis")

    rating_data = get_rating_distribution(
        selected_brand,
        selected_primary_category,
        selected_secondary_category
    )

    if not rating_data.empty:

        fig = px.bar(
            rating_data,
            x="rating",
            y="count",
            title="Rating Distribution",
            text="count"
        )

        fig.update_xaxes(
            dtick=1
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # PRODUCT SENTIMENT
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🛍️ Product-wise Sentiment Analysis"
    )

    product_sentiment = get_product_sentiment(
        selected_brand,
        selected_primary_category,
        selected_secondary_category
    )

    if not product_sentiment.empty:

        fig = px.bar(
            product_sentiment,
            x="product_name",
            y="count",
            color="sentiment",
            title="Top Product Sentiment Results"
        )

        fig.update_layout(
            xaxis_tickangle=-45
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # ASPECT ANALYSIS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🔍 Customer Opinion / Aspect Analysis"
    )

    aspect_data = get_aspect_counts(
        selected_brand,
        selected_primary_category,
        selected_secondary_category
    )

    if not aspect_data.empty:

        fig = px.bar(
            aspect_data,
            x="Aspect",
            y="Reviews",
            title="Frequently Mentioned Product Aspects",
            text="Reviews"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            aspect_data,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # RECENT REVIEWS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📝 Recent Customer Reviews"
    )

    recent_reviews = get_recent_reviews(
        selected_brand,
        selected_primary_category,
        selected_secondary_category,
        100
    )

    if not recent_reviews.empty:

        st.dataframe(
            recent_reviews,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No reviews found."
        )

    # --------------------------------------------------------
    # BUSINESS INSIGHTS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "💡 Business Insights"
    )

    if stats["total"] > 0:

        positive_percentage = (
            stats["positive"]
            / stats["total"]
            * 100
        )

        negative_percentage = (
            stats["negative"]
            / stats["total"]
            * 100
        )

        if positive_percentage >= 60:

            st.success(
                f"✅ Customer satisfaction is strong. "
                f"{positive_percentage:.1f}% of reviews are positive."
            )

        elif negative_percentage >= 30:

            st.error(
                f"⚠️ A significant number of customers "
                f"have negative opinions ({negative_percentage:.1f}%). "
                f"Product improvement should be considered."
            )

        else:

            st.info(
                "ℹ️ Customer sentiment is mixed. "
                "Further product-level analysis is recommended."
            )

        if stats["average_rating"] >= 4:

            st.success(
                f"⭐ Average rating is {stats['average_rating']:.2f}. "
                f"The selected products are performing well."
            )

        elif stats["average_rating"] < 3:

            st.warning(
                f"⚠️ Average rating is only "
                f"{stats['average_rating']:.2f}. "
                f"Management should investigate customer complaints."
            )

    else:

        st.info(
            "No data available for business insights."
        )


# ============================================================
# PAGE 2 — PRODUCT MANAGEMENT
# ============================================================

elif page == "🛍️ Product Management":

    st.title(
        "🛍️ Product Management"
    )

    st.markdown(
        """
        Enterprise Systems module for managing cosmetic
        product information.
        """
    )

    st.divider()

    # --------------------------------------------------------
    # ADD PRODUCT
    # --------------------------------------------------------

    st.subheader(
        "➕ Add New Product"
    )

    with st.form(
        "product_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            product_name = st.text_input(
                "Product Name"
            )

            brand = st.text_input(
                "Brand"
            )

            category = st.text_input(
                "Category"
            )

        with col2:

            price = st.number_input(
                "Price (₹)",
                min_value=0.0,
                step=10.0
            )

        submitted = st.form_submit_button(
            "Add Product"
        )

        if submitted:

            if not product_name.strip():

                st.error(
                    "Please enter a product name."
                )

            elif not brand.strip():

                st.error(
                    "Please enter a brand."
                )

            else:

                add_product_to_database(
                    product_name.strip(),
                    brand.strip(),
                    category.strip(),
                    price
                )

                st.success(
                    "✅ Product added successfully!"
                )

    # --------------------------------------------------------
    # PRODUCT CATALOGUE
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📦 Product Catalogue"
    )

    search_text = st.text_input(
        "Search product or brand"
    )

    if products_table_exists():

        products = load_product_catalogue(
            search_text
        )

        if not products.empty:

            st.dataframe(
                products,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No products found."
            )

    else:

        st.warning(
            "Products table is not available."
        )


# ============================================================
# PAGE 3 — REVIEW MANAGEMENT
# ============================================================

elif page == "📝 Review Management":

    st.title(
        "📝 Review Management"
    )

    st.markdown(
        """
        Add customer reviews and automatically perform:

        **Text Preprocessing → Sentiment Analysis → Opinion Mining**
        """
    )

    st.divider()

    # --------------------------------------------------------
    # REVIEW FORM
    # --------------------------------------------------------

    st.subheader(
        "➕ Add Customer Review"
    )

    with st.form(
        "review_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            product_id = st.text_input(
                "Product ID (optional)"
            )

            product_name = st.text_input(
                "Product Name"
            )

            brand = st.text_input(
                "Brand"
            )

            primary_category = st.text_input(
                "Primary Category",
                value="Skincare"
            )

            secondary_category = st.text_input(
                "Secondary Category"
            )

        with col2:

            tertiary_category = st.text_input(
                "Tertiary Category"
            )

            rating = st.slider(
                "Rating",
                min_value=1,
                max_value=5,
                value=5
            )

            review = st.text_area(
                "Customer Review",
                height=150
            )

        submitted = st.form_submit_button(
            "Analyze & Save Review"
        )

        if submitted:

            if not product_name.strip():

                st.error(
                    "Please enter the product name."
                )

            elif not brand.strip():

                st.error(
                    "Please enter the brand."
                )

            elif not review.strip():

                st.error(
                    "Please enter a customer review."
                )

            else:

                # -----------------------------
                # SENTIMENT
                # -----------------------------

                sentiment, score = analyze_sentiment(
                    review
                )

                # -----------------------------
                # OPINION MINING
                # -----------------------------

                detected_aspects = analyze_opinions(
                    review
                )

                aspect_text = ", ".join(
                    detected_aspects
                )

                # -----------------------------
                # SAVE
                # -----------------------------

                saved_id = save_manual_review(
                    product_id.strip() or None,
                    product_name.strip(),
                    brand.strip(),
                    primary_category.strip(),
                    secondary_category.strip(),
                    tertiary_category.strip(),
                    rating,
                    review.strip(),
                    sentiment,
                    score,
                    aspect_text
                )

                st.success(
                    f"✅ Review saved successfully! "
                    f"Review ID: {saved_id}"
                )

                # -----------------------------
                # RESULT
                # -----------------------------

                st.subheader(
                    "📊 Analysis Result"
                )

                result_col1, result_col2, result_col3 = st.columns(3)

                with result_col1:

                    st.metric(
                        "Sentiment",
                        sentiment
                    )

                with result_col2:

                    st.metric(
                        "Sentiment Score",
                        f"{score:.3f}"
                    )

                with result_col3:

                    st.metric(
                        "Detected Aspects",
                        len(detected_aspects)
                    )

                if detected_aspects:

                    st.info(
                        "Detected aspects: "
                        + ", ".join(
                            detected_aspects
                        )
                    )

                else:

                    st.info(
                        "No predefined product aspects detected."
                    )

                # Clear cached dashboard results
                st.cache_data.clear()

    # --------------------------------------------------------
    # STORED REVIEWS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📋 Stored Reviews"
    )

    stored_reviews = get_recent_reviews(
        "All",
        "All",
        "All",
        100
    )

    if not stored_reviews.empty:

        st.dataframe(
            stored_reviews,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No reviews available."
        )


# ============================================================
# PAGE 4 — ITPM PROJECT MANAGEMENT
# ============================================================

elif page == "📅 ITPM Project Management":

    st.title(
        "📅 ITPM Project Management"
    )

    st.markdown(
        """
        This section represents the **IT Project Management**
        component of the project.
        """
    )

    st.divider()

    # --------------------------------------------------------
    # PROJECT OVERVIEW
    # --------------------------------------------------------

    st.subheader(
        "📌 Project Overview"
    )

    summary = get_project_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Project Duration",
            summary["Duration"]
        )

    with col2:

        st.metric(
            "Project Manager",
            summary["Project Manager"]
        )

    with col3:

        st.metric(
            "Subjects",
            summary["Main Subjects"]
        )

    with col4:

        st.metric(
            "Technology",
            "Python + SQLite"
        )

    st.write(
        "**Project:**",
        summary["Project Name"]
    )

    # --------------------------------------------------------
    # WBS
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📋 Work Breakdown Structure (WBS)"
    )

    wbs = get_wbs()

    st.dataframe(
        wbs,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # PROJECT SCHEDULE
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "📅 Project Schedule"
    )

    schedule = get_schedule()

    st.dataframe(
        schedule,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # SCHEDULE VISUALIZATION
    # --------------------------------------------------------

    st.subheader(
        "📊 Schedule Visualization"
    )

    schedule_chart = px.bar(
        schedule,
        x="Duration (Weeks)",
        y="Task",
        orientation="h",
        text="Duration (Weeks)",
        title="Project Task Duration"
    )

    st.plotly_chart(
        schedule_chart,
        use_container_width=True
    )

    # --------------------------------------------------------
    # MILESTONES
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🎯 Project Milestones"
    )

    milestones = get_milestones()

    st.dataframe(
        milestones,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # RESOURCES
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "👥 Resource Management"
    )

    resources = get_resources()

    st.dataframe(
        resources,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # COST ESTIMATION
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "💰 Cost Estimation"
    )

    costs = get_cost_estimation()

    st.dataframe(
        costs,
        use_container_width=True,
        hide_index=True
    )

    total_cost = costs[
        "Estimated Cost (₹)"
    ].sum()

    st.metric(
        "Total Estimated Project Cost",
        f"₹{total_cost:,.0f}"
    )

    # --------------------------------------------------------
    # RISK MANAGEMENT
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "⚠️ Risk Register"
    )

    risks = get_risks()

    st.dataframe(
        risks,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # ITPM ACTIVITIES
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🛠️ ITPM Activities"

    )

    activities = pd.DataFrame({

        "Activity": [
            "Requirement Analysis",
            "Project Planning",
            "Work Breakdown Structure",
            "Project Scheduling",
            "Resource Allocation",
            "Cost Estimation",
            "Risk Management",
            "Testing",
            "Monitoring",
            "Final Deployment"
        ],

        "Purpose": [
            "Identify system requirements",
            "Plan project activities",
            "Break project into manageable tasks",
            "Define task timelines",
            "Assign project resources",
            "Estimate project expenses",
            "Identify and control risks",
            "Verify system functionality",
            "Track project progress",
            "Deliver final system"
        ]
    })

    st.dataframe(
        activities,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.sidebar.divider()

st.sidebar.caption(
    "Smart Cosmetic Product Management & Customer Opinion Analytics System"
)

st.sidebar.caption(
    "ES + ITPM + ASTMA"
)