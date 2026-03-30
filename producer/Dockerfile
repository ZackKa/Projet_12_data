# FROM python:3.11-slim
FROM python:3.10-slim

WORKDIR /app
# Définit le répertoire de travail dans le conteneur

COPY requirements.txt . 
# Copie le fichier requirements.txt dans le conteneur
RUN pip install --no-cache-dir -r requirements.txt
# Installe les dépendances sans stocker de cache pour alléger l’image

COPY producer.py .
# Copie le script principal du producteur dans le conteneur

CMD ["python", "producer.py"] 
# Lance le script principal du producteur