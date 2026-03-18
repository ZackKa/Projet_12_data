# README – POC Avantages Sportifs – Sport Data Solution
## 1. Contexte et problématique

**Sport Data Solution** est une start-up fondée par deux sportifs passionnés :

- Alexandre, leader d’un groupe de cyclistes,

- Juliette, marathonienne convaincue.

L’entreprise développe des solutions de monitoring et d’analyse de performance sportive pour des sportifs amateurs et semi-professionnels.

Juliette souhaite renforcer la culture sportive au sein de l’entreprise en proposant des avantages aux salariés qui pratiquent une activité physique régulière. 

### Objectifs métier

- Encourager un mode de vie sain

- Améliorer le bien-être des salariés

- Valoriser la pratique sportive en entreprise

- Mesurer l’impact financier des avantages proposés

## 2. Objectifs du POC

Ce Proof of Concept vise à :

1. Collecter et intégrer les données RH et sportives

2. Générer des données d’activités sportives réalistes (type Strava)

3. Calculer :

- une prime sportive (5% du salaire)

- des jours de bien-être

4. Mettre en place des tests de qualité des données

5. Automatiser le pipeline de bout en bout

6. Superviser les exécutions avec alerting

7. Préparer les données pour un dashboard PowerBI

## 3. Technologies et outils utilisés

| Catégorie           | Outils / Librairies |
|--------------------|------------------|
| **Orchestration**    | Kestra (orchestration des tâches ETL et automation Slack) |
| **Base de données**  | PostgreSQL (stockage des données RAW, STAGING, MART) |
| **Langage**          | Python (ingestion, transformation, simulation Strava, calcul des distances) |
| **Librairies**       | pandas, numpy, requests, openrouteservice, python-dateutil, sqlalchemy, psycopg2-binary, Faker, openpyxl,pytest |
| **API externe**       | OpenRouteService |
| **Visualisation**    | PowerBI (dashboard pour KPI et simulation d’impact financier) |
| **Conteneurisation**       | Docker / Docker Compose |
| **Simulation & tests** | Pytest pour les données sportives réalistes pour 12 mois, tests de cohérence et validation des données |
| **Communication interne** | Slack + email pour notifications |

## 4. Architecture du pipeline

#### Le pipeline suit une architecture en plusieurs couches :

[Sources Excel]
        ↓
[Ingestion Kestra]
        ↓
[PostgreSQL - RAW]
        ↓
[Transformation Python / SQL]
        ↓
[STAGING (données enrichies)]
        ↓
[Tests qualité (Pytest)]
        ↓
[MART (tables métiers)]
        ↓
[PowerBI Dashboard]

Monitoring :
- Logs Kestra
- Alertes Slack / Email


## 5. Infrastructure mise en place

Le projet utilise Docker Compose pour lancer l’ensemble de l’infrastructure :

- PostgreSQL (port interne `5432`, exposé sur `5433` sur la machine locale)

- Kestra (orchestration et exécution des tasks ETL, exposé sur `8080`)

### Docker

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

## 6. Variables d’environnement

Le projet utilise une clé API pour le calcul des distances et un webhook slack pour l'envoie des messages :

`ORS_API_KEY`
`SLACK_WEBHOOK`


## 7. Organisation des données

### RAW (données brutes)

- rh_raw : fichiers RH initiaux (identité, salaire, adresse, moyen de déplacement).

- sport_practice_raw : activités sportives déclarées par salarié.

- sports_activity_raw : historique simulé des activités sportives (12 mois, type Strava).

- config_parameters : règles paramétrables (taux prime, nombre minimum d’activités, distances max selon mode de déplacement).

### STAGING (données enrichies / transformées)

- employees_enriched : ajout des distances domicile-travail, validité des déclarations, âge, ancienneté.

- sports_activity_clean : nettoyage et validation des activités sportives simulées.

### MART (tables métier)

- fact_prime_sportive : calcul des primes 5%.

- fact_bien_etre : calcul des 5 journées bien-être.

- kpi_global : tableau de bord global pour PowerBI.

## 8. Pipeline Kestra – Description des tasks

Le workflow Kestra est organisé pour automatiser l’ensemble du POC, de l’ingestion à la simulation des activités sportives.

| Task ID                              | Description                                                                 |
|--------------------------------------|-----------------------------------------------------------------------------|
| **start**                            | Début du workflow et journalisation.                                        |
| **ingestion_all**                    | Création du dossier de travail et copie des fichiers RH et sportives.       |
| **check_data**                       | Vérification des fichiers importés : lecture, structure, doublons, valeurs manquantes. |
| **create_config_parameters**         | Paramétrage métier                                     |
| **create_raw_tables**                | Création des tables RAW : poc_rh_raw et poc_sportive_raw.                   |
| **load_raw_tables**                  | Lecture des fichiers Excel et insertion dans les tables RAW PostgreSQL.     |
| **test_poc_rh_raw**                  | Tests qualité RH                                   |
| **test_poc_sportive_raw**            | Tests qualité sport                                  |
| **create_rh_enriched_table**         | Création de la table poc_employees_enriched pour les données enrichies domicile-travail.     |
| **distances_domicile_travail**       | Calcul des distances domicile-travail via OpenRouteService et validation des déclarations. |
| **create_sport_activity_table**      | Création de la table poc_sport_activity pour stocker les activités sportives simulées. |
| **generate_sport_activity**          | Génération aléatoire et réaliste de plusieurs activités sportives par salarié avec commentaires. |
| **create_sport_activity_clean_table**| Nettoyage des données activité sportive                      |
| **test_poc_sport_activity_clean**    | Tests qualité activités                                |
| **create_fact_prime_sportive**       | Calcul des primes                                   |
| **create_fact_bien_etre**            | Calcul de la condition "bien-être"                                  |
| **create_kpi_global**                | Table finale KPI                                  |
| **notify_failure_email**             | Notifications Email                                  |
| **notify_failure_slack**             | Notifications Slack                                  |



## 9. Qualité des données et règles métiers

Des tests automatiques sont implémentés avec PyTest.

### Données RH

- Pas de valeurs nulles

- Pas de doublons

- salaire_brut > 0

- nb_cp ≥ 0

- Âge ≥ 18 ans à l’embauche

### Activités sportives

- id_salarie non NULL

- type_sport non NULL

 -distance ≥ 0

- duree_min > 0

- date_debut :

- pas dans le futur

- limitée à 1 an

### Nettoyage

Une table `poc_sport_activity_clean` filtre uniquement les données valides.

## 10. Monitoring et gestion des erreurs
### Surveillance

- Logs détaillés dans Kestra

- Suivi des exécutions

- Temps d’exécution observable

### Gestion des erreurs

- Retry automatique des tâches critiques

- Arrêt du pipeline si tests échouent

- Alertes automatiques :

    - Slack

    - Email

## 11. Paramétrage métier

Les règles sont externalisées dans la table :

`poc_config_parameters`

Exemples :

prime_rate = 5%

min_activities = 15

max_walk_km = 15

max_bike_km = 25

Permet d’adapter le pipeline sans modifier le code

## 12. Simulation des données

Les activités sportives sont générées avec :

- Faker (données réalistes)

- Logique métier (distance, durée)

- Historique sur 12 mois

- Commentaires dynamiques

## 13. Table KPIs générés

- Montant total des primes

- Nombre d’employés éligibles prime

- Nombre d’activités sportives

- Éligibilité bien-être

## 14. Instructions pour lancer le workflow

1. Lancer Docker Compose :
!!! Attention avant de lancer cette commande assurer vous d'avoir lancer docker (linux) ou docker desktop (windows/macOs)
```bash
docker-compose up -d
```
2. Vérifier que les conteneurs postgres et kestra sont en ligne.

3. Accéder à l’interface Kestra sur http://localhost:8080.

4. Importer le workflow pipeline_sport_p12 dans Kestra.

5. **!!! Pensez à mettre votre clé api. Vous pouvez en créer une sur le site de openrouteservice. Ainsi que votre Slack webhook créer sur slack pour recevoir les message**

6. Exécuter le workflow et suivre les logs pour validation.


## Notes techniques

Les distances domicile-travail sont calculées avec OpenRouteService (API key nécessaire).

Les activités sportives simulées sont générées aléatoirement mais avec des plages réalistes (distance, durée, fréquence).

Les commentaires sont générés automatiquement pour chaque activité.

## 15. Conclusion

Ce POC démontre la faisabilité d’un système complet :

- Pipeline automatisé

- Données fiables

- Calculs métiers

- Monitoring et alerting

Il constitue une base solide pour une industrialisation future.