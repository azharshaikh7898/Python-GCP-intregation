from uuid import uuid4


class InMemoryStorage:
    def __init__(self, bucket: str):
        self.bucket = bucket
        self.objects: dict[str, tuple[bytes, str]] = {}

    def upload(self, name: str, data: bytes, content_type: str) -> str:
        self.objects[name] = (data, content_type)
        return f"gs://{self.bucket}/{name}"

    def list(self, prefix: str = "") -> list[str]:
        return sorted(n for n in self.objects if n.startswith(prefix))


class InMemoryPublisher:
    def __init__(self):
        self.messages: list[dict] = []

    def publish(self, payload: dict) -> str:
        message_id = str(uuid4())
        self.messages.append({"id": message_id, "data": payload})
        return message_id


class InMemoryWarehouse:
    def __init__(self):
        self.rows: list[dict] = []

    def insert(self, row: dict) -> None:
        self.rows.append(row)

    def recent(self, limit: int) -> list[dict]:
        return list(reversed(self.rows))[:limit]
