
# Smart Cosmetic Product Management & Customer Opinion Analytics System

## Project Overview
A Python-based application that analyzes cosmetic product reviews to identify customer sentiment and opinions about product aspects.

## Objectives
- Analyze customer reviews using sentiment analysis.
- Classify reviews as Positive, Negative, or Neutral.
- Identify aspects such as price, quality, packaging, texture, fragrance, and pigmentation.
- Display insights using an interactive Streamlit dashboard.
- Manage product and review information using SQLite.
- Demonstrate Enterprise Systems (ES), IT Project Management (ITPM), and Advanced Social, Text and Media Analytics (ASTMA).

## Technology Stack
- Python
- Streamlit
- Pandas
- SQLite
- VADER Sentiment Analysis
- Plotly
- Natural Language Processing (NLP)

## Dataset
Uses the Sephora Products and Skincare Reviews dataset:
https://www.kaggle.com/datasets/nadyinky/sephora-products-and-skincare-reviews

Download the dataset and place the source CSV files in the `dataset/` folder before running the preparation scripts.

## Run Locally
1. Install the dependencies:
   `pip install -r requirements.txt`
2. Prepare the dataset:
   `python prepare_dataset.py`
3. Analyze the reviews:
   `python analyze_dataset.py`
4. Launch the application:
   `streamlit run app.py`

## Main Features
- Sentiment analytics dashboard
- Product management
- Review management
- Aspect-based opinion mining
- Project management information, including schedules, milestones, costs, and risks

## Academic Integration
Enterprise Systems (ES), IT Project Management (ITPM), and Advanced Social, Text and Media Analytics (ASTMA).
