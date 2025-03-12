from flask import Flask, render_template, request
from pymongo import MongoClient

app = Flask(__name__)

# Connessione al database
client = MongoClient("mongodb://localhost:27017/")
db = client["Chinook_optimized"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    # Otteniamo il tipo di query selezionato
    query_type = request.form['query_type']

    if query_type == "count_tracks":
        result = db.Track.count_documents({})
        mongo_query = "db.Track.count_documents({})"
        result_data = [{"Risultato": result}]
    elif query_type == "count_album":
        result = len(db.Track.distinct("Album.AlbumId"))
        mongo_query = "db.Track.distinct('Album.AlbumId')"
        result_data = [{"Risultato": result}]
    elif query_type == "count_genres":
        result = len(db.Track.distinct("Genre.GenreId"))
        mongo_query = "db.Track.distinct('Genre.GenreId')"
        result_data = [{"Risultato": result}]
    elif query_type == "count_artists":
        result = len(db.Track.distinct("Artist.ArtistId"))
        mongo_query = "db.Track.distinct('Artist.ArtistId')"
        result_data = [{"Risultato": result}]
    elif query_type == "count_playlists":
        result = len(db.Track.distinct("Playlist.PlaylistId"))
        mongo_query = "db.Track.distinct('Playlist.PlaylistId')"
        result_data = [{"Risultato": result}]
    elif query_type == "songs_per_album":
        result = db.Track.aggregate([
            {
                "$group": {
                    "_id": "$Album.Title",
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "value": "$_id",
                    "count": 1
                }
            },
            {
                "$sort": {"count": -1}
            }
        ])
        mongo_query = "db.Track.aggregate([{$group: {_id: '$Album.Title', count: {$sum: 1}}, {$project: {_id: 0, Album: '$_id', Count: 1}}, {$sort: {Count: -1}}])"
        result_data = list(result)
        return render_template('results_2.html', result_data=result_data, mongo_query=mongo_query, column_titles=["Album", "Numero di Canzoni"])
    elif query_type == "songs_per_genre":
        result = db.Track.aggregate([
            {
                "$group": {
                    "_id": "$Genre.Name",
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "value": "$_id",
                    "count": 1
                }
            },
            {
                "$sort": {"count": -1}
            }
        ])
        mongo_query = "db.Track.aggregate([{$group: {_id: '$Genre.Name', count: {$sum: 1}}, {$project: {_id: 0, Genre: '$_id', Count: 1}}, {$sort: {Count: -1}}])"
        result_data = list(result)
        return render_template('results_2.html', result_data=result_data, mongo_query=mongo_query, column_titles=["Genere", "Numero di Canzoni"], column_keys=["Genre", "count"])
    
    elif query_type == "songs_per_artist":
        result = db.Track.aggregate([
            {
                "$group": {
                    "_id": "$Artist.Name",
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "value": "$_id",
                    "count": 1
                }
            },
            {
                "$sort": {"count": -1}
            }
        ])
        mongo_query = "db.Track.aggregate([{$group: {_id: '$Artist.Name', count: {$sum: 1}}, {$project: {_id: 0, Artist: '$_id', Count: 1}}, {$sort: {Count: -1}}])"
        result_data = list(result)
        return render_template('results_2.html', result_data=result_data, mongo_query=mongo_query, column_titles=["Artista", "Numero di Canzoni"], column_keys=["Artist", "count"])
    elif query_type == "songs_per_playlist":
        result = db.Track.aggregate([
            {
                "$unwind": "$Playlist"
            },
            {
                "$group": {
                    "_id": "$Playlist.Name",
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "value": "$_id",
                    "count": 1
                }
            },
            {
                "$sort": {"count": -1}
            }
        ])
        mongo_query = "db.Track.aggregate([{$unwind: '$Playlist'}, {$group: {_id: '$Playlist.Name', count: {$sum: 1}}, {$project: {_id: 0, Playlist: '$_id', Count: 1}}, {$sort: {Count: -1}}])"
        result_data = list(result)
        return render_template('results_2.html', result_data=result_data, mongo_query=mongo_query, column_titles=["Playlist", "Numero di Canzoni"], column_keys=["Playlist", "count"])
    elif query_type == "artists_per_playlist":
        result = db.Track.aggregate([
            {
                "$unwind": "$Playlist"
            },
            {
                "$group": {
                    "_id": "$Playlist.Name",
                    "artists": {"$addToSet": "$Artist.Name"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "value": "$_id",
                    "count": {"$size": "$artists"}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ])
        mongo_query = "db.Track.aggregate([{$unwind: '$Playlist'}, {$group: {_id: '$Playlist.Name', artists: {$addToSet: '$Artist.Name'}}, {$project: {_id: 0, Playlist: '$_id', Count: {$size: '$artists'}}}, {$sort: {Count: -1}}])"
        result_data = list(result)
        return render_template('results_2.html', result_data=result_data, mongo_query=mongo_query, column_titles=["Playlist", "Numero di Artisti"], column_keys=["Playlist", "count"])    
    elif query_type == "albums_per_artist":
        result = db.Track.aggregate([
            {
                "$unwind": "$Artist"
            },
            {
                "$group": {
                    "_id": "$Artist.Name",
                    "albums": {"$addToSet": "$Album.Title"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "value": "$_id",
                    "count": {"$size": "$albums"}
                }
            },
            {
                "$sort": {"count": -1}
            }
        ])   
        mongo_query = "db.Track.aggregate([{$unwind: '$Artist'}, {$group: {_id: '$Artist.Name', albums: {$addToSet: '$Album.Title'}}, {$project: {_id: 0, Artist: '$_id', Count: {$size: '$albums'}}}, {$sort: {Count: -1}}])"
        result_data = list(result)
        return render_template('results_2.html', result_data=result_data, mongo_query=mongo_query, column_titles=["Artista", "Numero di Album"], column_keys=["Artist", "count"]) 
    else:
        result_data = []
        mongo_query = "Invalid query type"
    
    return render_template('results.html', result_data=result_data, mongo_query=mongo_query)

if __name__ == "__main__":
    app.run(debug=True)
