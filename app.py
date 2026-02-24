from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np


from dotenv import load_dotenv
load_dotenv()


from tmdbv3api import TMDb, Movie
tmdb = TMDb()

import os

tmdb.api_key = os.environ.get("TMDB_API_KEY")
tmdb_movie = Movie()

# Import recommender functions
from ml_recommender.recommender import (
    load_ratings, load_movies, build_monthly_genre_profiles, recommend_movies_for_month, monthly_movies
)

app = Flask(__name__, template_folder="web_demo", static_folder="web_demo")

# ----------------------------
# Load data
# ----------------------------
def load_watched(csv_path):
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['Month'] = df['Date'].dt.month
    df = df.dropna(subset=['Name','Year'])
    df['Key'] = list(zip(df['Name'], df['Year']))
    # MonthIndex: Jan 2025 = 1, Feb 2025 = 2, ..., Feb 2026 = 14
    df['MonthIndex'] = (df['Date'].dt.year - 2025) * 12 + df['Date'].dt.month
    # Dummy poster initially
    df['poster'] = df['Name'].apply(lambda x: f"https://dummyimage.com/200x300/000/fff&text={x.replace(' ', '+')}")
    return df

df_watched = load_watched("ml_recommender/watched.csv")
# df_ratings = load_ratings("ml_recommender/title.ratings.tsv")
# df_movies = load_movies("ml_recommender/title.basics.tsv", df_ratings)
df_movies = pd.read_csv("ml_recommender/processed_movies.csv")
df_movies['Key'] = list(zip(df_movies['Name'], df_movies['Year']))
df_movies['genres'] = df_movies['genres'].apply(eval)  # convert string back to list


df_movies['Key'] = list(zip(df_movies['Name'], df_movies['Year']))

# Merge genres into watched movies
df_watched = df_watched.merge(df_movies[['Key','genres']], on='Key', how='left')

# Exclude watched from candidate movies
watched_keys = set(df_watched['Key'])
df_movies = df_movies[~df_movies['Key'].isin(watched_keys)].copy()

# Add poster column for candidate movies (dummy for now)
df_movies['poster'] = df_movies['Name'].apply(lambda x: f"https://dummyimage.com/200x300/000/fff&text={x.replace(' ', '+')}")

# Build monthly genre profiles
month_profiles = build_monthly_genre_profiles(df_watched)


# ----------------------------
# TMDb Poster function
# ----------------------------
def get_poster_url(movie_name, year=None):
    try:
        results = tmdb_movie.search(movie_name)
        if year:
            results = [m for m in results if hasattr(m, "release_date") and m.release_date and m.release_date.startswith(str(year))]
            if not results:
                results = tmdb_movie.search(movie_name)
        poster_path = results[0].poster_path if results else None
        if poster_path:
            return f"https://image.tmdb.org/t/p/w200{poster_path}"
    except Exception as e:
        print(f"TMDb error for {movie_name}: {e}")
    return f"https://dummyimage.com/200x300/000/fff&text={movie_name.replace(' ', '+')}"


# ----------------------------
# Helper: Filter watched movies
# ----------------------------
def get_watched_movies(month_index=None):
    df = df_watched.copy()
    if month_index:
        df = df[df['MonthIndex'] == month_index]

    # TMDb posters (only if not already there)
    if 'poster' not in df.columns or df['poster'].isnull().all():
        df['poster'] = df.apply(lambda row: get_poster_url(row['Name'], row['Year']), axis=1)

    if 'rating' not in df.columns:
        df['rating'] = None

    return df[['Name','poster','genres','rating']].to_dict(orient='records')


# ----------------------------
# Routes
# ----------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    month_index = data.get("month_index")

    recs_df = recommend_movies_for_month(month_index, month_profiles, df_movies, watched_keys)

    # Add TMDb poster for each movie if not already set
    recs_df = recs_df.copy()
    recs_df['poster'] = recs_df.apply(
        lambda row: get_poster_url(row['Name'], row['Year']),
        axis=1
    )

    recs = recs_df[['Name','poster','genres','rating']].to_dict(orient="records")
    return jsonify(recs)


# Route to get watched movies for a specific month
@app.route("/watched", methods=["POST"])
def watched():
    data = request.get_json()
    month_index = data.get("month_index")  # 1-14

    # Handle "all months" if month_index is None
    if not month_index:
        month_index = None

    # Get list of Keys for this month
    watched_keys_for_month = monthly_movies(month_index, df_watched)  # returns list of (Name, Year)

    # Return JSON: only display name
    movies_list = [
        {"display": f"{name} ({year})"}
        for name, year in watched_keys_for_month
    ]

    return jsonify(movies_list)


if __name__ == "__main__":
    print(f"Loaded {len(df_watched)} watched movies")
    print(f"Loaded {len(df_movies)} candidate movies")
    app.run(debug=True)