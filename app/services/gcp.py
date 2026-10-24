import json

from google.cloud import bigquery, pubsub_v1, storage


class GCSStorage:
    def __init__(self, project: str, bucket: str):
        self._client = storage.Client(project=project)
        self._bucket_name = bucket
        self._bucket = self._client.bucket(bucket)

    def upload(self, name: str, data: bytes, content_type: str) -> str:
        blob = self._bucket.blob(name)
        blob.upload_from_string(data, content_type=content_type)
        return f"gs://{self._bucket_name}/{name}"

    def list(self, prefix: str = "") -> list[str]:
        return [b.name for b in self._client.list_blobs(self._bucket_name, prefix=prefix)]


class PubSubPublisher:
    def __init__(self, project: str, topic: str):
        self._publisher = pubsub_v1.PublisherClient()
        self._topic_path = self._publisher.topic_path(project, topic)

    def publish(self, payload: dict) -> str:
        future = self._publisher.publish(
            self._topic_path, json.dumps(payload).encode("utf-8")
        )
        return future.result(timeout=10)  # blocks until Pub/Sub returns the message ID


class BigQueryWarehouse:
    def __init__(self, project: str, dataset: str, table: str):
        self._client = bigquery.Client(project=project)
        self._table_id = f"{project}.{dataset}.{table}"

    def insert(self, row: dict) -> None:
        errors = self._client.insert_rows_json(self._table_id, [row])
        if errors:
            raise RuntimeError(f"BigQuery insert failed: {errors}")

    def recent(self, limit: int) -> list[dict]:
        job = self._client.query(
            f"SELECT * FROM `{self._table_id}` ORDER BY uploaded_at DESC LIMIT @limit",
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("limit", "INT64", limit)]
            ),
        )
        return [dict(row) for row in job.result()]
