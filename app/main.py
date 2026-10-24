from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile

from app.deps import Services, get_services
from app.schemas import FileRecord

app = FastAPI(title="GCP Showcase API", version="1.0.0")

# Endpoints are plain `def` on purpose: GCP clients are blocking, and FastAPI
# runs sync endpoints in a threadpool so they don't block the event loop.


@app.get("/health")
def health(svc: Services = Depends(get_services)):
    return {"status": "ok", "backend": svc.mode}


@app.post("/files", response_model=FileRecord, status_code=201)
def upload_file(file: UploadFile = File(...), svc: Services = Depends(get_services)):
    data = file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    safe_name = Path(file.filename or "upload").name  # strip any path components
    object_name = f"{uuid4().hex[:8]}-{safe_name}"
    content_type = file.content_type or "application/octet-stream"

    uri = svc.storage.upload(object_name, data, content_type)          # 1. Cloud Storage
    record = {
        "file_name": object_name,
        "uri": uri,
        "size_bytes": len(data),
        "content_type": content_type,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
    }
    svc.warehouse.insert(record)                                       # 2. BigQuery
    svc.publisher.publish({"event": "file.uploaded", **record})        # 3. Pub/Sub
    return record


@app.get("/files")
def list_files(prefix: str = "", svc: Services = Depends(get_services)):
    return {"files": svc.storage.list(prefix)}


@app.get("/events", response_model=list[FileRecord])
def recent_events(limit: int = 10, svc: Services = Depends(get_services)):
    limit = max(1, min(limit, 100))  # clamp to a safe range
    return svc.warehouse.recent(limit)
