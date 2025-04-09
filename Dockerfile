FROM python:3.12-slim

WORKDIR /app

ENV DOCKER_BUILD=True

# Copia le dipendenze e installa i pacchetti
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il progetto
COPY . .

CMD ["streamlit", "run", "my_app/app.py", "--server.address=0.0.0.0"]
