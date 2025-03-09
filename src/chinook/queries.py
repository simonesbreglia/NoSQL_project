from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)

# Connessione a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['Chinook']

# Esempio di tabelle (collections) disponibili in MongoDB
tables = db.list_collection_names()

# Step 1: Selezione della tabella
@app.route('/', methods=['GET', 'POST'])
def select_table():
    if request.method == 'POST':
        selected_table = request.form['table']
        return redirect(url_for('select_query', table=selected_table))

    return render_template('select_table.html', tables=tables)


# Step 2: Selezione del tipo di query sulla tabella
@app.route('/select_query/<table>', methods=['GET', 'POST'])
def select_query(table):
    queries = ['Find All', 'Count', 'Filter']  # Esempio di query disponibili per una tabella
    
    if request.method == 'POST':
        query_type = request.form['query']
        if query_type == 'Find All':
            return redirect(url_for('show_results', table=table, query_type='find_all'))
        elif query_type == 'Count':
            return redirect(url_for('show_results', table=table, query_type='count'))
        elif query_type == 'Filter':
            return redirect(url_for('apply_filters', table=table, query_type='filter'))

    return render_template('select_query.html', table=table, queries=queries)


# Step 3: Applicare eventuali filtri sulla query
@app.route('/apply_filters/<table>/<query_type>', methods=['GET', 'POST'])
def apply_filters(table, query_type):
    if request.method == 'POST':
        # Qui aggiungi la logica per applicare i filtri
        filter_field = request.form.get('field')
        filter_value = request.form.get('value')
        
        if query_type == 'filter':
            query_results = db[table].find({filter_field: filter_value})
        return redirect(url_for('show_results', table=table, query_type=query_type))

    return render_template('apply_filters.html', table=table, query_type=query_type)


# Step 4: Visualizzazione dei risultati della query
@app.route('/show_results/<table>/<query_type>', methods=['GET', 'POST'])
def show_results(table, query_type):
    if query_type == 'find_all':
        query_results = db[table].find()
    elif query_type == 'count':
        query_results = db[table].count_documents({})
    elif query_type == 'filter':
        query_results = []  # Se hai filtrato, visualizza i risultati filtrati

    query_results = pd.DataFrame(list(query_results)) if query_results else None

    return render_template('show_results.html', query_results=query_results)


if __name__ == '__main__':
    app.run(debug=True)

