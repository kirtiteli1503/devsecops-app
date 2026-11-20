# devsecops-app

Small Flask + PostgreSQL notes API used as the vehicle for an end-to-end DevSecOps pipeline
(GitHub Actions, Trivy, Gitleaks, ECR, Terraform, EKS, Helm, ArgoCD, Prometheus/Grafana).

## Endpoints
| Method | Path | Description |
|---|---|---|
| GET | /health | Liveness check |
| GET | /metrics | Prometheus metrics |
| GET | /notes | List notes |
| POST | /notes | Create note `{"title": "...", "body": "..."}` |
| GET | /notes/<id> | Get one note |
| DELETE | /notes/<id> | Delete note |

## Run locally
```bash
docker compose up --build
curl localhost:5000/health
curl -X POST localhost:5000/notes -H 'Content-Type: application/json' -d '{"title":"hello"}'
curl localhost:5000/notes
```

## Run tests
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

**Stack:** Flask, PostgreSQL, Docker, Docker Compose
