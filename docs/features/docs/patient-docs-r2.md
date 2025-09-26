# Patient Documents via Cloudflare R2

## Executive Summary
- Introduces document management per appointment with metadata stored in MongoDB and files stored in Cloudflare R2 (or any S3-compatible storage).
- Adds API endpoints for upload presign, confirmation, listing, download, and deletion with tenant-aware authorization and auditing fields.
- Extends the appointment detail experience in the frontend with a document panel (drag & drop upload, listing, download, soft/hard delete) available from cards, agenda, and calendar views.
- Documents rollout strategy covering local tests (MinIO or R2) and promotion to Coolify environments.

## Architecture Overview
1. **Presigned Upload Flow**
   - Client requests `POST /appointments/{appointmentId}/documents/presign` with filename, MIME type, and size.
   - Backend validates tenant/role, allowed MIME types, and size, persists a `pending` document metadata row, and returns a presigned PUT URL to R2.
   - Client uploads directly to R2 using the provided URL, then calls `POST /appointments/{appointmentId}/documents/{documentId}/confirm` with the final size/ETag. The record transitions to `available`.
2. **Storage Key Convention**
   - `patients/{patientId}/appointments/{appointmentId}/{yyyy}/{mm}/{uuid}_{sanitizedName}` (patientId derived client-side and sanitized server-side).
3. **Document Retrieval & Removal**
   - `GET /appointments/{appointmentId}/documents` lists non-deleted documents.
   - `GET /appointments/{appointmentId}/documents/{documentId}/download` issues a presigned GET URL (default TTL 600s).
   - `DELETE /appointments/{appointmentId}/documents/{documentId}?hard=true|false` performs soft-delete (default) or hard-delete (admin only; also deletes from R2).
4. **Security & Auditing**
   - Requires tenant/user context from headers (`X-User-Id`, `X-User-Role`, `X-Tenant-Id`).
   - Metadata captures `uploaderUserId`, `sourceIP`, timestamps, and deletion actors.
5. **Frontend**
   - A slide-over drawer allows uploads (drag & drop), shows upload status, lists documents, and exposes download/delete actions.
   - Accessible from appointment cards, agenda view, and calendar day modal.

## Environment Variables
| Variable | Description |
| --- | --- |
| `R2_ACCOUNT_ID` | Cloudflare account ID (or empty when using custom S3 endpoint). |
| `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` | Credentials for the bucket. |
| `R2_BUCKET_PATIENT_DOCS` | Bucket name dedicated to patient documents. |
| `R2_PRESIGN_TTL_SECONDS` | TTL (seconds) for presigned URLs (default 600). |
| `MAX_UPLOAD_MB` | Max upload size for patient docs (default 10 MB). |
| `ALLOWED_MIME_LIST` | Comma-separated allowed MIME types (default PDF/JPEG/PNG/WEBP/HEIC). |
| `S3_ENDPOINT` | Optional override (e.g., `http://localhost:9000` for MinIO). |
| Frontend: `VITE_API_USER_ID`, `VITE_API_USER_ROLE`, `VITE_API_TENANT_ID`, `VITE_PATIENT_DOCS_MAX_MB`, `VITE_PATIENT_DOCS_ALLOWED_MIME`. |

## Local Testing Plan
### A. Using MinIO
1. Start MinIO locally (`docker run -p 9000:9000 -p 9001:9001 ...`).
2. Create bucket `patient-docs` and apply CORS allowing `http://localhost:*`, methods `PUT,GET`, headers `*`, expose `ETag`.
3. Configure backend `.env.local`:
   - `S3_ENDPOINT=http://localhost:9000`
   - MinIO access/secret keys, `R2_BUCKET_PATIENT_DOCS=patient-docs`.
4. Configure frontend `.env.local` to point at backend (`VITE_API_URL=http://localhost:8000` etc.).
5. Flow checklist:
   - Presign -> PUT upload -> confirm -> list -> download -> delete (soft/hard) using the UI.
   - Validate: PDF/JPG ≤10 MB succeeds; MIME outside `ALLOWED_MIME_LIST` returns 400; download URL expires after ~10 minutes; soft-deleted docs disappear from list; hard delete removes object from MinIO (verify via MinIO console).

### B. Using Cloudflare R2 Directly
1. Create R2 bucket and S3 API token pair (separate keys per environment). Note default endpoint `https://<account_id>.r2.cloudflarestorage.com`.
2. Apply CORS for `http://localhost:3000` and `http://localhost:5173` during dev.
3. Configure backend `.env.local.r2` with account ID, keys, bucket name, TTL, and clear `S3_ENDPOINT`.
4. Repeat the same functional checklist as MinIO to validate end-to-end behaviour.

## Promotion to Coolify + R2
1. **Coolify App Setup**
   - Add backend service with healthcheck `/health` and set environment variables identical to `.env.staging` or `.env.prod` (include R2 credentials, bucket, TTL, allowed MIME).
   - Frontend service should include mock headers (or integrate actual auth when available) so the API receives tenant/user context.
2. **R2 Configuration**
   - Create buckets for staging and production.
   - Configure CORS to include `https://clinica-staging.widia.io` and `https://clinica.widia.io` (plus backend domains if required).
   - Issue dedicated access keys per environment (principle of least privilege).
3. **Smoke Tests After Deployment**
   - Upload a valid PDF/image via UI; confirm metadata stored and file visible in R2 console.
   - Validate list and download link expiration (~10 minutes).
   - Execute soft-delete (document disappears from UI) and hard-delete (object removed from bucket) as admin.
   - Ensure collaborator role cannot hard-delete (API returns 403) and that tenant isolation works by using different headers.

## Acceptance Checklist
- [ ] Backend endpoints respond with correct status codes and payloads for happy path and validation errors.
- [ ] Presigned upload + confirmation persists metadata and makes download available.
- [ ] Soft delete hides document without removing from storage; hard delete removes from storage and marks record.
- [ ] Frontend dropzone enforces size/type limits and surfaces errors.
- [ ] Document drawer accessible from cards, calendar modal, and agenda views.
- [ ] Audit fields (`uploaderUserId`, `sourceIP`, timestamps) populate in database.
- [ ] `.env.example` and frontend `.env.example` include new variables.
- [ ] Documentation (this file) reviewed and linked in release notes.

## Definition of Done
- Code merged with automated tests passing and manual smoke checklist completed.
- Documentation updated (architecture, env vars, rollout steps).
- Feature toggled in staging with successful smoke test before production rollout.
- Monitoring/alerts (if applicable) configured for upload errors.
- Stakeholders (ops/support) informed about new env vars and manual validation steps.
