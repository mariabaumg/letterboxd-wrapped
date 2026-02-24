# streamlit_app/utils.py
import pandas as pd
import zipfile
import os
import streamlit as st

def read_letterboxd_zip(uploaded_file):
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv') and 'watched' in f.lower()]
        if not csv_files:
            st.error("no watched.csv found in the zip!")
            return pd.DataFrame()
        csv_name = csv_files[0]
        zip_ref.extract(csv_name, os.getcwd())
        df = pd.read_csv(csv_name)
        os.remove(csv_name)
    return df

def letterboxd_wrapped(df, year=None):
    if df.empty:
        return {}
    if year:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df[df['Date'].dt.year == year]

    stats = {}
    stats['total_films'] = len(df)
    stats['films_list'] = df[['Date', 'Name', 'Year', 'Letterboxd URI']].sort_values(by='Date')    
    df['Month'] = df['Date'].dt.month
    stats['films_per_month'] = df['Month'].value_counts().sort_index()
    
    return stats
