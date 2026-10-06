# ============================================================================
# pipeline/run_sessionization.ps1
# Windows PowerShell runner for MapReduce Sessionization on YARN
# ============================================================================

$STREAMING_JAR = "/opt/hadoop-2.7.4/share/hadoop/tools/lib/hadoop-streaming-2.7.4.jar"
$INPUT_PATH = "/log-analytics/processed/web_logs.tsv"
$OUTPUT_PATH = "/log-analytics/results/sessions"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Starting MapReduce Sessionization Job on YARN" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Clean up old output
Write-Host "Cleaning previous output at $OUTPUT_PATH..."
docker exec namenode hdfs dfs -rm -r -f $OUTPUT_PATH

# 2. Run MapReduce via Hadoop Streaming
Write-Host "Submitting Sessionization job to YARN..." -ForegroundColor Yellow
docker exec namenode hadoop jar $STREAMING_JAR `
    -D mapreduce.job.name="WebLogSessionization" `
    -D mapreduce.job.reduces=2 `
    -input $INPUT_PATH `
    -output $OUTPUT_PATH `
    -mapper "python3 session_mapper.py" `
    -reducer "python3 session_reducer.py" `
    -file /mapreduce/session_mapper.py `
    -file /mapreduce/session_reducer.py `
    -cmdenv PYTHONIOENCODING=utf-8

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Sessionization Completed! Checking Results in HDFS:" -ForegroundColor Green
docker exec namenode hdfs dfs -ls $OUTPUT_PATH
