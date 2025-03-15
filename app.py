import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = st.secrets['mongo']['uri']
client = MongoClient(uri, server_api=ServerApi('1'))

db = client['Chinook']


st.title("Chinook Database Query Selector")

# Definisci le query come funzioni
def count_tracks():
    return db.Track.count_documents({}), ["Number of Tracks"]

def count_albums():
    return len(db.Track.distinct("Album.AlbumId")), ["Number of Albums"]

def count_genres():
    return len(db.Track.distinct("Genre.GenreId")), ["Number of Genres"]

def count_artists():
    return len(db.Track.distinct("Artist.ArtistId")), ["Number of Artists"]

def count_playlists():
    return len(db.Track.distinct("Playlist.PlaylistId")), ["Number of Playlists"]

def count_songs_per_album():
    return list(db.Track.aggregate([
        {"$group": {"_id": "$Album.Title", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "Album": "$_id", "Number of tracks": "$count"}},
        {"$sort": {"Number of": -1}}
    ])), None

def count_songs_per_genre():
    return list(db.Track.aggregate([
        {"$group": {"_id": "$Genre.Name", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "Genre": "$_id", "Number of tracks": "$count"}},
        {"$sort": {"Number of tracks": -1}}
    ])), None

def count_songs_per_artist():
    return list(db.Track.aggregate([
        {"$group": {"_id": "$Artist.Name", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "Artist": "$_id", "Count": "$count"}},
        {"$sort": {"Count": -1}}
    ])), None

# Map the queries to functions
queries = {
    "Count the number of tracks": count_tracks,
    "Count the number of albums": count_albums,
    "Count the number of genres": count_genres,
    "Count the number of artists": count_artists,
    "Count the number of playlists": count_playlists,
    "Count the number of songs per album": count_songs_per_album,
    "Count the number of songs per genre": count_songs_per_genre,
    "Count the number of songs per artist": count_songs_per_artist,
}

# Select the query
selected_query = st.selectbox(
    "Select the query to execute:",
    options=list(queries.keys()),
)

# Esegui la query selezionata
if selected_query:
    st.write(f"Query selected: {selected_query}")
    
    query_result, titles = queries[selected_query]()  # Chiama la funzione corretta
    
    # Se il risultato è una lista (es. da aggregate()), visualizzalo come tabella
    if isinstance(query_result, list):
        st.dataframe(query_result)
    else:
        st.write(f"{titles[0]}: {query_result}")

