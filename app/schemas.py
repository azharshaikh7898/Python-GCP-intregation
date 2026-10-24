from datetime import datetime

from pydantic import BaseModel


class FileRecord(BaseModel):
    file_name: str
    uri: str
    size_bytes: int
    content_type: str
    uploaded_at: datetime
