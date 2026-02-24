# ml_recommender/recommender.py
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
import zipfile
import os

# --- Step 1: load watched movies ---
def load_watched_movies(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv') and 'watched' in f.lower()]
        if not csv_files:
            raise FileNotFoundError("No watched CSV found in the zip!")
        csv_name = csv_files[0]
        zip_ref.extract(csv_name, os.getcwd())
    
    df_watched = pd.read_csv(csv_name)
    df_watched['Date'] = pd.to_datetime(df_watched['Date'], errors='coerce')
    df_watched['Year'] = pd.to_numeric(df_watched['Year'], errors='coerce')
    df_watched['Month'] = df_watched['Date'].dt.month
    df_watched = df_watched.dropna(subset=['Name','Year'])
    df_watched['Key'] = list(zip(df_watched['Name'], df_watched['Year']))
    
    return df_watched

# --- Step 2: load IMDB ratings ---
def load_ratings(ratings_path):
    df_ratings = pd.read_csv(
        ratings_path,
        sep='\t',
        usecols=['tconst', 'averageRating', 'numVotes'],
        dtype={'tconst':str}
    )
    df_ratings['averageRating'] = pd.to_numeric(df_ratings['averageRating'], errors='coerce')
    df_ratings['numVotes'] = pd.to_numeric(df_ratings['numVotes'], errors='coerce')
    df_ratings = df_ratings[(df_ratings['averageRating']>=7) & (df_ratings['numVotes']>=1000)]
    df_ratings = df_ratings.rename(columns={'averageRating':'rating', 'numVotes':'votes'})
    return df_ratings

# --- Step 3: load IMDB movie info ---
def load_movies(basics_path, df_ratings):
    chunks = []
    for chunk in pd.read_csv(
        basics_path,
        sep='\t',
        usecols=['tconst','titleType','primaryTitle','startYear','genres'],
        dtype='str',
        chunksize=100_000
    ):
        chunk = chunk[chunk['titleType'].isin(['movie','tvseries'])]
        chunk = chunk[["tconst","titleType","primaryTitle","startYear","genres"]]
        chunks.append(chunk)
    df_movies = pd.concat(chunks, ignore_index=True)
    
    df_movies = df_movies.rename(columns={"primaryTitle":"Name","startYear":"Year"})
    df_movies['genres'] = df_movies['genres'].apply(lambda x: x.split(",") if pd.notna(x) else [])
    df_movies['Year'] = pd.to_numeric(df_movies['Year'], errors='coerce')
    
    # merge ratings
    df_movies_filtered = df_movies.merge(
        df_ratings[['tconst','rating','votes']],
        on='tconst',
        how='inner'
    )
    
    return df_movies_filtered

# --- Step 4: build monthly genre profiles ---
def build_monthly_genre_profiles(df_watched):
    """
    df_watched: dataframe with 'Date' and 'genres'
    returns: dict MonthIndex -> Counter of genres
    """
    df_monthly = df_watched[df_watched['Date'].dt.year >= 2025].copy()
    df_monthly['MonthIndex'] = (df_monthly['Date'].dt.year - 2025) * 12 + df_monthly['Date'].dt.month
    df_monthly = df_monthly[['MonthIndex','genres']].copy()
    
    month_profiles = defaultdict(Counter)
    for _, row in df_monthly.iterrows():
        month = row['MonthIndex']
        genres_list = row['genres'] if isinstance(row['genres'], list) else []
        for g in genres_list:
            month_profiles[month][g] += 1
    return month_profiles

# --- Step 5: recommend movies ---
def recommend_movies_for_month(month_index, month_profiles, df_movies, watched_keys=set(), top_n=200, select_n=8):
    """
    Returns a list of recommended movies for the given MonthIndex, excluding watched movies.
    """
    month_counter = month_profiles.get(month_index)
    if not month_counter:
        return []
    
    genre_space = list(month_counter.keys())
    month_vector = np.array([month_counter[g] for g in genre_space], dtype=float)
    month_vector /= month_vector.sum()
    
    # Exclude watched
    df_candidates = df_movies[~df_movies['Key'].isin(watched_keys)].copy()
    
    movie_scores = []
    for idx, row in df_candidates.iterrows():
        movie_vector = np.array([1 if g in row['genres'] else 0 for g in genre_space], dtype=float)
        if movie_vector.sum() == 0:
            continue
        movie_vector /= movie_vector.sum()
        movie_scores.append((np.dot(month_vector, movie_vector), idx))
    
    movie_scores.sort(reverse=True, key=lambda x: x[0])
    top_movies_idx = [idx for _, idx in movie_scores[:top_n]]
    if not top_movies_idx:
        return []
    
    selected_idx = random.sample(top_movies_idx, min(select_n, len(top_movies_idx)))
    
    return df_candidates.loc[selected_idx]


def monthly_movies(month_index, df_watched_with_genres):
    """
    month_index: month index
    returns: list of movies watched
    """
    if month_index is None:
        filtered_df = df_watched_with_genres.copy()
    else:
        filtered_df = df_watched_with_genres[df_watched_with_genres['MonthIndex'] == month_index]

    return filtered_df[['Key']]['Key'].tolist()




if __name__ == "__main__":
    print("=== TESTING RECOMMENDER MODULE ===")

    # Load watched movies
    df_watched = pd.read_csv("ml_recommender/watched.csv")
    df_watched['Date'] = pd.to_datetime(df_watched['Date'], errors='coerce')  # <-- IMPORTANT
    df_watched['Year'] = pd.to_numeric(df_watched['Year'], errors='coerce')
    df_watched['Key'] = list(zip(df_watched['Name'], df_watched['Year']))

    # Load ratings and movies
    df_ratings = load_ratings("ml_recommender/title.ratings.tsv")
    df_movies = load_movies("ml_recommender/title.basics.tsv", df_ratings)

    # Add Key to df_movies
    df_movies['Key'] = list(zip(df_movies['Name'], df_movies['Year']))

    # Merge genres into watched
    df_watched = df_watched.merge(
        df_movies[['Key', 'genres']],
        on='Key',
        how='left'
    )

    # Exclude watched movies from candidates
    watched_keys = set(df_watched['Key'])
    df_movies = df_movies[~df_movies['Key'].isin(watched_keys)].copy()

    # Build monthly genre profiles
    month_profiles = build_monthly_genre_profiles(df_watched)

    # Test recommendations for MonthIndex = 1
    recs_df = recommend_movies_for_month(1, month_profiles, df_movies, watched_keys)
    print("Sample Recommendations for Month 1:")
    print(recs_df[['Name','genres','rating']].head())