# Rapport Projet DevOps

## Sujet

L'application permet de reserver des ressources, par exemple des salles. Elle expose une API de reservation, un service de notification separe, une base PostgreSQL et une interface web simple.

## Architecture logicielle

```mermaid
flowchart LR
  Front[Frontend Web] --> API[reservation-service FastAPI]
  API --> Controller[Controllers]
  Controller --> Service[Services]
  Service --> Data[Data / Repositories]
  Data --> DB[(PostgreSQL)]
  Service --> Notify[notification-service FastAPI]
```

## Architecture Docker

```mermaid
flowchart LR
  Browser --> Frontend[frontend:8080]
  Browser --> Reservation[reservation-service:8000]
  Reservation --> Postgres[(postgres:5432)]
  Reservation --> Notification[notification-service:8001]
```

## Tests et couverture

Commande :

```powershell
pytest --cov=backend --cov-report=term-missing --cov-report=html
```

Sous OneDrive, utiliser `%TEMP%` pour le fichier coverage si Windows bloque la suppression des fichiers temporaires.

Captures a ajouter avant la remise :

- resultat des tests unitaires.
- rapport de couverture.
- pipeline GitHub Actions reussi.

## Qualite logicielle

Commande :

```powershell
ruff check .
```

Si SonarCloud est configure, ajouter une capture du tableau de bord qualite.

## Google Labs

Ajouter ici les captures d'ecran des Google Labs faits, comme demande dans le sujet.
