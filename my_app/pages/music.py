import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from db_utils import get_local_connection, get_remote_connection, get_docker_connection
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os


st.set_page_config(page_title="Music Database", page_icon=":musical_note:", layout="wide", initial_sidebar_state = "collapsed")

if os.environ.get('DOCKER_BUILD') == "True":
    print("Docker build detected")
    db = get_docker_connection()
else:
    print("Docker build not detected")
    db = get_local_connection()

if "filters" not in st.session_state:
    st.session_state.filters = []

    # Definisci le query come funzioni
def count_tracks():
    return db.Track.distinct("Track.Name"), ["Number of Tracks", "Track Title"]

def count_albums():
    return db.Track.distinct("Album.Title"), ["Number of Albums", "Album Title"]

def count_genres():
    return db.Track.distinct("Genre.Name"), ["Number of Genres", "Genre Name"]

def count_artists():
    return db.Track.distinct("Artist.Name"), ["Number of Artists", "Artist Name"]

def count_playlists():
    return db.Track.distinct("Playlist.Name"), ["Number of Playlists", "Playlist Name"]

def count_songs_per_album():
    return list(db.Track.aggregate([
        {"$group": {"_id": "$Album.Title", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "Album": "$_id", "Number of tracks": "$count"}},
        {"$sort": {"Number of tracks": -1}}
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
        {"$project": {"_id": 0, "Artist": "$_id", "Number of tracks": "$count"}},
        {"$sort": {"Number of tracks": -1}}
    ])), None

def count_songs_per_playlist():
    return list(db.Track.aggregate([
        {"$unwind": "$Playlist"},
        {"$group": {"_id": "$Playlist.Name", "count": {"$sum": 1}}},
        {"$project": {"_id": 0, "Playlist": "$_id", "Number of tracks": "$count"}},
        {"$sort": {"Number of tracks": -1}}
    ])), None

def count_artists_per_playlist():
    return list(db.Track.aggregate([
        {"$unwind": "$Playlist"},
        {"$group": {"_id": "$Playlist.Name", "artists": {"$addToSet": "$Artist.Name"}}},
        {"$project": {"_id": 0, "Playlist": "$_id", "Artists": {"$size": "$artists"}}},
        {"$sort": {"Artists": -1}}
    ])), None

def albums_per_artist():
    return list(db.Track.aggregate([
        {"$group": {"_id": "$Artist.Name", "albums": {"$addToSet": "$Album.Title"}}},
        {"$project": {"_id": 0, "Artist": "$_id", "Albums": {"$size": "$albums"}}},
        {"$sort": {"Albums": -1}}
    ])), None  


central_col_width = 0.5
side_col_width = (1 - central_col_width) / 2

_, central_col, _ = st.columns([side_col_width, central_col_width, side_col_width])

with central_col:

    st.title("Chinook Database Query Selector")             
    type_of_query = st.selectbox("Select the type of query to execute:", ["Count", "Aggregate and Count", "Filtering"], index = None)

# Map the queries to functions
queries_count = {
    "Count the number of tracks": count_tracks,
    "Count the number of albums": count_albums,
    "Count the number of genres": count_genres,
    "Count the number of artists": count_artists,
    "Count the number of playlists": count_playlists,
}
queries_aggregate_and_count = {
    "Count the number of songs per album": count_songs_per_album,
    "Count the number of songs per genre": count_songs_per_genre,
    "Count the number of songs per artist": count_songs_per_artist,
    "Count the number of songs per playlist": count_songs_per_playlist,
    "Count the number of artists per playlist": count_artists_per_playlist,
    "Count the number of albums per artist": albums_per_artist
}




# Select the query
with central_col:
    if type_of_query == "Count":
        selected_query = st.selectbox("Select the query to execute:", list(queries_count.keys()), index = None)    
        queries = queries_count
    elif type_of_query == "Aggregate and Count":
        selected_query = st.selectbox("Select the query to execute:", list(queries_aggregate_and_count.keys()), index = None)
        queries = queries_aggregate_and_count
    else:
        selected_query = "Filtering"

# Esegui la query selezionata
if selected_query:
    
    
    # Se il risultato è una lista (es. da aggregate()), visualizzalo come tabella
    if type_of_query == "Aggregate and Count":
        query_result, titles = queries[selected_query]()  # Chiama la funzione corretta
        df = pd.DataFrame(query_result)

        fig_bar = go.Figure()
        fig_bar.add_trace(
            go.Bar(
                x = df[df.columns[0]].tolist(),
                y = df[df.columns[1]].tolist(),
                text = df[df.columns[1]].tolist(),
                textposition = 'auto',
                marker_color = 'indigo',

            )
        )

        fig_bar.update_layout(
            title = dict(
                text = f"Total number of {df.columns[1]} by {df.columns[0]}",
                font = dict(size = 20),
                xanchor = 'center',
                x = 0.5,
                yanchor = 'top',
            ),
            xaxis_title = df.columns[0],
            yaxis_title = df.columns[1],
            showlegend = False,
            height = 800,
        )
        with central_col:
            visual_mode = st.radio(
                "Select the visualization mode:",
                ("Bar Chart", "Table"),
                index=0,
                horizontal=True,
            )

        if visual_mode == "Bar Chart":
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        else:
            _, col, _ = st.columns([side_col_width, central_col_width, side_col_width])
            with col:
                st.dataframe(query_result)

        
    elif type_of_query == "Count":                                                     
        query_result, titles = queries[selected_query]()  # Chiama la funzione corretta
        with central_col:                             
            st.write(f"{titles[0]}: {len(query_result)}")
            details = st.toggle("Show details", False)
            if details:
                st.dataframe(query_result, column_config = {'value': titles[1]})
        
    elif type_of_query == "Filtering":

        # Bottone per aggiungere un filtro
        if st.button("Add a filter"):
            st.session_state.filters.append({"field": "", "operator": "", "value": ""})

        fields = {
            "Track Name": "Track.Name",
            "Album Title": "Album.Title",
            "Genre": "Genre.Name",
            "Artist Name": "Artist.Name",
            "Composer": "Track.Composer",
            "Playlist Name": "Playlist.Name",
            "Track length": "Track.Milliseconds",
            "Price (€)": "Track.UnitPrice",
            "Media type": "MediaType.Name"
        }

        columns = [
            "Track Name",
            "Album Title",
            "Genre",
            "Artist Name",
            "Composer",
            "Playlist Name",
            "Track length",
            "Price",
            "Media type"
        ]

        operator_map = {
            "=": "$eq",
            ">": "$gt",
            "<": "$lt",
            ">=": "$gte",
            "<=": "$lte",
            "!=": "$ne"
        }

        # Mostra tutti i filtri esistenti
        with st.expander("Filters", expanded=True):
            for i, f in enumerate(st.session_state.filters):
                col1, col2, col3, col4 = st.columns([3, 2, 4, 1])
                
                # Campo del filtro
                f["field"] = col1.selectbox(f"Field {i+1}", fields.keys(), key=f"field_{i}", index = None)
                
                if f["field"] == "Track length" or f["field"] == "Price":
                # Operatore (esempio: =, >, <, ecc.)
                    f["operator"] = col2.selectbox(f"Operator {i+1}", ["=", ">", "<", ">=", "<=", "!="], key=f"operator_{i}", index = None)

                else:
                    f["operator"] = col2.selectbox(f"Operator {i+1}", ["=", "!="], key=f"operator_{i}", index = None)

                values = db.Track.distinct(fields[f["field"]]) if f["field"] is not None else []
                
                # Valore del filtro
                if f["field"] == "Price":
                    f["value"] = col3.number_input(f"Value {i+1}", key=f"value_{i}", value = 0)
                elif f["field"] == "Track length":
                    minuts = col3.number_input(f"Minuts {i+1}", key=f"value_{i}_m", value = 0)
                    seconds = col3.number_input(f"Seconds {i+1}", key=f"value_{i}_s", value = 0)
                    f["value"] = minuts*60000 + seconds*1000
                else:
                    f["value"] = col3.selectbox(f"Value {i+1}", values, key=f"value_{i}", index = None)
                
                # Pulsante per rimuovere il filtro
                if col4.button("❌", key=f"remove_{i}"):
                    st.session_state.filters.pop(i)
                    st.rerun()  # Forza il refresh della UI dopo la rimozione

                # aggiungi un qualcosa per selezionare le colonne da visualizzare, la lista è columns

            selected_columns = st.multiselect("Select columns to display", columns, default=columns)

        # Esegui la query con i filtri

        if st.button("Execute query"):
            
            and_filters = []
            project = {}
            for f in st.session_state.filters:
                if f['field'] is not None and f['operator'] is not None and f['value'] is not None:
                    query = {fields[f["field"]]: {operator_map[f["operator"]]: f["value"]}}
                    and_filters.append(query)

            project = {
                "_id": 0,
                "Track Name": "$Track.Name" if "Track Name" in selected_columns else None,
                "Album Title": "$Album.Title" if "Album Title" in selected_columns else None,
                "Genre": "$Genre.Name" if "Genre" in selected_columns else None,
                "Artist Name": "$Artist.Name" if "Artist Name" in selected_columns else None,
                "Composer": "$Track.Composer" if "Composer" in selected_columns else None,
                "Playlist Name": "$Playlist.Name" if "Playlist Name" in selected_columns else None,
                "Track length": "$Track.Milliseconds" if "Track length" in selected_columns else None,
                "Price": "$Track.UnitPrice" if "Price" in selected_columns else None,
                "Media type": "$MediaType.Name" if "Media type" in selected_columns else None
            }

            # elimina le chiavi con valore None
            project = {k: v for k, v in project.items() if v is not None}



            query = {"$and": and_filters} if and_filters else {}
            # Esegui la query
            query_result = list(db.Track.find(query, project))

            # trasforma i millisecondi in minuti e secondi
            for q in query_result:
                if "Track length" in q:
                    q["Track length"] = f"{q['Track length'] // 60000}:{(q['Track length'] % 60000) // 1000:02}"

            # Visualizza il risultato
            st.write(f"Number of results: {len(query_result)}")
            st.dataframe(query_result)