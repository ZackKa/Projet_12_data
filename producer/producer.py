import json
import time
import random
import uuid
from datetime import datetime, timedelta

import pandas as pd
import requests
from kafka import KafkaProducer
from faker import Faker
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# ----------------------------
# CONFIG
# ----------------------------
KAFKA_BROKER = "redpanda-0:9092"
TOPIC = "sport_activity"

FILE_RH = "/data/sport_data_solution/Donnees_RH.xlsx"
FILE_SPORT = "/data/sport_data_solution/Donnees_Sportive.xlsx"
# WEBHOOK_URL = os.getenv("SLACK_WEBHOOK") désactivé pour test rapide

# if WEBHOOK_URL is None:
#     raise ValueError("Le webhook Slack n'est pas défini dans le .env !") désactivé pour test rapide

fake = Faker("fr_FR")

sports_distance = ["runing","randonnée","vélo","triathlon","natation"]

moods = [
    "Motivation au top",
    "Super sensations",
    "Fatigué mais content",
    "Belle sortie",
    "Très bonne énergie"
]

weather = [
    "Sous le soleil",
    "Malgré la pluie",
    "Avec un peu de vent",
    "Temps parfait pour le sport"
]

# slack_templates = [
#     "🎉 Bravo {prenom} {nom} ! Super sortie de {sport} le {date} ! 💪",
#     "🏅 {prenom} {nom} a fait une belle séance de {sport} le {date} ! Continue comme ça !",
#     "🔥 {prenom} {nom}, ton activité {sport} du {date} est impressionnante !",
#     "⚡ {prenom} {nom} a accompli un superbe {sport} le {date} ! Félicitations !",
#     "💪 {prenom} {nom}, bravo pour ta séance de {sport} le {date} ! Gardons cette énergie !"
# ]

# ----------------------------
# KAFKA
# ----------------------------
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8")
)

# ----------------------------
# LOAD DATA
# ----------------------------
# df_rh = pd.read_excel(FILE_RH)
# df_sport = pd.read_excel(FILE_SPORT)

# df = pd.merge(df_rh, df_sport, on="ID salarié", how="inner")
# df = df[df["Pratique d'un sport"].notna()]

# print("Données chargées :", len(df))
try:
    df_rh = pd.read_excel(FILE_RH)
    df_sport = pd.read_excel(FILE_SPORT)
    df = pd.merge(df_rh, df_sport, on="ID salarié", how="inner")
    df = df[df["Pratique d'un sport"].notna()]
    print(f"Données chargées : {len(df)} salariés sportifs")
except Exception as e:
    print(f"Erreur lecture fichiers Excel : {e}")
    exit(1)

# ----------------------------
# GENERATION
# ----------------------------
total_generated = 0
today = datetime.now()

# Début du chrono
start_time = datetime.now() # Début du chrono pour mesurer le temps d'exécution

for _, row in df.iterrows():
    id_salarie = int(row["ID salarié"])
    sport = row["Pratique d'un sport"]
    sport_lower = sport.lower()

    nb_activities = random.randint(5, 30)

    for _ in range(nb_activities):

        # DATE
        random_days = random.randint(0, 365)
        date = today - timedelta(days=random_days)
        hour = random.randint(6, 21)
        minute = random.randint(0, 59)
        date_debut = date.replace(hour=hour, minute=minute, second=0)

        # DISTANCE / DUREE
        distance_m = None
        duree_min = random.randint(5, 120)

        if sport_lower in sports_distance:
            if sport_lower == "runing":
                distance_m = random.randint(3000, 15000)
            elif sport_lower == "randonnée":
                distance_m = random.randint(5000, 25000)
            elif sport_lower == "vélo":
                distance_m = random.randint(5000, 80000)
            elif sport_lower == "triathlon":
                distance_m = random.randint(30000, 70000)
            elif sport_lower == "natation":
                distance_m = random.randint(500, 3000)

            duree_min = int(distance_m / 200)

        # COMMENTAIRE (fidèle à ton Kestra)
        if random.random() < 0.3:
            commentaire = None
        else:
            if distance_m:
                km = distance_m / 1000

                if km < 3:
                    template = fake.random_element([
                        "Petite sortie de {sport} : {distance:.1f} km en {duree} min. 💪",
                        "{distance:.1f} km de {sport} parcourus rapidement en {duree} min. 😎"
                    ])
                elif km < 10:
                    template = fake.random_element([
                        "Séance de {sport} de {distance:.1f} km en {duree} min. 🔥",
                        "Super {sport} aujourd'hui : {distance:.1f} km en {duree} min ! ⚡"
                    ])
                else:
                    template = fake.random_element([
                        "Grosse sortie de {sport} : {distance:.1f} km en {duree} min. 🏅",
                        "Performance record : {distance:.1f} km de {sport} en {duree} min ! 💪"
                    ])

                commentaire = template.format(
                    sport=sport_lower,
                    distance=km,
                    duree=duree_min
                )
            else:
                if duree_min < 20:
                    template = fake.random_element([
                        "Petite séance de {sport} pendant {duree} min. 💪",
                        "Courte séance de {sport} de {duree} min. 😃"
                    ])
                elif duree_min < 60:
                    template = fake.random_element([
                        "Bonne séance de {sport} : {duree} min bien efficaces. 🔥",
                        "{duree} min de {sport}, super séance ! ⚡"
                    ])
                else:
                    template = fake.random_element([
                        "Grosse séance de {sport} : {duree} min d'effort intense ! 🏅",
                        "Longue séance de {sport} pendant {duree} min, top performance ! 💪"
                    ])

                commentaire = template.format(
                    sport=sport_lower,
                    duree=duree_min
                )

            commentaire += f" {fake.random_element(moods)}. {fake.random_element(weather)}."

        # EVENT FINAL
        activity = {
            # "id_activite": str(uuid.uuid4()), # generer automatiquement par postgres lors de la lescture avec kestra
            "id_salarie": id_salarie,
            "date_debut": date_debut.isoformat(),
            "type_sport": sport,
            "distance_m": distance_m,
            "duree_min": duree_min,
            "commentaire": commentaire
        }

        # SEND KAFKA
        try:
            producer.send(TOPIC, value=activity)
        except Exception as e:
            print(f"Erreur envoi Kafka pour {id_salarie} : {e}")

        # SLACK message encouragement et commentaire
        # message_template = fake.random_element(slack_templates)
        # message_text = message_template.format(
        #     prenom=row['Prénom'],
        #     nom=row['Nom'],
        #     sport=sport,
        #     date=date_debut.strftime('%d/%m/%Y %H:%M')
        # )

        # try:
        #     requests.post(WEBHOOK_URL, json={"text": message_text})
        # except Exception as e:
        #     print(f"Erreur Slack: {e}")

        # ----------------------------
        # SLACK - désactivé pour test rapide
        # ----------------------------
        # try:
        #     message_text = fake.random_element(slack_templates).format(
        #         prenom=row['Prénom'],
        #         nom=row['Nom'],
        #         sport=sport,
        #         date=date_debut.strftime('%d/%m/%Y %H:%M')
        #     )
        #     requests.post(WEBHOOK_URL, json={"text": message_text})
        # except Exception as e:
        #     print(f"Erreur Slack pour {id_salarie} : {e}")

        total_generated += 1

        if total_generated % 10 == 0:
            print(f"{total_generated} activités générées et envoyées")

        #time.sleep(0.1) # pause de 0.1 seconde pour version avec message Slack
        time.sleep(0.01) # pause de 0.01 seconde pour version sans message Slack

producer.flush()
# Fin du chrono
end_time = datetime.now()
elapsed = end_time - start_time

print(f"TOTAL : {total_generated} activités envoyées dans Kafka")
print(f"Temps total de génération : {elapsed.total_seconds():.2f} secondes")