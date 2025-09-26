"""Utility client for interacting with Cloudflare R2 using boto3."""

from __future__ import annotations

import asyncio
from typing import Dict, Optional

import boto3
from botocore.client import Config

from src.infrastructure.config import Settings


class R2StorageClient:
    """Minimal wrapper around boto3 for generating presigned URLs."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = self._build_client()

    def _build_client(self):
        endpoint = self._settings.r2_endpoint_url
        session = boto3.session.Session()
        return session.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=self._settings.r2_access_key_id,
            aws_secret_access_key=self._settings.r2_secret_access_key,
            region_name="auto",
            config=Config(signature_version="s3v4"),
        )

    @property
    def bucket(self) -> str:
        bucket = self._settings.r2_bucket_patient_docs
        if not bucket:
            raise ValueError("R2_BUCKET_PATIENT_DOCS não está configurado")
        return bucket

    def generate_presigned_put(
        self,
        *,
        key: str,
        content_type: str,
        expires_in: Optional[int] = None,
        extra_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, object]:
        """Generate a presigned PUT URL for direct uploads."""

        params = {
            "Bucket": self.bucket,
            "Key": key,
            "ContentType": content_type,
        }
        if extra_headers:
            params.update(extra_headers)

        url = self._client.generate_presigned_url(
            "put_object",
            Params=params,
            ExpiresIn=expires_in or self._settings.r2_presign_ttl_seconds,
        )
        return {"url": url, "headers": {"Content-Type": content_type}}

    def generate_presigned_get(
        self, *, key: str, expires_in: Optional[int] = None
    ) -> str:
        """Generate a presigned GET URL for temporary downloads."""

        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in or self._settings.r2_presign_ttl_seconds,
        )

    async def delete_object(self, *, key: str) -> None:
        """Delete an object from the bucket asynchronously."""

        await asyncio.to_thread(
            self._client.delete_object, Bucket=self.bucket, Key=key
        )
