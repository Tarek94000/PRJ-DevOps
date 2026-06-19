# DevOps Reservation Project

Application de reservation de ressources construite pour le projet DevOps.

## Services

- `reservation-service`: API FastAPI principale avec architecture `controllers / services / data`.
- `notification-service`: API FastAPI separee appelee lors des reservations et annulations.
- `postgres`: base PostgreSQL lancee par Docker Compose.
- `frontend`: interface web statique optionnelle.

## Demarrage local avec Docker

```powershell
copy .env.example .env
docker compose up --build
```

Endpoints utiles :

- Reservation API: http://localhost:8000/docs
- Notification API: http://localhost:8001/docs
- Front Web: http://localhost:8080

## Developpement Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest --cov=backend --cov-report=term-missing
ruff check .
```

Si le dossier est synchronise par OneDrive et que coverage ne peut pas supprimer ses fichiers temporaires, lancer :

```powershell
$env:COVERAGE_FILE="$env:TEMP\devops-reservation.coverage"; pytest --cov=backend --cov-report=term-missing --cov-report=xml
```

## Rapport

Le rapport de projet est dans `docs/report.md`. Il contient les points a completer avec les captures de tests, couverture, qualite et Google Labs avant la remise Moodle.
