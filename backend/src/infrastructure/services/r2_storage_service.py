"""Service responsible for interacting with Cloudflare R2 / S3-compatible storage."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from src.domain.base import DomainException
from src.infrastructure.config import Settings


class R2StorageService:
    """Wrapper around boto3 to generate pre-signed URLs and manage objects."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: Optional[BaseClient] = None

    @property
    def bucket_name(self) -> str:
        bucket = self._settings.r2_bucket_patient_docs
        if not bucket:
            raise DomainException(
                "Bucket para documentos de pacientes não configurado"
            )
        return bucket

    def _resolve_endpoint(self) -> str:
        if self._settings.s3_endpoint:
            return self._settings.s3_endpoint
        if self._settings.r2_account_id:
            return (
                f"https://{self._settings.r2_account_id}.r2.cloudflarestorage.com"
            )
        raise DomainException(
            "Endpoint S3/R2 não configurado. Defina S3_ENDPOINT ou R2_ACCOUNT_ID."
        )

    def _client_instance(self) -> BaseClient:
        if self._client is None:
            endpoint = self._resolve_endpoint()
            config = Config(signature_version="s3v4", retries={"max_attempts": 3})
            self._client = boto3.client(
                "s3",
                endpoint_url=endpoint,
                aws_access_key_id=self._settings.r2_access_key_id,
                aws_secret_access_key=self._settings.r2_secret_access_key,
                region_name="auto",
                config=config,
            )
        return self._client

    def generate_presigned_put(
        self, key: str, *, content_type: str, expires_in: int
    ) -> str:
        try:
            return self._client_instance().generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
            )
        except (ClientError, BotoCoreError) as exc:
            raise DomainException(
                "Não foi possível gerar URL de upload para o documento"
            ) from exc

    def generate_presigned_get(self, key: str, *, expires_in: int) -> str:
        try:
            return self._client_instance().generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )
        except (ClientError, BotoCoreError) as exc:
            raise DomainException(
                "Não foi possível gerar URL de download para o documento"
            ) from exc

    def delete_object(self, key: str) -> None:
        try:
            self._client_instance().delete_object(
                Bucket=self.bucket_name, Key=key
            )
        except (ClientError, BotoCoreError) as exc:
            raise DomainException(
                "Falha ao remover arquivo do storage de documentos"
            ) from exc

    def build_expiration(self) -> datetime:
        ttl_seconds = self._settings.r2_presign_ttl_seconds
        return datetime.utcnow() + timedelta(seconds=ttl_seconds)
