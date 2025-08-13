# Dashboard Security Hardening Checklist (Phase 0 Gate)

Status: IN PROGRESS  
Owner: You  
Purpose: Must be 100% complete BEFORE ingesting any personal Garmin data.

## 1. Credentials & Secrets
- [ ] `.env.example` created (no secrets) and committed
- [ ] Real `.env` created locally (NOT committed)
- [ ] `.env` permissions set to 600 (rw-------)
- [ ] Garmin credentials are for a dedicated / low-risk account (optional but recommended)

## 2. Default Credential Changes
- [ ] Grafana admin username changed from `admin`
- [ ] Grafana admin password changed from default
- [ ] InfluxDB user & password set (not defaults)
- [ ] InfluxDB token stored ONLY in `.env`

## 3. File System Permissions
- [ ] Token / credential directory permissions: 700
- [ ] `private/` directory created with 700 permissions
- [ ] Raw export directories (`RAW_EXPORT_DIR`) excluded by `.gitignore`

## 4. Network & Usage
- [ ] Sync interval set to 24h (`SYNC_INTERVAL_HOURS=24`)
- [ ] Retry policy uses exponential backoff (documented)
- [ ] No continuous polling scripts running < 1h intervals

## 5. Data Hygiene
- [ ] No raw JSON containing personal data committed
- [ ] Sample synthetic record (sanitized) available for docs if needed
- [ ] Pre-commit hook prevents committing `.env` or `private/` contents

## 6. Parity & Integrity Pre-Gate
- [ ] Score parity tests implemented (A=65,B=88,C=25)
- [ ] Integrity rule (sum contrib ≈ score/100) enforced (script or tests)
- [ ] `WB_FORMULA_VERSION` declared in `.env.example`

## 7. Documentation
- [ ] README privacy warning section added/updated
- [ ] Mention of unofficial API risks and personal-use only scope
- [ ] Instructions to rotate credentials (manual note)

## 8. Verification Run
- [ ] Dry run ingestion executed with synthetic data ONLY
- [ ] Logs reviewed: no plaintext credentials present
- [ ] Dashboard accessible ONLY on localhost (no port exposure publicly)

## 9. Final Approval
- [ ] All boxes checked
- [ ] Commit hash recorded here: `COMMIT=`
- [ ] Date of approval recorded: `DATE=`

---
Completion of this checklist is the gating condition for Phase 1 ingestion work.
