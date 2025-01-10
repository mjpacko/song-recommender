import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials 
import pandas as pd

def search_song(search_query, artist_name=None):
    try:
        # Build the search query
        if artist_name:
            search_query += f" artist:{artist_name}"
        
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
    try:
        track = sp.track(track_id)
        artist_id = track['artists'][0]['id']
        artist = sp.artist(artist_id)
        
        # Extract genres from the artist's profile
        genres = artist.get('genres', [])
        
        # Extract track details
        track_details = {
            'title': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'is_explicit': track['explicit'],
            'album_cover': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'release_year': track['album']['release_date'][:4],
            'genres': ', '.join(genres)
        }
        return track_details
    except Exception as e:
        st.error(f"An error occurred while fetching track details: {str(e)}")
        return None

def genre_encoding(df):
    # 1. Get all unique genres (no threshold filtering)
    genres = []
    for genre_list in df['Genres'].dropna():
        genre_list = genre_list.split(', ')
    genres = [genre.strip() for genre in genres]
    all_genres.extend(genres)

    unique_genres = sorted(list(set(all_genres)))  # Get all unique genres and sort them

    # 2. Create one-hot encoding for all genres
def encode_all_genres(genre_string):
    if pd.isna(genre_string):
        return [0] * len(unique_genres)
    
    genre_list = genre_string.split(', ')
    return [1 if genre in genre_list else 0 for genre in unique_genres]

    # Create encoded columns
    genre_encoded = pd.DataFrame(
        df['genres'].apply(encode_all_genres).tolist(),
        columns=unique_genres
)
    
    