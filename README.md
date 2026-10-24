# GCP Showcase API

FastAPI service integrating Cloud Storage, BigQuery and Pub/Sub.
Upload a file, and it is stored in GCS, logged to BigQuery, and announced on Pub/Sub.

**Design:** services sit behind Protocol interfaces. With no GCP credentials the app
runs on in-memory fakes (`BACKEND=auto|mock|gcp`), so the full test suite runs offline.

## Run
    pip install -r requirements.txt
    pytest
    uvicorn app.main:app --reload

## Run against real GCP
    export BACKEND=gcp GOOGLE_CLOUD_PROJECT=<project> GCS_BUCKET=<bucket>
    export GOOGLE_APPLICATION_CREDENTIALS=<key.json>
    uvicorn app.main:app

## Endpoints
POST /files · GET /files · GET /events · GET /health
