import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    backend: str      # auto | mock | gcp
    project: str
    bucket: str
    topic: str
    dataset: str
    table: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            backend=os.getenv("BACKEND", "auto"),
            project=os.getenv("GOOGLE_CLOUD_PROJECT", ""),
            bucket=os.getenv("GCS_BUCKET", "showcase-uploads"),
            topic=os.getenv("PUBSUB_TOPIC", "file-events"),
            dataset=os.getenv("BQ_DATASET", "showcase"),
            table=os.getenv("BQ_TABLE", "file_events"),
        )

    def use_gcp(self) -> bool:
        if self.backend == "gcp":
            return True
        if self.backend == "mock":
            return False
        # auto: use GCP only if a project and credentials are configured
        return bool(self.project and os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
