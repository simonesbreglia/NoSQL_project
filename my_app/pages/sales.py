import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from db_utils import get_local_connection, get_remote_connection
import requests



st.set_page_config(page_title="Sales Database", page_icon=":chart_with_upwards_trend:", layout="wide")

db = get_local_connection()

central_col_width = 0.5
side_col_width = (1 - central_col_width) / 2

_, central_col, _ = st.columns([side_col_width, central_col_width, side_col_width])

with central_col:
    st.title("Sales Database")
    