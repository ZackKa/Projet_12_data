import json
from datetime import datetime
import random
from kafka import KafkaProducer

KAFKA_BROKER = "localhost:19092"  # au lieu de redpanda-0:9092 car on lance la commande docker-compose up -d dans le dossier kestra et non dans le dossier producer. car on est pas dans le conteneur redpanda.
TOPIC = "sport_activity"

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8")
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
}

# Envoi à Kafka
producer.send(TOPIC, value=activity)
producer.flush()

print("✅ Activité test envoyée à Kafka :", activity)

# lancer python single_activity_producer.py pour envoyer une seule activité à Kafka et tester kestra ensuite. 
# Ce script sert à tester l'envoi de messages rapidement et ne pas attendre l'envoi de tous les messages, ce qui prend du temps