# Letterboxd Wrapped – Monthly Movie Recommender

This is a Flask app that shows your watched movies and gives movie recommendations each month based on your viewing habits.

## Live Demo

Check out the live app here: [https://letterboxd-wrapped-1.onrender.com/](https://letterboxd-wrapped-1.onrender.com/)

## Project Overview & Goals

This project was made to emulate spotify wrapped for letterboxd. Check out '/streamlit_app' for early data exploration/project beginnings.

This project uses my own letterboxd data to generate monthly movie suggestions based on viewing behavior via **machine learning techniques**. A key **goal for future development** is to allow users to **upload their own CSVs**, making the app fully personalized for any user’s movie history.  

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