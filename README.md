# README – POC Avantages Sportifs – Sport Data Solution
## 1. Contexte et problématique

**Sport Data Solution** est une start-up fondée par deux sportifs passionnés :

- Alexandre, leader d’un groupe de cyclistes,

- Juliette, marathonienne convaincue.

L’entreprise développe des solutions de monitoring et d’analyse de performance sportive pour des sportifs amateurs et semi-professionnels.

Juliette souhaite renforcer la culture sportive au sein de l’entreprise en proposant des avantages aux salariés qui pratiquent une activité physique régulière. 

## 2. Objectifs métier

- Encourager un mode de vie sain

- Améliorer le bien-être des salariés

- Valoriser la pratique sportive en entreprise

- Mesurer l’impact financier des avantages proposés

## 3. Objectifs du POC

Ce Proof of Concept vise à :

1. Collecter et intégrer les données RH et sportives

2. Générer des données d’activités sportives réalistes (type Strava)

3. Mettre en place une architecture hybride batch + streaming

4. Calculer :

        - une prime sportive (5% du salaire)

        - des jours de bien-être

5. Mettre en place des tests de qualité des données

6. Automatiser le pipeline de bout en bout

7. Superviser les exécutions avec alerting

8. Préparer les données pour un dashboard PowerBI

## 4. Technologies et outils utilisés

| Catégorie           | Outils / Librairies |
|--------------------|------------------|
| **Orchestration**    | Kestra (orchestration des tâches ETL et automation Slack) |
| **Base de données**  | PostgreSQL (stockage des données RAW, STAGING, MART) |
| **Streaming**        | Redpanda (Kafka API compatible) |
| **Message broker**   | Kafka (via Redpanda) |
| **Langage**          | Python (ingestion, transformation, simulation Strava, calcul des distances) |
| **Librairies**       | pandas, numpy, requests, openrouteservice, python-dateutil, sqlalchemy, psycopg2-binary, Faker, openpyxl,pytest |
| **API externe**       | OpenRouteService |
| **Visualisation**    | PowerBI (dashboard pour KPI et simulation d’impact financier) |
| **Conteneurisation**       | Docker / Docker Compose |
| **Simulation & tests** | Pytest pour les données sportives réalistes pour 12 mois, tests de cohérence et validation des données |
| **Communication interne** | Slack + email pour notifications |

## 5. Architecture du pipeline

#### Le pipeline suit une architecture en plusieurs couches :

```text
                   [Sources Excel]
                          │
          ┌───────────────┴───────────────┐
          │                               │
 [Ingestion Kestra (Batch)]   [Producer Python → Redpanda / Kafka → Consumer Kestra (Streaming)]
          │                               │
          └───────────────┬───────────────┘
                          │
                 [PostgreSQL - RAW]
                          │
             [Transformation Python / SQL]
                          │
               [STAGING (données enrichies)]
                          │
                 [Tests qualité (Pytest)]
                          │
                 [MART (tables métiers)]
                          │
                 [PowerBI Dashboard]
```
#### Type d’architecture

Le pipeline combine :

- Batch → ingestion des données RH

- Streaming → ingestion des activités sportives

Monitoring :
- Logs Kestra
- Alertes Slack / Email


## 6. Infrastructure mise en place

Le projet utilise Docker Compose pour lancer l’ensemble de l’infrastructure :

- PostgreSQL (port interne `5432`, exposé sur `5433` sur la machine locale)

- Kestra (orchestration et exécution des tasks ETL, exposé sur `8080`)

### Docker

Conteneurs :

- `postgres` : stockage des données

- `kestra` : orchestration ETL et scripts Python

- `redpanda-0` : broker Kafka

- `redpanda-console` : interface Kafka

- `producer` : simulation des activités

Volumes persistants :

- `postgres-data-projet12`

- `kestra-data-projet12`

- `redpanda-data`

### Dockerfile Kestra

Les Dockerfiles personnalisés installent Python 3 et les librairies nécessaires pour :

- L’ingestion et le traitement des fichiers Excel,

- L’appel à l’API OpenRouteService pour calculer les distances domicile-travail,

- La génération de données simulées type Strava,

- La communication avec PostgreSQL.

## 7. Variables d’environnement

Le projet utilise une clé API pour le calcul des distances et un webhook slack pour l'envoie des messages.

Ces informations peuvent être définies soit dans un fichier .env, soit dans les secrets de Kestra. Pour un POC, il est aussi possible de les mettre directement dans le code, mais cela n’est pas sécurisé pour un usage en production.

Vous devez créer un .env à la racine du projet avec :

`ORS_API_KEY=*******`
`SLACK_WEBHOOK=*******`


## 8. Organisation des données

### RAW (données brutes)

- rh_raw : fichiers RH initiaux (identité, salaire, adresse, moyen de déplacement).

- sport_practice_raw : activités sportives déclarées par salarié.

- sports_activity_raw : historique simulé des activités sportives (12 mois, type Strava).

- config_parameters : règles paramétrables (taux prime, nombre minimum d’activités, distances max selon mode de déplacement).

- poc_sport_activity_messages : Pour avoir un historique des messages d'encouragement envoyés sur Slack

### STAGING (données enrichies / transformées)

- employees_enriched : ajout des distances domicile-travail, validité des déclarations, âge, ancienneté.

- sports_activity_clean : nettoyage et validation des activités sportives simulées.

### MART (tables métier)

- fact_prime_sportive : calcul des primes 5%.

- fact_bien_etre : calcul des 5 journées bien-être.

- kpi_global : tableau de bord global pour PowerBI.

## 9. Pipeline Kestra – Description des tasks

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
| **consume_kafka_sport_activity**     | Consommation des données Kafka |
| **create_table_message_slack**       | Création de la table poc_sport_activity_messages pour l'historique des messages slack.     |
| **send_encouragement_messages**      | Task qui envoie des messages slack pour chaque activité     |
| **create_sport_activity_clean_table**| Nettoyage des données activité sportive                      |
| **test_poc_sport_activity_clean**    | Tests qualité activités                                |
| **create_fact_prime_sportive**       | Calcul des primes                                   |
| **create_fact_bien_etre**            | Calcul de la condition "bien-être"                                  |
| **create_kpi_global**                | Table finale KPI                                  |
| **create_kpi_global_monitoring**     | Sert pour afficher logs   |
| **log_final_summary**                | Affiche les logs de volumétrie   |
| **notify_failure_email**             | Notifications Email                                  |
| **notify_failure_slack**             | Notifications Slack                                  |


## 10. Simulation des données (Streaming)

Les activités sportives sont générées via un **producer Python**.

### Fonctionnement

1. Lecture fichiers Excel

2. Génération d’activités réalistes

3. Envoi dans Kafka (`sport_activity`)

### Objectif

Simuler une API type Strava en temps réel.

### Consommation

Kestra récupère les événements et les stocke dans PostgreSQL.


## 11. Qualité des données et règles métiers

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

## 12. Monitoring et gestion des erreurs

Le pipeline intègre plusieurs mécanismes pour garantir fiabilité, traçabilité et détection des anomalies.

### Suivi et surveillance

- Logs détaillés et suivi des exécutions dans Kestra
- Retry automatique pour les tâches critiques
- Temps d’exécution observable
- Indicateurs de volumétrie calculés via `Kestra.outputs()` :
  - Lignes RH chargées (`rh_rows`)
  - Lignes sport (`sport_rows`)
  - Activités sportives (`nb_activities_kafka`)
  - Lignes KPI global (`nb_kpi_rows`)

Ces métriques permettent de détecter rapidement toute anomalie et de suivre l’évolution des volumes.

### Gestion des alertes

- Arrêt du pipeline si les tests échouent
- Alertes automatiques :
  - Slack
  - Email

Un résumé global est affiché en fin de pipeline, donnant une lecture rapide de l’état et des performances.

## 13. Paramétrage métier

Les règles sont externalisées dans la table :

`poc_config_parameters`

Exemples :

        - prime_rate = 5%

        - min_activities = 15

        - max_walk_km = 15

        - max_bike_km = 25

Permet d’adapter le pipeline sans modifier le code

## 14. Simulation des données (`producer.py`)

Les activités sportives sont générées avec :

- Faker (données réalistes)

- Logique métier (distance, durée)

- Historique sur 12 mois

- Commentaires dynamiques

## 15. Table KPIs générés

- Montant total des primes

- Nombre d’employés éligibles prime

- Nombre d’activités sportives

- Éligibilité bien-être

## 16. Dashboard Power BI

Les données finales permettent de visualiser :

- primes

- activité sportive

- éligibilité

- impact financier

## 17. Instructions pour lancer le workflow

1. Lancer Docker Compose :
!!! Attention avant de lancer cette commande assurer vous d'avoir lancer docker (linux) ou docker desktop (windows/macOs)
```bash
docker-compose up -d

**A savoir** cette commande lance tout le projet, donc en cas de réexécution du projet, pensez à commenter le produceur dans docker-compose.yaml du dossier Kestra, pour ne pas avoir de nouvelles données sportives créées qui seront ajoutées aux anciennes.

```
2. Vérifier que les conteneurs postgres et kestra sont en ligne.

3. Accéder à l’interface Kestra sur http://localhost:8080.

4. Importer le workflow **pipeline_sport_p12** dans **Kestra**. Vous le trouverez dans le fichier `code_kestra.yaml`

5. **!!! Pensez à mettre votre clé api dans un fichier .env à la racine du projet. Vous pouvez en créer une sur le site de openrouteservice. Ainsi que votre Slack webhook créer sur slack pour recevoir les message**

6. Exécuter le workflow et suivre les logs pour validation.

## Notes techniques

Les distances domicile-travail sont calculées avec OpenRouteService (API key nécessaire).

Les activités sportives simulées sont générées aléatoirement mais avec des plages réalistes (distance, durée, fréquence).

Les commentaires sont générés automatiquement pour chaque activité.

## 18. Conclusion

Ce POC démontre la faisabilité d’un système complet :

- Pipeline automatisé

- Données fiables

- Calculs métiers

- Monitoring et alerting

Il constitue une base solide pour une industrialisation future.