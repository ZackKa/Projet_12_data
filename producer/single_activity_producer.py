import json # Permet de convertir les données en format JSON
from datetime import datetime # Permet de générer une date actuelle
from kafka import KafkaProducer # Permet d’envoyer des messages à Kafka

KAFKA_BROKER = "localhost:19092"  # au lieu de redpanda-0:9092 car on lance la commande docker-compose up -d dans le dossier kestra et non dans le dossier producer. car on est pas dans le conteneur redpanda.
TOPIC = "sport_activity" # Nom du topic Kafka cible

producer = KafkaProducer( # Initialise le producteur Kafka
    bootstrap_servers=KAFKA_BROKER, # Adresse du broker Kafka
    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8") # Convertit les données en JSON encodé en UTF-8
)

# ----------------------------
# Génération d'une seule activité
# ----------------------------
activity = {
    "id_salarie": 1,  # ID test
    "date_debut": datetime.now().isoformat(),
    "type_sport": "running",
    "distance_m": 5000,
    "duree_min": 30,
    "commentaire": "Séance test pour Slack ⚡"
} # Crée un événement de test simulant une activité sportive

# Envoi à Kafka
producer.send(TOPIC, value=activity) # Envoie le message au topic Kafka
producer.flush() # Force l’envoi de tous les messages en attente

print("✅ Activité test envoyée à Kafka :", activity)

# lancer python single_activity_producer.py pour envoyer une seule activité à Kafka et tester kestra ensuite. 
# Ce script sert à tester l'envoi de messages rapidement et ne pas attendre l'envoi de tous les messages, ce qui prend du temps