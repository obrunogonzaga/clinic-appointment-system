# Patient Documents via Cloudflare R2

## Executive Summary

This feature enables clinics to attach supporting documents (medical orders, guides, imaging) to individual appointments. Uploads are executed directly from the browser to Cloudflare R2 using pre-signed URLs while the backend persists metadata only. A new "Documentos" section in the appointment detail modal allows collaborators and administrators to drop files, preview uploads, download existing documents through expiring links, and soft/hard delete entries with full audit metadata.

## Architecture Overview

1. **Pre-signed PUT** – The frontend requests `/api/v1/appointments/{appointmentId}/documents/presign-upload` providing file metadata and patient identifier. The API validates MIME/size, creates a pending document record, and returns a 10-minute pre-signed PUT URL plus mandatory headers.
2. **Direct upload** – The browser PUTs the file to R2 using the signed URL without proxying through the API.
3. **Confirmation** – After upload the UI calls `/confirm` with the document ID and optional ETag, allowing the API to mark the document as uploaded, record uploader, IP, and timestamps.
4. **Listing** – `/documents` returns non-deleted metadata per appointment scoped by tenant and role, used to render the list view.
5. **Download** – `/download-url` issues an expiring GET pre-sign so files are always fetched from R2.
6. **Deletion** – `DELETE /documents/{documentId}?hard=true|false` performs soft deletes by default (metadata retained, hidden from list) and hard deletes remove the object from R2 while keeping audit fields.

All endpoints enforce collaborator/admin authorization and tenant scoping via the `X-Tenant-ID` header (front-end uses the user department). Storage keys follow `patients/{patientId}/appointments/{appointmentId}/{yyyy}/{mm}/{uuid}_{sanitizedName}` to keep uploads organized.

## Environment Variables

Add the following to environment files (`.env.local`, `.env.staging`, `.env.prod`, etc.):

```env
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_PATIENT_DOCS=patient-docs
R2_PRESIGN_TTL_SECONDS=600
MAX_UPLOAD_MB=10
ALLOWED_MIME_LIST=application/pdf,image/jpeg,image/png,image/webp,image/heic
S3_ENDPOINT=
```

* `S3_ENDPOINT` should point to `http://localhost:9000` when using MinIO locally. Leave blank to auto-build `https://<R2_ACCOUNT_ID>.r2.cloudflarestorage.com` in production.
* `MAX_UPLOAD_MB` and `ALLOWED_MIME_LIST` are configurable and shared with the UI guidance.

## Local Testing Guide

### Path A – MinIO locally

1. **Boot MinIO:**
   ```bash
   docker run -p 9000:9000 -p 9001:9001 \
     -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin \
     minio/minio server /data
   ```
2. **Create bucket:** via MinIO console (`http://localhost:9001`) create `patient-docs` and apply CORS allowing origins `http://localhost:3000` and `http://localhost:5173` with `PUT`/`GET`, headers `*`, expose header `ETag`.
3. **Configure backend env:** set `S3_ENDPOINT=http://localhost:9000`, credentials `minioadmin/minioadmin`, bucket name, TTL, MIME list and 10 MB limit.
4. **Run stack:** `make dev-backend` and `make dev-frontend`.
5. **Validation flow:**
   - Use appointment detail modal → "Documentos" to upload both PDF and JPG ≤10 MB.
   - Attempt to upload a disallowed type (e.g., `.exe`) → expect 400 from presign.
   - Use browser dev tools to confirm signed GET expires after 10 minutes (re-request after TTL).
   - Soft delete hides the document from list; confirm record remains via Mongo shell.
   - Hard delete removes from list and object disappears from MinIO bucket.

### Path B – Cloudflare R2 directly

1. **Create R2 bucket:** from Cloudflare dashboard, create bucket (e.g., `patient-docs`) and generate API tokens for staging and prod.
2. **Configure CORS:** allow origins `http://localhost:3000` and `http://localhost:5173`, methods `GET,PUT`, headers `*`, expose `ETag`.
3. **Set `.env.local.r2`:** fill account ID, access key, secret, bucket name. Leave `S3_ENDPOINT` blank.
4. **Run backend/frontend** with the R2 env file loaded.
5. **Repeat checklist** from Path A using real R2 endpoints (monitor Cloudflare R2 bucket for uploads/deletes).

## Promotion to Coolify + R2

1. **App configuration:** In Coolify set environment variables identical to `.env.staging` / `.env.prod`, including bucket, keys, TTL, MIME list, max size, and optionally `S3_ENDPOINT` (usually blank for R2).
2. **Health checks:** ensure backend `/health` endpoint is configured in Coolify for deploy status.
3. **R2 CORS:**
   - Staging bucket: allow origins `https://clinica-staging.widia.io` (and frontend host).
   - Production bucket: allow origins `https://clinica.widia.io` plus API host as needed.
4. **Credentials:** Use separate Access Keys for staging and production buckets to avoid cross-environment access.
5. **Smoke test post-deploy:**
   - Upload valid PDF/JPG and confirm list renders.
   - Trigger download and verify link expires after TTL.
   - Run soft delete and ensure document hidden; attempt hard delete and verify object gone in R2.
   - Confirm collaborator (non-admin) cannot access another tenant (header mismatch → 403/404).

## Acceptance Checklist

- [ ] Upload valid files (≤10 MB, allowed MIME) succeeds via UI and stored metadata shows uploader, timestamps, tenant, key.
- [ ] Invalid MIME/oversized files rejected with clear message.
- [ ] Download link works immediately and expires after configured TTL.
- [ ] Soft delete hides document while metadata remains (check Mongo collection `patient_documents`).
- [ ] Hard delete removes object from storage and marks metadata with `hard_deleted_at`.
- [ ] Tenant scoping respected (`X-Tenant-ID` mismatch denies access).
- [ ] Audit fields (`uploaderUserId`, `uploadedAt`, `sourceIP`) populated after confirmation.

## Definition of Done

- Backend endpoints for presign, confirm, list, download, delete implemented with R2 integration and tenant-aware authorization.
- Mongo metadata persistence covers auditing, soft/hard delete, and storage key generation per specification.
- React appointment detail modal exposes upload dropzone, document list, download and delete actions respecting roles.
- `.env.example` documents new environment variables.
- Manual validation checklist executed for both MinIO (local) and R2 (cloud) paths.
- Documentation updated (this file) with rollout and testing guidance.
