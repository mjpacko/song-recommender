import os
import sys

print("Current Working Directory:", os.getcwd())
print("Python Path:", sys.path)


import streamlit as st
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

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

        # Add genres to the DataFrame as separate columns with value 1
        for genre in genres:
            df[genre] = 1  # Create a new column for each genre with value 1

        # Load the clustered dataset to get the desired column order
        clustered_df = pd.read_csv('../data/7_clustered_dataset.csv')
        desired_columns = clustered_df.columns.tolist()

        # Reorder the DataFrame to match the clustered dataset columns
        df = df.reindex(columns=desired_columns)

        # Drop any columns that are not present in the clustered dataset
        df = df.loc[:, df.columns.intersection(desired_columns)]

        # Return the DataFrame
        return df

    except Exception as e:
        st.error(f"An error occurred while fetching track details: {str(e)}")
        return None

    except Exception as e:
        st.error(f"An error occurred while fetching track details: {str(e)}")
        return None


# Streamlit UI
st.title("🎵 Spotify Song Recommender 🎵")

# Search inputs
search_query = st.text_input("Enter song name:", "")
artist_name = st.text_input("Enter artist name (optional):", "")

# DataFrame to store track details
if 'track_data' not in st.session_state:
    st.session_state.track_data = pd.DataFrame(columns=['title', 'artist', 'album', 'is_explicit', 'album_cover', 'release_year'])

if search_query:
    search_query = search_query.lower()
    artist_name = artist_name.lower() if artist_name else None
    with st.spinner('Searching...'):
        results = search_song(search_query, artist_name)
    
    if results:
        st.write("### Search Results:")
        
        if 'selected_track' not in st.session_state:
            st.session_state.selected_track = None
        
        for idx, track in enumerate(results):
            cols = st.columns([1, 2, 1])  # Proportions for artwork : info : button
            
            with cols[0]:
                st.image(track['album_cover'], width=80)
            
            with cols[1]:
                st.markdown(f"**{track['title']}**")
                st.markdown(f"*{track['artist']}*")
                st.markdown(f"Released: {track['year']}")
                if track['preview_url']:
                    st.audio(track['preview_url'], format="audio/mp3", start_time=0)
            
            with cols[2]:
                if st.button("Select", key=f"select_{idx}"):
                    st.session_state.selected_track = track
                    # Fetch track details and store in DataFrame
                    track_details_df = get_track_details(track['id'])  # This now returns a DataFrame
                    if track_details_df is not None:
                        # Use pd.concat to add the new row to the existing DataFrame
                        if 'track_data' not in st.session_state:
                            st.session_state.track_data = pd.DataFrame()  # Initialize if it doesn't exist
                        
                        st.session_state.track_data = pd.concat([st.session_state.track_data, track_details_df], ignore_index=True)

            st.markdown("---")
        
        if st.session_state.selected_track:
            st.write("### Selected Track Details:")
            st.dataframe(st.session_state.track_data)
    else:
        st.warning("No songs found. Try another search!")
