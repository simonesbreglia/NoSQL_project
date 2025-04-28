import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

@st.cache_resource

def get_docker_connection():
    url = "mongodb://mongodb:27017/"
    client = MongoClient(url)
    # controlla se esiste il db Chinook
    db = client['Chinook']
    # elimina il db Chinook se esiste
    if db in client.list_database_names():
        client.drop_database(db)
    return db["Chinook"]

def get_remote_connection():
    uri = st.secrets['mongo']['uri']
    client = MongoClient(uri, server_api=ServerApi('1'))
    return client['Chinook']

def get_local_connection():
    url = "mongodb://localhost:27017/"
    client = MongoClient(url)
    return client['Chinook']

def pin_g_mongo(client):
    try:
        client.admin.command('ping')
    except Exception as e:
        return False
    return True