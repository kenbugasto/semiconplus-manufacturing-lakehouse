
-- ============================================================
-- SemiconPlus Semiconductor Manufacturing Lakehouse
-- Unity Catalog foundation
-- ============================================================

-- The managed storage location is supplied through the target
-- environment. Never commit cloud-storage paths or credentials.

CREATE CATALOG IF NOT EXISTS semiconplus_portfolio
MANAGED LOCATION '${catalog_managed_location}'
COMMENT 'Governed catalog for the SemiconPlus semiconductor manufacturing lakehouse portfolio project';

USE CATALOG semiconplus_portfolio;

CREATE SCHEMA IF NOT EXISTS landing
COMMENT 'Landing files and ingestion resources';

CREATE SCHEMA IF NOT EXISTS bronze
COMMENT 'Raw Delta data with source and ingestion metadata';

CREATE SCHEMA IF NOT EXISTS silver
COMMENT 'Validated, standardized, and deduplicated manufacturing data';

CREATE SCHEMA IF NOT EXISTS gold
COMMENT 'Business-ready facts, dimensions, KPIs, and analytical data marts';

CREATE SCHEMA IF NOT EXISTS quarantine
COMMENT 'Invalid and unresolved records requiring investigation';

CREATE SCHEMA IF NOT EXISTS security
COMMENT 'Access mappings, security functions, and governance metadata';

CREATE SCHEMA IF NOT EXISTS secure
COMMENT 'Dynamic views with row-level filtering and column protection';

CREATE SCHEMA IF NOT EXISTS monitoring
COMMENT 'Pipeline audits, data-quality results, operational metrics, and logs';

-- Landing volumes
CREATE VOLUME IF NOT EXISTS landing.source_files
COMMENT 'Incoming batch source files for CSV, TSV, JSON, TXT, LOG, JDBC extracts, and other supported formats';

CREATE VOLUME IF NOT EXISTS landing.test_data
COMMENT 'Small deterministic datasets used for development and automated testing';

CREATE VOLUME IF NOT EXISTS landing.streaming_events
COMMENT 'Simulated tester and equipment events used by streaming pipelines';

CREATE VOLUME IF NOT EXISTS landing.binary_documents
COMMENT 'Binary manufacturing documents used for metadata and document-processing demonstrations';

-- Monitoring volumes
CREATE VOLUME IF NOT EXISTS monitoring.checkpoints
COMMENT 'Checkpoint files used by the standalone Structured Streaming comparison';

CREATE VOLUME IF NOT EXISTS monitoring.pipeline_logs
COMMENT 'Operational logs and supporting pipeline-monitoring files';

-- Quarantine volumes
CREATE VOLUME IF NOT EXISTS quarantine.rescued_files
COMMENT 'Malformed or incompatible source files retained for investigation';

CREATE VOLUME IF NOT EXISTS quarantine.rejected_files
COMMENT 'Source files rejected during file-level ingestion validation';

-- Validation
SHOW SCHEMAS IN semiconplus_portfolio;
SHOW VOLUMES IN semiconplus_portfolio.landing;
SHOW VOLUMES IN semiconplus_portfolio.monitoring;
SHOW VOLUMES IN semiconplus_portfolio.quarantine;
