# DevOps Reservation Project

Application de reservation de salles et ressources construite pour le projet DevOps.

## Services

- `reservation-service`: API FastAPI principale avec architecture `controllers / services / data`.
- `notification-service`: API FastAPI separee appelee lors des creations, modifications et annulations.
- `postgres`: base PostgreSQL lancee par Docker Compose.
- `frontend`: tableau de bord web statique servi par Nginx.

## Demarrage local avec Docker

```powershell
copy .env.example .env
docker compose up --build
```

Endpoints utiles :

- Reservation API: http://localhost:8000/docs
- Notification API: http://localhost:8001/docs
- Front Web: http://localhost:8080

Si un ancien volume PostgreSQL contient le schema minimal precedent, supprimer ou recreer le volume Docker avant de tester les nouvelles colonnes.

## Fonctionnalites

- Creation et listing des utilisateurs.
- Creation, listing, consultation, modification et desactivation logique des ressources.
- Creation, listing, consultation, modification et annulation des reservations.
- Dashboard de statistiques globales.
- Notifications typees pour `reservation_created`, `reservation_updated` et `reservation_cancelled`.

## Principaux endpoints

| Methode | Chemin | Usage |
| --- | --- | --- |
| `GET` | `/health` | Etat de l'API reservation |
| `POST` | `/users` | Creer un utilisateur |
| `GET` | `/users` | Lister les utilisateurs |
| `GET` | `/users/{id}` | Lire un utilisateur |
| `POST` | `/resources` | Creer une ressource |
| `GET` | `/resources` | Lister les ressources |
| `GET` | `/resources/{id}` | Lire une ressource |
| `PATCH` | `/resources/{id}` | Modifier une ressource |
| `DELETE` | `/resources/{id}` | Desactiver une ressource |
| `POST` | `/reservations` | Creer une reservation |
| `GET` | `/reservations` | Lister les reservations |
| `GET` | `/reservations/{id}` | Lire une reservation |
| `PATCH` | `/reservations/{id}` | Modifier une reservation |
| `POST` | `/reservations/{id}/cancel` | Annuler une reservation |
| `GET` | `/dashboard` | Statistiques globales |

## Regles metier

- Une reservation doit finir apres son debut.
- Une ressource inactive ne peut pas etre reservee.
- Le nombre de participants ne peut pas depasser la capacite de la ressource.
- Les conflits de creneau sont detectes a la creation et a la modification.
- Une reservation deja annulee ne peut pas etre annulee une seconde fois.
- Une reservation annulee ne peut pas etre modifiee.

## Developpement Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ruff check .
pytest --cov=backend --cov-report=term-missing --cov-report=xml
```

Si le dossier est synchronise par OneDrive et que coverage ne peut pas supprimer ses fichiers temporaires, lancer :

```powershell
$env:COVERAGE_FILE="$env:TEMP\devops-reservation.coverage"; pytest --cov=backend --cov-report=term-missing --cov-report=xml
```

La CI GitHub Actions execute :

- `ruff check .` pour la qualite statique Python.
- `pytest --cov=backend --cov-report=term-missing --cov-report=xml --cov-fail-under=80` pour les tests unitaires, API et le seuil minimal de couverture.
- `docker compose config` puis `docker compose build` pour valider les fichiers Docker et la construction des services.
- SonarCloud si le secret `SONAR_TOKEN` est configure dans le depot.

Dependabot verifie chaque semaine les dependances `pip` et les actions GitHub afin de proposer des mises a jour de securite et maintenance.

## Outils externes requis

- Docker Desktop pour lancer PostgreSQL, les APIs et le frontend.
- GitHub pour l'hebergement du code.
- GitHub Actions pour l'integration continue.
- SonarCloud si l'analyse qualite est activee avec `SONAR_TOKEN`.
- Google Cloud Skills Boost ou Google Labs selon la consigne Moodle.

## Rapport

Le rapport de projet est dans `docs/report.md`. Il contient les sections architecture, regles metier, tests, qualite logicielle et captures Google Labs a joindre avant la remise Moodle.
