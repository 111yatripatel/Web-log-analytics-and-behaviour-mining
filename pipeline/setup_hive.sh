#!/bin/bash
# ============================================================================
# pipeline/setup_hive.sh
# Sets up the Hive database and external table over HDFS web logs
# ============================================================================

set -e

echo "=================================================="
echo "Initializing Hive Schema and External Table"
echo "=================================================="

docker exec hive-server hive -f /hive_scripts/schema.sql

echo "Verifying Hive Database and Table..."
docker exec hive-server hive -e "USE web_log_analytics; DESCRIBE FORMATTED web_logs;"

echo "Hive setup completed successfully."
