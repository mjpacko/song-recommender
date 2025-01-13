import streamlit as st
import pandas as pd
#import sys
#sys.path.append('.')
from utils.functions import search_song, get_track_details, create_training_dataset, apply_kmeans_model

# Set the page configuration to wide mode
st.set_page_config(
    page_title="Discoverfy",
    page_icon="🎵",
    layout="wide")


### MAIN FUNCTION ###

def main():
    # Create two columns for layout
    col1, col2 = st.columns([1, 1])  # Adjust the proportions as needed

    with col1:
        show_search()

    with col2:
        show_recommendations()

def show_search():
    st.title("🎵 Welcome to Discoverfy🎵")

    search_query = st.text_input("Enter song name:", "", key="search_query", 
                                  help="Search for a song", 
                                  placeholder="Song name")

    artist_name = st.text_input("Enter artist name (optional):", "", key="artist_name", 
                                 help="Artist name (optional)", 
                                 placeholder="Artist name")

    no_explicit = st.checkbox("No Explicit")  # Checkbox for filtering explicit songs

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
                            # Create a new DataFrame row from the track details
                            if 'track_data' not in st.session_state:
                                st.session_state.track_data = pd.DataFrame()  # Initialize if it doesn't exist
                            
                            st.session_state.track_data = pd.concat([st.session_state.track_data, track_details_df], ignore_index=True)

                            # Create the training dataset
                            training_data = create_training_dataset(st.session_state.track_data)

                            # Apply the KMeans model to get cluster labels
                            cluster_labels = apply_kmeans_model(training_data)

                            # Get the last cluster label assigned to the selected track
                            assigned_cluster = cluster_labels[-1]  # Assuming the last label corresponds to the selected track

                            # Store the assigned cluster in session state
                            st.session_state.assigned_cluster = assigned_cluster

                            # Show recommendations
                            st.session_state.show_recommendations = True  # Set flag to show recommendations

            st.markdown("---")
        
        else:
            st.warning("No songs found. Try another search!")

def show_recommendations():

    if 'assigned_cluster' in st.session_state and st.session_state.show_recommendations:
        # Load the clustered dataset
        clustered_df = pd.read_csv('data/7_clustered_dataset.csv')

        # Filter songs from the same cluster
        same_cluster_songs = clustered_df[clustered_df['cluster'] == st.session_state.assigned_cluster]

        # Check if the "No Explicit" checkbox is checked
        if st.session_state.get('no_explicit', False):
            same_cluster_songs = same_cluster_songs[same_cluster_songs['is_explicit'] == False]

        # Randomly select 5 songs from the same cluster
        if len(same_cluster_songs) > 5:
            recommended_songs = same_cluster_songs.sample(n=5)
        else:
            recommended_songs = same_cluster_songs  # If less than 5, take all

        # Display the recommended songs
        st.write("### Recommended Playlist:")
        for _, song in recommended_songs.iterrows():
            st.markdown(f"**{song['title']}** by *{song['artist']}*")
            st.image(song['album_cover'], width=80)  # Assuming you have an album cover column

if __name__ == "__main__":
    main()