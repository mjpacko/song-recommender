
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.preprocessing import StandardScaler
from joblib import load
import random
from dotenv import load_dotenv
import os
import sys
sys.path.append('.')

def search_song(search_query, artist_name=None):
    try:
        # Build the search query
        if artist_name:
            search_query += f" artist:{artist_name}"
        
        # Initialize Spotify client
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=st.secrets['SPOTIPY_CLIENT_ID'], client_secret=st.secrets['SPOTIPY_CLIENT_SECRET']))

        # Search for the track on Spotify
        results = sp.search(q=search_query, type='track', limit=5)
        
        if not results['tracks']['items']:
            return None
        
        # Extract relevant information for each track
        tracks = []
        for track in results['tracks']['items']:
            release_year = track['album']['release_date'][:4]
            track_info = {
                'title': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'year': release_year,
                'album_cover': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'id': track['id'],
                'preview_url': track['preview_url']
            }
            tracks.append(track_info)
        
        return tracks
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

def get_track_details(track_id):

    # Initialize Spotify client
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=st.secrets['SPOTIPY_CLIENT_ID'], client_secret=st.secrets['SPOTIPY_CLIENT_SECRET']))

    try:
        track = sp.track(track_id)
        artist_id = track['artists'][0]['id']
        artist = sp.artist(artist_id)

        # Extract genres from the artist's profile
        genres = artist.get('genres', [])

        # Create a DataFrame to hold track details
        track_details = {
            'title': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'is_explicit': track['explicit'],
            'album_cover': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'release_year': track['album']['release_date'][:4],
        }

        # Create a DataFrame from the track details
        df = pd.DataFrame([track_details])  # Create a DataFrame with a single row

        # Load the clustered dataset to get the desired column order
        clustered_df = pd.read_csv('data/7_clustered_dataset.csv') 
        desired_columns = clustered_df.columns.tolist()

        # Initialize the DataFrame with the first 7 columns
        df = df.reindex(columns=desired_columns)  # Ensure the DataFrame has the same columns

        # Initialize genre columns with 0/1 encoding after the 7th column
        for genre in desired_columns[6:]:  # Start from the 8th column
            if genre in genres:
                df[genre] = 1  # Set to 1 if the genre is present
            else:
                df[genre] = 0  # Set to 0 if the genre is not present

        # Return the DataFrame
        return df

    except Exception as e:
        st.error(f"An error occurred while fetching track details: {str(e)}")
        return None
    
def create_training_dataset(original_df):
    # Define the columns to remove
    columns_to_remove = ['title', 'artist', 'album', 'is_explicit', 'album_cover', 'cluster', 'isHot']
    
    # Create a new DataFrame by dropping the specified columns
    training_df = original_df.drop(columns=columns_to_remove, errors='ignore')  # Use errors='ignore' to avoid errors if columns are missing

    # Initialize and fit the scaler
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(training_df)
    df_scaled = pd.DataFrame(scaled_data, columns=training_df.columns)
    
    return df_scaled

def apply_kmeans_model(df_scaled):
    # Load the pre-trained KMeans model
    kmeans_model = load('models/kmeans_model.joblib')
    
    # Predict the clusters for the scaled data
    cluster_labels = kmeans_model.predict(df_scaled)
    
    return cluster_labels