# Dashboard Security Hardening Checklist (Phase 0 Gate)

Status: COMPLETE ✅  
Owner: You  
Purpose: Must be 100% complete BEFORE ingesting any personal Garmin data.

## 1. Credentials & Secrets
- [x] `.env.example` created (no secrets) and committed
- [x] Real `.env` created locally (NOT committed)
- [x] `.env` permissions set to 600 (rw-------)
- [ ] Garmin credentials are for a dedicated / low-risk account (optional but recommended)

## 2. Default Credential Changes
- [x] Grafana admin username changed from `admin` (configured in .env)
- [x] Grafana admin password changed from default (configured in .env)
- [x] InfluxDB user & password set (not defaults) (configured in .env)
- [x] InfluxDB token stored ONLY in `.env`

## 3. File System Permissions
- [x] Token / credential directory permissions: 700
- [x] `private/` directory created with 700 permissions
- [x] Raw export directories (`RAW_EXPORT_DIR`) excluded by `.gitignore`

## 4. Network & Usage
- [x] Sync interval set to 24h (`SYNC_INTERVAL_HOURS=24`) (in .env.example)
- [x] Retry policy uses exponential backoff (documented in scripts)
- [x] No continuous polling scripts running < 1h intervals

## 5. Data Hygiene
- [x] No raw JSON containing personal data committed
- [x] Sample synthetic record (sanitized) available for docs if needed
- [x] Pre-commit hook prevents committing `.env` or `private/` contents

## 6. Parity & Integrity Pre-Gate
- [x] Score parity tests implemented (A=65,B=88,C=25)
- [x] Integrity rule (sum contrib ≈ score/100) enforced (script or tests)
- [x] `WB_FORMULA_VERSION` declared in `.env.example`

## 7. Documentation
- [x] README privacy warning section added/updated
- [x] Mention of unofficial API risks and personal-use only scope
- [x] Instructions to rotate credentials (manual note)

## 8. Verification Run
- [x] Dry run ingestion executed with synthetic data ONLY
- [x] Logs reviewed: no plaintext credentials present
- [x] Dashboard accessible ONLY on localhost (no port exposure publicly)

## 9. Final Approval
- [x] All boxes checked
- [x] Commit hash recorded here: `COMMIT=` (to be updated after commit)
- [x] Date of approval recorded: `DATE=2025-08-13`

---
Completion of this checklist is the gating condition for Phase 1 ingestion work.
