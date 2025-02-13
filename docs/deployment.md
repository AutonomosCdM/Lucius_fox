# Deployment Guide

## Prerequisites
- Python 3.8+
- Docker
- Kubernetes (optional)

## Local Development Setup
```bash
# Clone repository
git clone https://github.com/autonomos/lucius_fox.git
cd lucius_fox

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env

# Run development server
python manage.py runserver
```

## Production Deployment
### Docker Setup
```bash
# Build Docker image
docker build -t lucius_fox .

# Run container
docker run -d \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  --name lucius_fox \
  lucius_fox
```

### Kubernetes Setup
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lucius-fox
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lucius-fox
  template:
    metadata:
      labels:
        app: lucius-fox
    spec:
      containers:
      - name: lucius-fox
        image: lucius_fox:latest
        ports:
        - containerPort: 8000
```

## Configuration
### Environment Variables
```bash
# Required
API_KEY=your_api_key
DATABASE_URL=postgres://user:pass@host:port/db

# Optional
LOG_LEVEL=INFO
MAX_WORKERS=4
```

## Monitoring
```bash
# Install monitoring tools
helm install prometheus prometheus-community/prometheus
helm install grafana grafana/grafana

# Configure dashboards
kubectl apply -f monitoring/dashboards.yaml
```
