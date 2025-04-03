import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from db_utils import get_local_connection, get_remote_connection, get_docker_connection
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random

def query_music(
        db : MongoClient,
        field : str,            # can be "Artist.Name", "Album.Title", "Track.Name", "Genre.Name"
        selected_option : list, # list of artists, albums, tracks or genres
        ):
    # una query raccoglie le vendite totali per ogni oggetto selezionato
    # una query raccoglie date di vendite e importo per ogni data

    


st.set_page_config(page_title="Sales Database", page_icon=":chart_with_upwards_trend:", layout="wide", initial_sidebar_state="collapsed")

db = get_local_connection()

if "run" not in st.session_state:
    st.session_state.run = False
if "back" not in st.session_state:
    st.session_state.back = False


st.markdown(
    """
    <h1 style='text-align: center;'>Sales Database</h1>
    """,
    unsafe_allow_html=True
)

fields = {
           "Artist": "Artist.Name",
           "Album": "Album.Title",
           "Track": "Track.Name",
            "Genre": "Genre.Name",
        }

def run_true():
    st.session_state.run = True
def run_false():
    st.session_state.run = False

central_column_width = 0.4
side_column_width = (1 - central_column_width) / 2
_, central_column, _ = st.columns([side_column_width, central_column_width, side_column_width])

with central_column:
    decision = st.selectbox(
        label = "Start by choosing whether to view sales by employee, customer, or music",
        options = ("Sales by Employee", "Sales by Customer", "Sales by Music"),
        index=None,
        on_change=run_false
    )
    if decision == "Sales by Music":
        music_decision = st.selectbox(
            label = "Now you can choose weather to select a track, an album, an artist or a genre",
            options = ("Track", "Album", "Artist", "Genre"),
            index=None,
            on_change=run_false
        )
        if music_decision:
            options = db.Track.distinct(fields[music_decision]) if not None else []
            options = sorted(options)
            options.insert(0, "Select All")
            selected_option = st.multiselect(
                label = f"Select {music_decision}, select multiple options for comparing sales",
                options = options,
                on_change=run_false,
            )
            if "Select All" in selected_option:
                selected_option = options[1:]  # Exclude "Select All" from the selection
            
            if selected_option:
                st.session_state.run = False
                run = st.button(label = "Run Query", use_container_width=True)
                if run:
                    run_true()

if st.session_state.run == True:
    
    if decision == "Sales by Music":
        # grafico temporale per le vendite di ogni oggetto selezionato

        if len(selected_option) > 1:
            # aggiungo un istogramma per riassumere le vendite totali



        



    