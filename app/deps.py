from dataclasses import dataclass
from functools import lru_cache

from app.config import Settings
from app.services.base import PublisherService, StorageService, WarehouseService
from app.services.mock import InMemoryPublisher, InMemoryStorage, InMemoryWarehouse


@dataclass
class Services:
    storage: StorageService
    publisher: PublisherService
    warehouse: WarehouseService
    mode: str


def build_mock_services(settings: Settings) -> Services:
    return Services(
        storage=InMemoryStorage(settings.bucket),
        publisher=InMemoryPublisher(),
        warehouse=InMemoryWarehouse(),
        mode="mock",
    )


@lru_cache
def get_services() -> Services:
    settings = Settings.from_env()
    if not settings.use_gcp():
        return build_mock_services(settings)

    # Imported lazily so mock mode never touches GCP libraries/credentials
    from app.services.gcp import BigQueryWarehouse, GCSStorage, PubSubPublisher

    return Services(
        storage=GCSStorage(settings.project, settings.bucket),
        publisher=PubSubPublisher(settings.project, settings.topic),
        warehouse=BigQueryWarehouse(settings.project, settings.dataset, settings.table),
        mode="gcp",
    )
