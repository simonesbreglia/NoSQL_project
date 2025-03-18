import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from db_utils import get_local_connection, get_remote_connection
import requests



st.set_page_config(page_title="Chinook Database", page_icon=":musical_note:", layout="wide")

db = get_local_connection()

central_col_width = 0.5
side_col_width = (1 - central_col_width) / 2
_, central_col, _ = st.columns([side_col_width, central_col_width, side_col_width])

with central_col:
    st.title("Chinook Database")
    page = st.selectbox("Which database would you like to see?", ["Music", "Sales"], index = None)



if page == "Music":
    st.switch_page("pages/music.py")
elif page == "Sales":
    st.switch_page("pages/sales.py")
 

