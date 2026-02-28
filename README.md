# Letterboxd Wrapped – Monthly Movie Recommender

This project is a monthly movie recommender built from personal Letterboxd data. It exists in two versions:
1. **Flask App** – dynamic app with machine learning recommendations, deployed on Render.  
2. **Static Version** – static site with machine learning recommendations preprocessed and stored in JSON file, deployed on **GitHub Pages**.

## Live Demo

- **Static GitHub Pages Site: (Recommended)** [https://mariabaumg.github.io/letterboxd-wrapped/](https://mariabaumg.github.io/letterboxd-wrapped/letterboxd-wrapped/)  
- **Dynamic Flask App:** [https://letterboxd-wrapped-1.onrender.com/](https://letterboxd-wrapped-1.onrender.com/)  


## Project Overview & Goals

This project was made to emulate Spotify Wrapped for Letterboxd. Check out '/streamlit_app' for early data exploration/project beginnings.

This project uses my own letterboxd data to generate monthly movie suggestions based on viewing behavior via **machine learning techniques**. A key **goal for future development** is to allow users to **upload their own CSVs**, making the app fully personalized for any user’s movie history.  

The **static GitHub Pages site** provides a lightweight alternative to the Flask app, offering JSON-based recommendations and movie browsing without requiring server-side computation. It’s ideal for fast access, easy sharing, or offline-like browsing.

## Features & Highlights

- **Machine Learning Recommendations:** Personalized monthly movie suggestions generated using **cosine similarity** and genre profiles.  
- **Data Wrangling & Processing:** Cleaned and merged multiple datasets including watched movies and IMDb metadata to create a structured, high-quality dataset for analysis.  
- **Dynamic Movie Posters:** Movie posters are pulled in real-time using the **TMDb API** for a visually rich experience. *(Note: generating recommendations may be slightly slow due to fetching posters.)*
- **Front-End Development:** Interactive web interface built with HTML, CSS, and JavaScript.
- **User-Centric Design:** Select a month to see curated recommendations or browse monthly watch history. 
- **Scalable & Production-Ready:** Deployed on **Render** with Python, Flask, and Gunicorn, ready for web access anywhere.  
- This project was **AI-assisted**, particularly for front-end development.

## Setup (for local development)

1. Clone the repository:

```bash
git clone https://github.com/mariabaumg/letterboxd-wrapped.git
cd letterboxd-wrapped