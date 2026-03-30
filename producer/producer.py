import json # Permet de sérialiser les données en format JSON
import time # Permet de gérer des pauses dans l’exécution
import random # Permet de générer des valeurs aléatoires
from datetime import datetime, timedelta # Gestion des dates et calculs temporels

import pandas as pd # Manipulation de données tabulaires (DataFrame)
from kafka import KafkaProducer # Client Kafka pour produire des messages
from faker import Faker # Générateur de données fictives
from dotenv import load_dotenv # Permet de charger les variables d’environnement

# Charger les variables d'environnement depuis .env
load_dotenv()

# ----------------------------
# CONFIG
# ----------------------------
KAFKA_BROKER = "redpanda-0:9092" # Adresse du broker Kafka (Redpanda ici)
TOPIC = "sport_activity" # Nom du topic Kafka cible

FILE_RH = "/data/sport_data_solution/Donnees_RH.xlsx" # Chemin du fichier RH
FILE_SPORT = "/data/sport_data_solution/Donnees_Sportive.xlsx" # Chemin du fichier sportif

fake = Faker("fr_FR") # Initialise Faker avec des données localisées en français

sports_distance = ["runing","randonnée","vélo","triathlon","natation"] # Liste des sports pour lesquels on peut calculer la distance

moods = [
    "Motivation au top",
    "Super sensations",
    "Fatigué mais content",
    "Belle sortie",
    "Très bonne énergie"
] # Liste de phrases décrivant l’état physique

weather = [
    "Sous le soleil",
    "Malgré la pluie",
    "Avec un peu de vent",
    "Temps parfait pour le sport"
] # Liste de phrases décrivant les conditions météo

# ----------------------------
# KAFKA
# ----------------------------
producer = KafkaProducer( # Initialise le producteur Kafka
    bootstrap_servers=KAFKA_BROKER, # Adresse du broker Kafka
    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8") # Convertit les données en JSON encodé en UTF-8
)

# ----------------------------
# LOAD DATA
# ----------------------------
try:
    df_rh = pd.read_excel(FILE_RH) # Charge le fichier RH
    df_sport = pd.read_excel(FILE_SPORT) # Charge le fichier sportif
    df = pd.merge(df_rh, df_sport, on="ID salarié", how="inner") # Fusionne les deux fichiers sur la colonne "ID salarié"
    df = df[df["Pratique d'un sport"].notna()] # Supprime les lignes où la colonne "Pratique d'un sport" est vide
    print(f"Données chargées : {len(df)} salariés sportifs") # Affiche le nombre de salariés sportifs chargés
except Exception as e:
    print(f"Erreur lecture fichiers Excel : {e}") # Affiche l'erreur si la lecture des fichiers Excel échoue
    exit(1)

# ----------------------------
# GENERATION
# ----------------------------
total_generated = 0 # Initialise le compteur de messages générés
today = datetime.now() # Obtient la date et l'heure actuelle

# Début du chrono
start_time = datetime.now() # Début du chrono pour mesurer le temps d'exécution

for _, row in df.iterrows(): # Parcourt chaque salarié du dataset
    id_salarie = int(row["ID salarié"]) # Obtient l'ID du salarié
    sport = row["Pratique d'un sport"] # Obtient le sport pratiqué par le salarié
    sport_lower = sport.lower() # Convertit le sport en minuscules

    nb_activities = random.randint(5, 30) # Génère un nombre aléatoire de 5 à 30 activités pour chaque salarié

    for _ in range(nb_activities): # Parcourt chaque activité pour le salarié

        # DATE
        random_days = random.randint(0, 365) # Nombre de jours aléatoire dans le passé
        date = today - timedelta(days=random_days) # Soustrait le nombre de jours aléatoire à la date actuelle pour obtenir une date passée
        hour = random.randint(6, 21) # Heure aléatoire entre 6 et 21
        minute = random.randint(0, 59) # Minute aléatoire entre 0 et 59
        date_debut = date.replace(hour=hour, minute=minute, second=0) # Remplace l'heure, les minutes et les secondes pour construire la date complète

        # DISTANCE / DUREE
        distance_m = None # Initialise la distance à None
        duree_min = random.randint(5, 120) # Génère une durée aléatoire entre 5 et 120 minutes

        if sport_lower in sports_distance: # Si le sport est dans la liste des sports pour lesquels on peut calculer la distance
            if sport_lower == "runing":
                distance_m = random.randint(3000, 15000) # Distance aléatoire entre 3000 et 15000 mètres pour le running
            elif sport_lower == "randonnée":
                distance_m = random.randint(5000, 25000) # Distance aléatoire entre 5000 et 25000 mètres pour la randonnée
            elif sport_lower == "vélo":
                distance_m = random.randint(5000, 80000) # Distance aléatoire entre 5000 et 80000 mètres pour le vélo
            elif sport_lower == "triathlon":
                distance_m = random.randint(30000, 70000) # Distance aléatoire entre 30000 et 70000 mètres pour le triathlon
            elif sport_lower == "natation":
                distance_m = random.randint(500, 3000) # Distance aléatoire entre 500 et 3000 mètres pour la natation

            duree_min = int(distance_m / 200) # Calcul de la durée en minutes en divisant la distance par 200

        # COMMENTAIRE 
        if random.random() < 0.3: # 30% de chances de ne pas avoir de commentaire
            commentaire = None
        else:
            if distance_m:
                km = distance_m / 1000 # Conversion de la distance en kilomètres

                if km < 3: # Si la distance est inférieure à 3 km
                    template = fake.random_element([
                        "Petite sortie de {sport} : {distance:.1f} km en {duree} min. 💪",
                        "{distance:.1f} km de {sport} parcourus rapidement en {duree} min. 😎"
                    ])
                elif km < 10: # Si la distance est inférieure à 10 km
                    template = fake.random_element([
                        "Séance de {sport} de {distance:.1f} km en {duree} min. 🔥",
                        "Super {sport} aujourd'hui : {distance:.1f} km en {duree} min ! ⚡"
                    ])
                else: # Si la distance est supérieure à 10 km
                    template = fake.random_element([
                        "Grosse sortie de {sport} : {distance:.1f} km en {duree} min. 🏅",
                        "Performance record : {distance:.1f} km de {sport} en {duree} min ! 💪"
                    ])

                commentaire = template.format( # Remplit le template avec les valeurs
                    sport=sport_lower,
                    distance=km,
                    duree=duree_min
                )
            else:
                if duree_min < 20: # Si la durée est inférieure à 20 minutes
                    template = fake.random_element([
                        "Petite séance de {sport} pendant {duree} min. 💪",
                        "Courte séance de {sport} de {duree} min. 😃"
                    ])
                elif duree_min < 60: # Si la durée est inférieure à 60 minutes
                    template = fake.random_element([
                        "Bonne séance de {sport} : {duree} min bien efficaces. 🔥",
                        "{duree} min de {sport}, super séance ! ⚡"
                    ])
                else: # Si la durée est supérieure à 60 minutes
                    template = fake.random_element([
                        "Grosse séance de {sport} : {duree} min d'effort intense ! 🏅",
                        "Longue séance de {sport} pendant {duree} min, top performance ! 💪"
                    ])

                commentaire = template.format( # Remplit le template avec les valeurs
                    sport=sport_lower,
                    duree=duree_min
                )

            commentaire += f" {fake.random_element(moods)}. {fake.random_element(weather)}." # Ajoute un commentaire aléatoire de la liste des états physiques et des conditions météo

        # EVENT FINAL
        activity = { # Crée un dictionnaire avec les données de l'activité
            "id_salarie": id_salarie,
            "date_debut": date_debut.isoformat(),
            "type_sport": sport,
            "distance_m": distance_m,
            "duree_min": duree_min,
            "commentaire": commentaire
        }

        # SEND KAFKA
        try:
            producer.send(TOPIC, value=activity) # Envoie l'activité à Kafka
        except Exception as e:
            print(f"Erreur envoi Kafka pour {id_salarie} : {e}") # Affiche l'erreur si l'envoi à Kafka échoue

        total_generated += 1 # Incrémente le compteur de messages générés

        if total_generated % 10 == 0:
            print(f"{total_generated} activités générées et envoyées") # Affiche le nombre total de messages générés et envoyés toutes les 10 activités

        time.sleep(0.01) # pause de 0.01 seconde pour éviter le spam

producer.flush() # Force l’envoi de tous les messages en attente
# Fin du chrono
end_time = datetime.now() # Obtient la date et l'heure actuelle
elapsed = end_time - start_time # Calcul le temps d'exécution
print(f"TOTAL : {total_generated} activités envoyées dans Kafka") # Affiche le nombre total de messages générés et envoyés
print(f"Temps total de génération : {elapsed.total_seconds():.2f} secondes") # Affiche le temps d'exécution