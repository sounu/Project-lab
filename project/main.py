import streamlit as st
import pandas as pd
import requests
import time
import os

# Set API URL
API_URL = "http://flask-api:8000"

# Load static files
def load_static_files():
    css_file = open("static/css/style.css").read()
    js_file = open("static/js/main.js").read()
    components = open("templates/components.html").read()
    return css_file, js_file, components

# Initialize page
def init_page():
    st.set_page_config(
        page_title="Movie Recommender",
        page_icon="🎬",
        layout="wide"
    )
    
    # Load static files
    css, js, components = load_static_files()
    
    # Inject CSS
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    # Inject JavaScript
    st.components.v1.html(f"<script>{js}</script>", height=0)
    
    # Display title using component template
    st.markdown(components.split("<!-- Page Title -->")[1].split("<!-- Footer -->")[0], 
               unsafe_allow_html=True)

# Initialize the page
init_page()

# Wait for API to be ready
def wait_for_api():
    max_retries = 30
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.get(f"{API_URL}/health")
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        retry_count += 1
        time.sleep(1)
        if retry_count == 1:  # Show message only on first attempt
            st.info("Waiting for API service to be ready...")
    return False

if not wait_for_api():
    st.error("Could not connect to the API service. Please try refreshing the page.")
    st.stop()

# Search box
search_query = st.text_input("Search for a movie:", "")

if search_query:
    with st.spinner('🔍 Searching for movies...'):
        response = requests.get(f"{API_URL}/search", params={'query': search_query})
        
    try:
        response.raise_for_status()
        movies = response.json()['results']
        
        if movies:
            st.markdown("### 🎯 Search Results")
            cols = st.columns(3)
            
            for idx, movie in enumerate(movies):
                with cols[idx % 3]:
                    # Use the movie card template from components.html
                    card_template = open("templates/components.html").read().split("<!-- Movie Card Template -->")[1].split("<!-- Page Title -->")[0]
                    card_html = card_template.format(
                        title=movie['title'],
                        genres=movie['genres']
                    )
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    if st.button("Get Recommendations 👉", key=f"btn_{idx}", type="primary"):
                        # Get recommendations from Flask API
                        rec_response = requests.get(f"{API_URL}/recommendations/{movie['movieId']}")
                        recommendations = rec_response.json()['recommendations']
                        
                        st.subheader(f"Movies similar to {movie['title']}")
                        rec_cols = st.columns(3)
                        
                        for rec_idx, rec in enumerate(recommendations):
                            with rec_cols[rec_idx % 3]:
                                st.write(f"**{rec['title']}**")
                                st.write(f"Genres: {rec['genres']}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching results: {str(e)}")

# Add footer from components
st.markdown(open("templates/components.html").read().split("<!-- Footer -->")[1], 
           unsafe_allow_html=True)
        
