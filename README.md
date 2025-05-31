# Progetto Big Data Simone Sbreglia

Questo repository contiene il __progetto di Big Data__ per il corso_Big Data Analytics_. Come negli altri progetti, specifico che ho seguito le consegne degli informatici perchè ho scelto il corso completo da 9 CFU tra gli esami a libera scelta.

Il progetto comprende una __sperimentazione di MongoDB__, un database NoSQL. Lo scopo del progetta era implementare un'interfaccia grafica che permettesse di creare query statiche e dinamiche collegandosi al database. Tutto il progetto è scritto in Python, anche l'interfaccia grafica è stata implementata tramite la libreria _Streamlit_.

Nel seguito sono elencate le istruzioni per l'esecuzione. Il progetto è stato scritto in __Python 3.2.17__.

## Istruzioni per l'esecuzione

1. **Clona il repository**
    ```bash
    git clone https://github.com/simonesbreglia/NoSQL_project
    cd NoSQL_project
    ```

2. **Crea un ambiente virtuale**

    - **Linux/MacOS**
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

    - **Windows**
      ```cmd
      python -m venv venv
      venv\Scripts\activate
      ```

3. **Installa le dipendenze**
    ```bash
    pip install -r requirements.txt
    ```

4. **Esecuzione**
    
    1. **MongoDB**: assicurati che il server MongoDB sia attivo e accessibile all'indirizzo predefinito `mongodb://localhost:27017/`.  
        Se desideri collegarti a un'istanza diversa (ad esempio su un altro host o porta), modifica l'URI di connessione nella funzione `get_local_connection` presente nel file `my_app/db_utils.py`.

    2. **Avvia l'applicazione**

        - **Linux/MacOS**
          ```bash
          python3 run_app.py
          ```
        - **Windows**
          ```cmd
          python run_app.py
          ```
        Il database verrà popolato ad ogni avvio.
        

    3. **Connettersi all'applicazione**

        Una volta avviata, l'applicazione sarà accessibile tramite browser all'indirizzo [http://localhost:8501](http://localhost:8501).

    4. **Note aggiuntive**

        - Assicurati che tutte le dipendenze siano installate correttamente.
        - In caso di problemi di connessione a MongoDB, verifica che il servizio sia in esecuzione e che le impostazioni dell'URI siano corrette.

5. **Docker**: per avviare l'applicazione tramite Docker, posizionati nella cartella principale del progetto e utilizza il comando:

    ```bash
    docker compose up
    ```

    Questo comando avvierà sia il server MongoDB che l'applicazione Streamlit tramite i servizi definiti nel file `docker-compose.yml`.  
    Una volta avviato, l'applicazione sarà accessibile all'indirizzo [http://localhost:8501](http://localhost:8501).

    Per interrompere i servizi, premi `CTRL+C` e poi esegui:

    ```bash
    docker compose down
    ```
    L'esecuzione tramite docker è stata testa solamente in sistemi Linux. Non è garantito il funzionamento in altri sistemi operativi.
        
    