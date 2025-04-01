import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import requests

@st.cache_resource

def get_docker_connection():
    url = "mongodb://mongodb:27017/"
    client = MongoClient(url)
    pin = pin_g_mongo(client)
    if pin == False:
        return get_remote_connection()
    return client['Chinook']

def get_remote_connection():
    uri = st.secrets['mongo']['uri']
    client = MongoClient(uri, server_api=ServerApi('1'))
    pin = pin_g_mongo(client)
    if pin == False:
        st.error("MongoDB connection failed. Please check your credentials.")
        return None
    return client['Chinook']

def get_local_connection():
    url = "mongodb://localhost:27017/"
    client = MongoClient(url)
    pin = pin_g_mongo(client)
    if pin == False:
        return get_docker_connection()
    return client['Chinook']

def pin_g_mongo(client):
    try:
        client.admin.command('ping')
    except Exception as e:
        return False
    return True