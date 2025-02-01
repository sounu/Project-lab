from flask import Flask, jsonify, request
import pickle
import pandas as pd
import os
import time

app = Flask(__name__)

# Global variables to store loaded data
df = None
knn = None
genre_matrix = None

def load_data():
    """Load data and models, return True if successful"""
    global df, knn, genre_matrix
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            with open('movie_data.pkl', 'rb') as f:
                data = pickle.load(f)
            
            df = data['df']
            knn = data['knn']
            genre_matrix = data['genre_matrix']
            print("Data loaded successfully")
            return True
        except Exception as e:
            print(f"Error loading data (attempt {retry_count + 1}/{max_retries}): {str(e)}")
            retry_count += 1
            time.sleep(5)  # Wait 5 seconds before retrying
    return False

# Move data loading to a proper initialization
if not load_data():
    print("Failed to load required data and models")
    # Let the container fail fast if data loading fails
    os._exit(1)

@app.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify({'results': []})
    
    # Search movies by title
    matches = df[df['title'].str.lower().str.contains(query)]
    results = matches.head(6).to_dict('records')
    return jsonify({'results': results})

@app.route('/recommendations/<int:movie_id>', methods=['GET'])
def get_recommendations(movie_id):
    try:
        # Find the movie index
        movie_idx = df[df['movieId'] == movie_id].index[0]
        
        # Get KNN recommendations
        distances, indices = knn.kneighbors(genre_matrix[movie_idx])
        
        # Get recommended movies (excluding the input movie)
        recommendations = df.iloc[indices[0][1:]].to_dict('records')
        return jsonify({'recommendations': recommendations})
    except IndexError:
        return jsonify({'error': 'Movie ID not found'}), 404
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Enhanced health check that verifies data is loaded"""
    if df is None or knn is None or genre_matrix is None:
        return jsonify({
            'status': 'unhealthy',
            'message': 'Data not properly loaded'
        }), 500
    return jsonify({
        'status': 'healthy',
        'data_loaded': True,
        'movie_count': len(df) if df is not None else 0
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000) 