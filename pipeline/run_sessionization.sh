#!/bin/bash
# ============================================================================
# pipeline/run_sessionization.sh
# Executes MapReduce Web Log Sessionization on Hadoop / YARN
# ============================================================================

set -e

STREAMING_JAR="/opt/hadoop-2.7.4/share/hadoop/tools/lib/hadoop-streaming-2.7.4.jar"
INPUT_PATH="/log-analytics/processed/web_logs.tsv"
OUTPUT_PATH="/log-analytics/results/sessions"

echo "=========================================================="
echo "Starting MapReduce Sessionization Job on YARN"
echo "=========================================================="

echo "Checking and cleaning previous output at: $OUTPUT_PATH"
docker exec namenode hdfs dfs -rm -r -f "$OUTPUT_PATH"

echo "Verifying input dataset exists at: $INPUT_PATH"
docker exec namenode hdfs dfs -test -e "$INPUT_PATH" || {
    echo "ERROR: Input dataset $INPUT_PATH does not exist in HDFS!"
    exit 1
}

echo "Submitting MapReduce Job to YARN with 2 reducers..."
docker exec namenode hadoop jar "$STREAMING_JAR" \
    -D mapreduce.job.name="WebLogSessionization" \
    -D mapreduce.job.reduces=2 \
    -input "$INPUT_PATH" \
    -output "$OUTPUT_PATH" \
    -mapper "python3 session_mapper.py" \
    -reducer "python3 session_reducer.py" \
    -file /mapreduce/session_mapper.py \
    -file /mapreduce/session_reducer.py \
    -cmdenv PYTHONIOENCODING=utf-8

echo "=========================================================="
echo "Sessionization MapReduce Completed Successfully!"
echo "Output Location: $OUTPUT_PATH"
echo "=========================================================="

docker exec namenode hdfs dfs -ls "$OUTPUT_PATH"
