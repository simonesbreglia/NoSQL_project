import time
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')

db = client['test-database']
collection = db['test-collection']

def test_inserimento(n):
    data = [{
        'Nome': f"User{i}",
        'Eta': 20 + i,
    }
        for i in range(n)]  
    start = time.time()
    collection.insert_many(data)
    end = time.time()
    return end - start
    
def test_lettura():
    start = time.time()
    list(collection.find(
        {"eta": {'$gt': 25}}
    ))
    end = time.time()
    return end - start



if __name__ == '__main__':
    print('Tempo di inserimento per 1000 record:', test_inserimento(1000))
    print('Tempo di lettura per 1000 record:', test_lettura())


