
import pandas as pd
import numpy as np
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from my_app.db_utils import get_local_connection, get_remote_connection, get_docker_connection


# client = MongoClient(uri, server_api=ServerApi('1'))
db = get_local_connection()

Track = db['Track']
Invoice = db['Invoice']
Customer = db['Customer']
Employee = db['Employee']

# torna indietro di due cartelle
path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)) + '/data/ChinookDataset/'

if db.my_collection.estimated_document_count() == 0:
        
    # Caricamento del dataset
    dfs = {}
    table_names = ['Album', 'Artist', 'Customer', 'Employee', 'Genre', 'Invoice', 'InvoiceLine', 'MediaType', 'Playlist', 'PlaylistTrack', 'Track']

    for table in table_names:
        dfs[table] = pd.read_csv(path + table + '.csv')
        dfs[table].index = np.arange(1, len(dfs[table]) + 1)

    # scorro le righe del dataframe 'Tracks' 

    for i in range(len(dfs['Track'])):
        record = dfs['Track'].loc[i+1]
        entry = {
            "Track": {
                "TrackId": int(record['TrackId']),
                "Name": record['Name'],
                "Composer": record['Composer'],
                "Milliseconds": int(record['Milliseconds']),
                "Bytes": int(record['Bytes']),
                "UnitPrice": float(record['UnitPrice'])
            },
            "Album": {
                "AlbumId": int(record['AlbumId']),
                "Title": dfs['Album'].loc[record['AlbumId']]['Title']
            },
            "Artist": {
                "ArtistId": int(dfs['Album'].loc[record['AlbumId']]['ArtistId']),
                "Name": dfs['Artist'].loc[dfs['Album'].loc[record['AlbumId']]['ArtistId']]['Name']
            },
            "MediaType": {
                "MediaTypeId": int(record['MediaTypeId']),
                "Name": dfs['MediaType'].loc[record['MediaTypeId']]['Name']
            },
            "Genre": {
                "GenreId": int(record['GenreId']),
                "Name": dfs['Genre'].loc[record['GenreId']]['Name']
            },
            "Playlist": [
                {
                    "PlaylistId": int(actual_record['PlaylistId']),
                    "Name": dfs['Playlist'].loc[actual_record['PlaylistId']]['Name']
                }
                for actual_record in dfs['PlaylistTrack'].loc[dfs['PlaylistTrack']['TrackId'] == (record['TrackId'] + 1)].to_dict(orient='records')
            ]
        }

        Track.insert_one(entry)

    for i in range(len(dfs['Invoice'])):
        record = dfs['Invoice'].loc[i+1]

        entry = {
            "InvoiceId": int(record['InvoiceId']),
            "InvoiceDate": record['InvoiceDate'],
            "BillingAddress": {
                "BillingAddress": record['BillingAddress'],
                "BillingCity": record['BillingCity'],
                "BillingState": record['BillingState'],
                "BillingCountry": record['BillingCountry'],
                "BillingPostalCode": record['BillingPostalCode'],
            },
            "Total": float(record['Total']),
            "CustomerId": int(record['CustomerId']),
            "SupportRepId": int(dfs['Customer'].loc[record['CustomerId']]['SupportRepId']),
            "InvoiceLines": [
                {
                    "InvoiceLineId": int(actual_record['InvoiceLineId']),
                    "TrackId": int(actual_record['TrackId']),
                    "UnitPrice": float(actual_record['UnitPrice']),
                    "Quantity": int(actual_record['Quantity'])
                }
                for actual_record in dfs['InvoiceLine'][dfs['InvoiceLine']['InvoiceId'] == (record['InvoiceId'])].to_dict(orient='records')
            ]
        }

        Invoice.insert_one(entry)

    
        
    for i in range(len(dfs['Customer'])):
        record = dfs['Customer'].loc[i+1]

        entry = {
            "CustomerId": int(record['CustomerId']),
            "FirstName": record['FirstName'],
            "LastName": record['LastName'],
            "Company": record['Company'],
            "Address": {
                "Address": record['Address'],
                "City": record['City'],
                "State": record['State'],
                "Country": record['Country'],
                "PostalCode": record['PostalCode'],
            },
            "Phone": record['Phone'],
            "Fax": record['Fax'],
            "Email": record['Email']
        }

        Customer.insert_one(entry)

    for i in range(len(dfs['Employee'])):
        record = dfs['Employee'].loc[i+1]

        entry = {
            "EmployeeId": int(record['EmployeeId']),
            "FirstName": record['FirstName'],
            "LastName": record['LastName'],
            "Title": record['Title'],
            "ReportsTo": int(record['ReportsTo']) if not pd.isnull(record['ReportsTo']) else None,
            "BirthDate": record['BirthDate'],
            "HireDate": record['HireDate'],
            "Address": {
                "Address": record['Address'],
                "City": record['City'],
                "State": record['State'],
                "Country": record['Country'],
                "PostalCode": record['PostalCode'],
            },
            "Phone": record['Phone'],
            "Fax": record['Fax'],
            "Email": record['Email']
        }

        Employee.insert_one(entry)

    print("Database popolato con successo!")    

else:
    print("Il database è già popolato. Nessuna azione necessaria.")