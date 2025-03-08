from faker import Faker
from pymongo import MongoClient
import random 
import time



class FillingDatabase():
    def __init__(self, db, collections):
        self.db = db
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client[self.db]
        self.users = self.db[collections[0]]
        self.transactions = self.db[collections[1]]

        self.user_id = 0
        self.transaction_id = 0

    def generate_user(self):
        fake = Faker()
        user = {}
        user['_id'] = self.user_id
        user['name'] = fake.name()
        user['birth_date'] = str(fake.date_of_birth(minimum_age=18, maximum_age=90))
        user['email'] = user['name'].replace(' ', '.') + str(user['_id']) + '@' + fake.domain_name()
        user['phone'] = fake.phone_number() 
        user['address'] = fake.address()
        self.user_id += 1
        return user
    
    def generate_transaction(self, user_id):
        fake = Faker()
        transaction = {}
        transaction['_id'] = {
            'transaction_id': self.transaction_id,
            'user_id': user_id
        }
        transaction['product_id'] = fake.random_int(1, 100)
        transaction['quantity'] = fake.random_int(1, 10)
        transaction['price'] = round( random.uniform(0, 1) * random.randint(10, 100), 2)
        transaction['date'] = str(fake.date_this_year())
        transaction['payment_method'] = fake.random_element(['credit_card', 'paypal', 'cash'])
        transaction['shipping_address'] = fake.address()
        transaction['billing_address'] = None if random.random() > 0.5 else fake.address()
        self.transaction_id += 1
        return transaction
    
    def fill_users(self, n):
        start = time.time()
        for i in range(n):
            self.users.insert_one(self.generate_user())
        end = time.time()

        print('Tempo di inserimento per', n, 'utenti:', end - start)

    def fill_transactions(self, n):
        start = time.time()
        for i in range(n):
            user_id = random.randint(0, self.user_id-1)
            transaction = self.generate_transaction(user_id)
            self.transactions.insert_one(transaction)
        end = time.time()

        print('Tempo di inserimento per', n, 'transazioni:', end - start)


if __name__ == '__main__':

    db = 'test_1'
    collections = ['users', 'transactions']
    
    # chiedi all'utente il numero di utenti e transazioni da inserire

    try :
        n_users = int(input('Inserisci il numero di utenti da inserire: '))
    except ValueError:
        print('Inserire un numero intero')
        n_users = int(input('Inserisci il numero di utenti da inserire: '))

    try :
        n_transactions = int(input('Inserisci il numero di transazioni da inserire: '))
    except ValueError:
        print('Inserire un numero intero')
        n_transactions = int(input('Inserisci il numero di transazioni da inserire: '))


    db = FillingDatabase(db, collections)
    db.fill_users(n_users)
    db.fill_transactions(n_transactions)

