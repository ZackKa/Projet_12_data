# README – POC Avantages Sportifs – Sport Data Solution
## Contexte et problématique

**Sport Data Solution** est une start-up fondée par deux sportifs passionnés :

- Alexandre, leader d’un groupe de cyclistes,

- Juliette, marathonienne convaincue.

L’entreprise développe des solutions de monitoring et d’analyse de performance sportive pour des sportifs amateurs et semi-professionnels.

Juliette souhaite renforcer la culture sportive au sein de l’entreprise en proposant des avantages aux salariés qui pratiquent une activité physique régulière. L’objectif est double :

1. Encourager un mode de vie actif et sain pour les employés.

2. Valoriser l’équilibre entre performance professionnelle et bien-être personnel, tout en favorisant l’esprit d’équipe.

Le POC (Proof of Concept) a pour but de tester la faisabilité technique d’un système de récompenses sportives et d’évaluer son impact financier sur l’entreprise.

## Objectifs du POC

1. Collecter et traiter les données RH et sportives des salariés.

2. Générer un historique de pratiques sportives simulées (type Strava).

3. Calculer l’éligibilité aux primes sportives (5% du salaire annuel) et aux 5 journées bien-être.

4. Automatiser la publication de messages de félicitations sur Slack.

5. Fournir un dashboard PowerBI avec les principaux indicateurs financiers et sportifs.

## Technologies et outils utilisés

| Catégorie           | Outils / Librairies |
|--------------------|------------------|
| **Orchestration**    | Kestra (orchestration des tâches ETL et automation Slack) |
| **Base de données**  | PostgreSQL (stockage des données RAW, STAGING, MART) |
| **Langage**          | Python (ingestion, transformation, simulation Strava, calcul des distances) |
| **Librairies Python**| pandas, numpy, requests, openrouteservice, python-dateutil, sqlalchemy, psycopg2-binary, Faker, openpyxl |
| **Visualisation**    | PowerBI (dashboard pour KPI et simulation d’impact financier) |
| **Simulation & tests** | Génération de données sportives réalistes pour 12 mois, tests de cohérence et validation des données |
| **Communication interne** | Slack  pour notifications automatiques |


## Infrastructure mise en place

Le projet utilise Docker Compose pour lancer l’ensemble de l’infrastructure :

- PostgreSQL (port interne `5432`, exposé sur `5433` sur la machine locale)

- Kestra (orchestration et exécution des tasks ETL, exposé sur `8080`)

### Docker Compose

Conteneurs :

- `postgres` : stockage des données

- `kestra` : orchestration ETL et scripts Python

Volumes persistants :

- `postgres-data-projet12`

- `kestra-data-projet12`

### Dockerfile Kestra

Le Dockerfile personnalisé installe Python 3 et les librairies nécessaires pour :

- L’ingestion et le traitement des fichiers Excel,

- L’appel à l’API OpenRouteService pour calculer les distances domicile-travail,

- La génération de données simulées type Strava,

- La communication avec PostgreSQL.

## Organisation des données

### RAW (données brutes)

- rh_raw : fichiers RH initiaux (identité, salaire, adresse, moyen de déplacement).

- sport_practice_raw : activités sportives déclarées par salarié.

- sports_activity_raw : historique simulé des activités sportives (12 mois, type Strava).

### STAGING (données enrichies / transformées)

- employees_enriched : ajout des distances domicile-travail, validité des déclarations, âge, ancienneté.

- sports_activity_clean : nettoyage et validation des activités sportives simulées.

### MART (tables métier)

- fact_prime_sportive : calcul des primes 5%.

- fact_bien_etre : calcul des 5 journées bien-être.

- kpi_global : tableau de bord global pour PowerBI.

- config_parameters : règles paramétrables (taux prime, nombre minimum d’activités, distances max selon mode de déplacement).

## Pipeline Kestra – Description des tasks

Le workflow Kestra est organisé pour automatiser l’ensemble du POC, de l’ingestion à la simulation des activités sportives.

| Task ID                        | Description                                                                 |
|--------------------------------|-----------------------------------------------------------------------------|
| **start**                      | Début du workflow et journalisation.                                        |
| **ingestion_all**              | Création du dossier de travail et copie des fichiers RH et sportives.       |
| **check_data**                 | Vérification des fichiers importés : lecture, structure, doublons, valeurs manquantes. |
| **create_raw_tables**          | Création des tables RAW : poc_rh_raw et poc_sportive_raw.                   |
| **load_raw_tables**            | Lecture des fichiers Excel et insertion dans les tables RAW PostgreSQL.     |
| **create_rh_enriched_table**   | Création de la table poc_employees_enriched pour les données enrichies.     |
| **distances_domicile_travail** | Calcul des distances domicile-travail via OpenRouteService et validation des déclarations. |
| **create_sport_activity_table**| Création de la table poc_sport_activity pour stocker les activités sportives simulées. |
| **generate_sport_activity**    | Génération aléatoire et réaliste de plusieurs activités sportives par salarié avec commentaires. |

Chaque tâche est indépendante et réutilisable, avec logs et vérifications pour faciliter le debug et le monitoring.

## Instructions pour lancer le workflow

1. Lancer Docker Compose :
!!! Attention avant de lancer cette commande assurer vous d'avoir lancer docker (linux) ou docker desktop (windows/macOs)
```bash
docker-compose up -d
```
2. Vérifier que les conteneurs postgres et kestra sont en ligne.

3. Accéder à l’interface Kestra sur http://localhost:8080
.

4. Importer le workflow pipeline_sport_p12 dans Kestra.

**!!! Pensez à mettre votre clé api. Vous pouvez en créer une sur le site de openrouteservice**

5. Exécuter le workflow et suivre les logs pour validation.

6. Les données RAW, STAGING et simulées seront disponibles dans PostgreSQL pour les étapes suivantes (MART, calcul primes et visualisation PowerBI).

## Notes techniques

Les distances domicile-travail sont calculées avec OpenRouteService (API key nécessaire).

Les activités sportives simulées sont générées aléatoirement mais avec des plages réalistes (distance, durée, fréquence).

Les commentaires sont générés automatiquement pour chaque activité.

Toutes les données sensibles (RH) sont stockées dans PostgreSQL et peuvent être sécurisées via permissions et chiffrement si nécessaire.