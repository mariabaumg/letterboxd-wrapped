import streamlit as st
import pandas as pd
import zipfile
import os
import altair as alt

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

# UI
st.title("Letterboxd Wrapped")
st.write("Upload your Letterboxd export ZIP to see your Wrapped stats!")

uploaded_file = st.file_uploader("Choose your Letterboxd ZIP", type=["zip"])
year = st.number_input("Year to view", min_value=1900, max_value=2100, value=2024)

month_map = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun",
             7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}

if uploaded_file:
    df = read_letterboxd_zip(uploaded_file)
    if not df.empty:
        stats = letterboxd_wrapped(df, year)
        
        st.subheader(f"Total films watched in {year}: {stats['total_films']}")
        
        st.subheader("Films watched (chronological):")
        st.dataframe(stats['films_list'])
        
        films_per_month = pd.Series(stats['films_per_month'])
        all_months = pd.Series(range(1, 13))
        films_per_month = films_per_month.reindex(all_months, fill_value=0)
        month_names = [month_map[m] for m in films_per_month.index]
        
        chart_df = pd.DataFrame({
            "Month": month_names,
            "Movies watched": films_per_month.values
        })

        # bar graph        
        chart = alt.Chart(chart_df).mark_bar(color='skyblue').encode(
            x=alt.X("Month", sort=list(month_map.values())),
            y="Movies watched"
        ).properties(
            title=f"Movies watched per month in {year}"
        )
        
        st.altair_chart(chart, use_container_width=True)