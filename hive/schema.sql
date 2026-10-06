-- ============================================================================
-- Hive Schema Definition for Distributed Web Log Analytics
-- ============================================================================

CREATE DATABASE IF NOT EXISTS web_log_analytics;
USE web_log_analytics;

-- External table mapped directly to the TSV file stored in HDFS
DROP TABLE IF EXISTS web_logs;
CREATE EXTERNAL TABLE IF NOT EXISTS web_logs (
    host STRING,
    log_time STRING,
    method STRING,
    url STRING,
    protocol STRING,
    status INT,
    response_bytes BIGINT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/log-analytics/processed';
