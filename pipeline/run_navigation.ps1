# ============================================================================
# pipeline/run_navigation.ps1
# Windows PowerShell runner for URL Navigation & Transition Mining on YARN
# ============================================================================

$STREAMING_JAR = "/opt/hadoop-2.7.4/share/hadoop/tools/lib/hadoop-streaming-2.7.4.jar"
$INPUT_PATH = "/log-analytics/processed/web_logs.tsv"
$TEMP_OUTPUT = "/log-analytics/results/transitions_raw"
$FINAL_OUTPUT = "/log-analytics/results/navigation"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Starting URL Navigation Mining Pipeline on YARN" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Clean previous outputs for safe re-runnability
Write-Host "Cleaning previous outputs..."
docker exec namenode hdfs dfs -rm -r -f $TEMP_OUTPUT
docker exec namenode hdfs dfs -rm -r -f $FINAL_OUTPUT

# 2. Stage 1: Extract URL transitions per host/session
Write-Host "Stage 1: Extracting URL transitions per host session..." -ForegroundColor Yellow
docker exec namenode hadoop jar $STREAMING_JAR `
    -D mapreduce.job.name="NavigationExtraction_Stage1" `
    -D mapreduce.job.reduces=2 `
    -input $INPUT_PATH `
    -output $TEMP_OUTPUT `
    -mapper "python3 navigation_mapper.py" `
    -reducer "python3 navigation_reducer.py" `
    -file /mapreduce/navigation_mapper.py `
    -file /mapreduce/navigation_reducer.py `
    -cmdenv PYTHONIOENCODING=utf-8

# 3. Stage 2: Aggregate transition frequencies across cluster
Write-Host "Stage 2: Aggregating global URL transition frequencies..." -ForegroundColor Yellow
docker exec namenode hadoop jar $STREAMING_JAR `
    -D mapreduce.job.name="NavigationAggregation_Stage2" `
    -D mapreduce.job.reduces=2 `
    -input "$TEMP_OUTPUT/part-*" `
    -output $FINAL_OUTPUT `
    -mapper "python3 transition_mapper.py" `
    -reducer "python3 navigation_aggregate_reducer.py" `
    -file /mapreduce/transition_mapper.py `
    -file /mapreduce/navigation_aggregate_reducer.py `
    -cmdenv PYTHONIOENCODING=utf-8

# 4. Clean temporary intermediate data
docker exec namenode hdfs dfs -rm -r -f $TEMP_OUTPUT

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Navigation Mining Completed! Checking Results in HDFS:" -ForegroundColor Green
docker exec namenode hdfs dfs -ls $FINAL_OUTPUT
