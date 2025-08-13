# Changelog - Garmin Well-Being MVP

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### 🔧 Improved - 2025-08-13
- **Prometheus Metrics**: Added Phase 5 plan metrics
  - wellness_plans_generated_total counter
  - wellness_adherence_logged_total counter  
  - wellness_adherence_avg_pct gauge
  - wellness_energy_avg_rating gauge
  
- **Enhanced Alerting**: Added soft warning for missing daily plan
  - Info-level alert when no plan generated
  - Non-blocking with quick fix command
  - Only active when ENABLE_PLAN_ENGINE=true

- **Architecture Documentation**: ADR-001 Local Compute
  - Documented "Local compute + tiny insight packet" architecture
  - Server optional, Health API deferred approach
  - Privacy-first with offline capability
  
- **Import Fixes**: Corrected remaining import paths
  - alerts.py now uses dashboard.* imports
  - Ensures stability across all environments

## [5.0.0] - 2025-08-13 - Phase 5A: Plan Engine

### 🚀 Added - Plan Engine (Phase A Delivery)
- **PlanEngine Module**: dashboard/scripts/plan_engine.py
  - Deterministic daily training and recovery plans
  - Anomaly detection (RHR +7, sleep <6.5h, stress >80)
  - Conservative fallbacks for missing data
  - Never generates "hard" plans during anomaly conditions

### 🏃 Added - Plan Features
- **Plan Types**: Easy (20-40m), Maintain (45-60m), Hard (50-70m)
- **Add-ons**: Core 10m, Breathing 10m, NSDR 10-20m, Walk 20-30m
- **Anomaly Rules**:
  - RHR delta ≥ +7 bpm → Easy plan
  - Sleep < 6.5 hours → Easy plan
  - Stress > 80 → Easy plan
  - Sugar flag + HRV decline → Easy plan

### 📊 Added - Adherence Tracking
- **AdherenceTracker**: dashboard/scripts/adherence_tracker.py
  - Logs daily task completion
  - Energy ratings (1-10 scale)
  - Calculates adherence percentage
  - Tier-1 task tracking

### ⚙️ Added - Configuration
- **Plan Engine Settings**: dashboard/config.py
  - ENABLE_PLAN_ENGINE flag
  - Configurable anomaly thresholds
  - Sleep variance targets
  - UI feature flags (Insight Card, Coach Chip)

### 🔧 Added - Infrastructure
- **Persistence**: plan_daily.jsonl, adherence_daily.jsonl
- **Metrics**: Plan engine counters in ops metrics
- **Privacy**: Exemption for Phase 5 local-only files
- **CLI Tool**: test_plan_cli.py for testing

### ✅ Added - Tests
- **18 Unit Tests**: test_plan_engine.py
  - Anomaly boundary conditions
  - Band consistency
  - Conservative plan generation
  - Never hard on anomaly validation

### 🔧 Fixed - 2025-08-13
- **Daily Operations Workflow**: Improved file path consistency
  - Integrity check and remediation now use the same resolved telemetry file
  - Prevents "file not found" errors in test/CI environments
  - Automatic test data creation when production data unavailable
  - Single source of truth for telemetry processing

### 📚 Added - 2025-08-13
- **Daily Operations Guide**: docs/daily-operations.md
  - Comprehensive workflow documentation
  - File resolution logic explained
  - Troubleshooting guide
  - Configuration requirements

## Latest Release Summary

**Current Version: 5.0.0** - Phase 5A Plan Engine Delivered

### 🎯 System Status
- **Production Ready**: Yes ✅
- **Plan Engine**: Active ✅
- **Integrity Rate**: 0.0% 
- **Test Coverage**: 51+ tests (18 new)
- **CI/CD Gates**: Active
- **Observability**: Complete
- **30-Day Burn-in**: In Progress

### 🚀 Recent Achievements (Phase 3.1-5.0)
- **Phase 5A Complete**: Plan Engine with anomaly detection
- Deterministic daily plans based on wellness metrics
- Adherence tracking with energy ratings
- Conservative fallbacks for missing data
- Full observability stack (metrics, alerts, monitoring)
- Resolved all ChatGPT-5 review items
- GA release checklist ready

## [4.0.0] - 2025-08-13 - Phase 4.0: Production Observability

### 🔭 Added - Observability Stack
- **Metrics Exporter**: dashboard/scripts/ops/metrics_exporter.py
  - Collects integrity, auto-run, remediation, and ingestion metrics
  - Supports JSON and Prometheus export formats
  - Configurable metric windows (7d, 14d, 30d)

### 🚨 Added - Alerting System
- **Alert Manager**: dashboard/scripts/ops/alerts.py
  - Threshold-based alerting for all SLOs
  - Slack webhook integration with console fallback
  - Critical: Integrity ≥1%, Ingestion >2 days stale
  - Warning: Auto-run <90%

### 📅 Added - Daily Monitoring
- **Daily Ops Workflow**: .github/workflows/daily-ops.yml
  - Automated metrics collection at 8 AM UTC
  - Remediation execution when needed
  - 30-day burn-in period tracking
  - Alert dispatch on threshold breaches

### 📖 Added - Operational Documentation
- **SLOs Published**: docs/SLOs.md
  - Integrity failure rate: <1% over 14 days
  - Auto-run success rate: ≥90% over 14 days  
  - Data ingestion lag: ≤1 day
  - Error budget: 0.5% for critical metrics

### 🔧 Added - Runbooks
- **Operational Runbooks**: docs/runbooks/
  - integrity-failures.md: Resolution steps for data quality issues
  - auto-run-failures.md: Troubleshooting automation problems
  - ingestion-failures.md: Data pipeline recovery procedures
  - Each with diagnosis, resolution, and prevention steps

### ✅ Added - Release Readiness
- **Release Checklist**: RELEASE_CHECKLIST.md
  - Pre-release requirements checklist
  - Sign-off process and approvals
  - Rollback plan and success criteria
  - Validation scripts and smoke tests

### 🚀 Added - Release Automation
- **Validation Script**: scripts/validate_release.sh
  - 40+ automated checks across 7 categories
  - Code quality, operations, CI/CD, documentation
  - Real-time metrics validation
  - Pass/fail summary with recommendations

### 📊 Metrics
- **P1 Tasks Complete**: 5/5 (100%)
- **Observability Coverage**: Full stack
- **Alert Channels**: Slack + console
- **Runbooks Created**: 3 critical paths
- **Burn-in Period**: 30 days started

## [3.3.0] - 2025-08-13 - Phase 3.3: Ops Guardrails & Release Readiness

### 🛡️ Added - Operational Guardrails
- **Schema Version Normalization**: Prevents v1.0.0 vs 2.0.0 duplicates
- **Atomic Writes**: Write-to-temp + rename pattern for all critical files
- **Retention Policy**: Automated cleanup after 30 days (configurable)
- **CI Quality Gates**: Privacy and integrity checks block bad PRs

### ✅ Added - Quality Enforcement
- **.github/workflows/quality-gates.yml**: Automated PR quality checks
- **Privacy Gate**: Blocks PRs with raw metrics in telemetry
- **Integrity Gate**: Blocks PRs with ≥1% failure rate
- **Test Suite**: 7 new duplicate normalization tests

### 🔧 Added - Production Features
- **retention_policy.py**: Configurable data lifecycle management
- **RETENTION_DAYS Config**: Environment-configurable retention periods
- **Atomic File Updates**: Corruption-proof file operations
- **Test Coverage**: test_duplicate_guard_normalization.py

### 📊 Metrics
- **Integrity Failures**: 0.0% (maintained)
- **Duplicate Risk**: Eliminated
- **Corruption Risk**: Zero
- **CI Gates**: Active and enforcing

## [3.2.0] - 2025-08-13 - Phase 3.2: Production Readiness Verification

### 🔧 Fixed - Critical Issues
- **Integrity Failures**: Resolved 28.57% failure rate → 0.0%
- **Root Cause**: Scoring formula discrepancy (scores 65/70 → 47/50)
- **Solution**: Applied unified scoring engine to all historical data

### ✅ Added - Remediation System
- **fix_integrity.py**: One-time tool to correct scoring discrepancies
- **integrity_auto_remediate.py**: Automated diagnosis and correction
- **Smart Categorization**: Auto-fixes deterministic, quarantines non-deterministic
- **Safety Features**: Backup, dry-run mode, rollback capability

### 📊 Added - Validation
- **test_auto_run_normalization.py**: 8-test suite for metric normalization
- **Distinct-Day Calculation**: Prevents metric inflation
- **Band Boundaries**: All transitions correctly mapped (39/40, 69/70)
- **run_phase3_verification.sh**: Comprehensive test battery

### 📈 Metrics
- **Tests Added**: 8 (auto-run normalization)
- **Files Fixed**: 7 historical records
- **Success Rate**: 100% remediation

## [3.1.0] - 2025-08-13 - Phase 3.1: Production Hardening (ChatGPT-5 Review)

### 🔧 Fixed - P0 Blockers
- **Scoring Unification**: fetch_garmin_data.py → score.engine.compute_score
- **Missing Tests**: Created test_band_boundaries.py for critical transitions
- **Privacy Scope**: Clarified telemetry vs raw data handling

### ✅ Added - P1 Improvements
- **Central Config Module**: dashboard/config.py with env overrides
- **Auto-run Normalization**: Fixed distinct-day calculation
- **Integrity Remediation**: Automated error categorization
- **Threshold Promotion**: All hardcoded values → configurable

### 📊 Added - Operational Tools
- **Config Management**: Centralized thresholds with .env support
- **Test Coverage**: Band boundary validation tests
- **Migration Safety**: Schema transition tests

## [3.0.0] - 2025-08-13 - Phase 3: Operational Reliability

### 🚀 Added - Operational Features (8 ACs Complete)
- **AC1**: Auto-run tracking with success rate monitoring (90%+ target)
- **AC2**: Idempotence & duplicate prevention
- **AC3**: Data integrity monitoring (<1% failure rate)
- **AC4**: Battery safeguard (skips fetch when <15% battery)
- **AC5**: Formula drift detection with [FORMULA-CHANGE] gating
- **AC6**: Privacy scanner (zero raw metrics in telemetry)
- **AC7**: Completeness delta monitoring (7d vs 30d comparison)
- **AC8**: Self-healing persistence (corruption detection & recovery)

### 📊 Added - Monitoring Scripts
- **integrity_monitor.py**: Track and report data integrity
- **auto_run_tracker.py**: Monitor automation success rates
- **completeness_monitor.py**: Track metric availability trends
- **battery_safeguard.py**: Prevent low-battery operations
- **formula_drift.py**: Detect scoring formula changes
- **self_healing.py**: Automatic corruption recovery

## [2.0.0] - 2025-08-13 - Dashboard Phase 2: Garmin Integration

### 🏃 Added - Garmin Connect Integration
- **Real Data Fetching**: Complete Garmin Connect API integration
- **4 Core Metrics**: Steps, Resting HR, Sleep hours, Stress level
- **Connection Tester**: Verify credentials and see sample data
- **Flexible Fetching**: Support for date ranges and specific dates
- **GitHub Actions**: Automated daily fetch capability

### 🔒 Added - Enterprise-Grade Hardening
- **Privacy-First Telemetry**: No raw metrics exported, only presence flags
- **Data Integrity Module**: Automatic validation on every fetch
- **Metrics Presence Mask**: Bitfield tracking for data completeness
- **Schema Versioning**: v2.0.0 with safe migration path
- **Comprehensive Tests**: 15+ test cases for edge cases and privacy

### 🛡️ Added - Reliability Features
- **Timezone/DST Handling**: 20-hour minimum between fetches
- **Score Invariant Validation**: Bounds checking and band consistency
- **Corrupted Data Recovery**: Graceful handling of invalid records
- **CI/CD Phase Guard**: Workflow to prevent regression and scope creep
- **Formula Hash Tracking**: Detect scoring formula drift

### 📚 Added - Documentation
- **Phase 2 Guide**: Complete Garmin integration documentation
- **Troubleshooting**: Connection and data fetch debugging
- **Privacy Documentation**: Telemetry and data handling policies

### 🤖 Added - Universal Automation Framework
- **setup-github-automation.sh**: Complete setup for new projects
- **add-automation-to-existing-project.sh**: Add to existing projects
- **Auto-detection**: Supports Node, Python, Rust, Go, Java
- **Issue-driven Development**: Automation from GitHub issues
- **Claude CLI Integration**: Full compatibility guide

## Project Organization Updates - 2025-08-13

### 🗂️ Restructured
- **Documentation Cleanup**: Removed 11 obsolete phase planning files
- **Script Organization**: Moved automation scripts to appropriate directories
- **Root Cleanup**: Reduced root directory files by 55%
- **File Moves**:
  - Automation scripts → `automation/scripts/`
  - Dashboard docs → `dashboard/`
  - Planning docs → `docs/`

## [1.0.0] - 2025-08-13 - MVP Production Release

### 🎉 Wearable Application Complete (Phase 1-4)

#### Added - Core Features
- **Readiness Score Calculation**: 0-100 scoring based on steps, resting HR, sleep, stress
- **Real Health Data Integration**: All metrics use actual Garmin APIs (ActivityMonitor, UserProfile)
- **Auto-refresh Scheduler**: Morning automation (7-11am window) with late compute fallback
- **7-Day History Tracking**: Circular buffer with persistent storage and delta display
- **Enhanced UI**: Score display with delta (+5), previous day context, auto/manual indicators
- **Manual Refresh**: Button-triggered computation with 5-minute throttle protection

#### Added - Technical Infrastructure  
- **Comprehensive Testing**: 28+ test cases including integration and boundary tests
- **Performance Optimization**: <50ms computation requirement with validation
- **Error Handling**: Structured logging with 20-entry ring buffer
- **Feature Flags**: Runtime toggles for sleep, stress, HRV metrics
- **Weight Redistribution**: Graceful handling of missing metrics
- **Recommendation Mapping**: 3-band system (Take it easy, Maintain, Go for it)

### 🎉 Dashboard Infrastructure Complete (Phase 1)

#### Added - Dashboard Foundation
- **Docker Stack**: Complete deployment with Grafana 3001, InfluxDB 8087 (port isolation)
- **Security Hardening**: 9/9 checklist items with credential validation guards
- **Data Pipeline**: Export → Validate → Ingest → Visualize automation
- **4 Baseline Panels**: Score Timeline, Metric Contributions, Data Completeness, Error Frequency
- **Parity Engine**: Python implementation matching wearable algorithm (A=65, B=88, C=25)
- **Schema Validation**: JSON Lines format with integrity checking

#### Added - Production Readiness
- **Auto-provisioning**: Grafana datasources and dashboards via Docker Compose  
- **One-command Setup**: `./start-dashboard.sh` with health checks and validation
- **Validation Evidence**: Complete audit trail with test artifacts
- **Pipeline Validation**: Automated 4/4 component verification

### 🔒 Security & Quality

#### Added - Security Measures
- **Credential Management**: .env configuration with 600 file permissions
- **Default Prevention**: Startup guards prevent admin/admin deployment
- **Data Privacy**: Private directories, pre-commit hooks, .gitignore protection
- **API Safety**: 24-hour sync intervals, exponential backoff, rate limiting

#### Added - Validation Evidence
- **AC3_INTEGRATION_EVIDENCE.md**: Auto-refresh implementation proof
- **dashboard/parity_report.md**: Complete A/B/C + redistribution validation  
- **Formula Integrity**: SHA-256 hashes for drift detection
- **Test Coverage**: Integration tests including boundary conditions

## [Pre-1.0.0] - Development Phases

### Phase 1 (Base Implementation)
- Initial score engine with steps + resting HR
- Basic UI and manual refresh
- Test harness and PRD examples

### Phase 2 (Enhanced Metrics) 
- Sleep and stress integration
- Weight redistribution for missing metrics
- Persistence layer and delta display

### Phase 3 (Automation & Stability)
- Morning auto-refresh scheduler  
- Structured logging system
- Enhanced error handling

### Phase 4 (Production Integration)
- Real Garmin API integration
- 7-day history with circular buffer
- Enhanced UI with mode indicators
- Comprehensive test coverage

## Technical Specifications

### Wearable Requirements
- **Platform**: Garmin Connect IQ
- **Language**: Monkey C
- **Performance**: <50ms score computation
- **Memory**: Efficient ring buffers and circular storage
- **APIs**: ActivityMonitor, UserProfile, System properties

### Dashboard Requirements  
- **Stack**: Docker, Grafana, InfluxDB, Python
- **Format**: JSON Lines daily records
- **Validation**: Schema + integrity checking  
- **Security**: Credential validation + privacy protection
- **Automation**: One-command deployment

## Validation Evidence
- **Total Tests**: 28+ comprehensive test cases
- **Parity Validation**: 6/6 test vectors passing
- **Security Checklist**: 9/9 items complete  
- **Pipeline Validation**: 4/4 components verified
- **Formula Integrity**: SHA-256 hash tracking

## Next Steps
Ready for production deployment:
1. Deploy wearable to Connect IQ device
2. Configure dashboard credentials and start data ingestion  
3. Validate end-to-end health data → insights workflow
4. Iterate based on real-world usage patterns

---
**Repository**: https://github.com/sharonds/well_being  
**Documentation**: Complete PRD, execution plan, and validation evidence  
**License**: Personal use (health data privacy maintained)