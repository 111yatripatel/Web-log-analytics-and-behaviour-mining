# Pipeline Execution Runbook

This runbook outlines the exact sequence of commands required to launch, execute, verify, and demonstrate the distributed Big Data pipeline.

---

## Prerequisites
- Windows 10/11 with **WSL2** and **Docker Desktop** installed and running.
- Python 3.10+ installed on host.
- NASA access log files placed in `data/raw/`:
  - `data/raw/NASA_access_log_Jul95`
  - `data/raw/NASA_access_log_Aug95`

---

## Step 1: Start the Docker Hadoop Cluster
```powershell
docker compose -f docker/docker-compose.yml up -d
```
Verify all 12 containers are healthy and running:
```powershell
docker compose -f docker/docker-compose.yml ps
```

---

## Step 2: Verify HDFS & YARN Health
Verify 2 live DataNodes in HDFS:
```powershell
docker exec namenode hdfs dfsadmin -report
```
Verify 2 NodeManagers in YARN:
```powershell
docker exec resourcemanager yarn node -list
```
Create HDFS project directories:
```powershell
docker exec namenode hdfs dfs -mkdir -p /log-analytics/raw
docker exec namenode hdfs dfs -mkdir -p /log-analytics/processed
docker exec namenode hdfs dfs -mkdir -p /log-analytics/results
docker exec namenode hdfs dfs -ls /log-analytics
```

---

## Step 3: Parse and Preprocess Raw Logs
Stream and normalize the 3.46M raw log records into clean TSV format:
```powershell
python preprocessing/parser.py
```
Check the generated report and sample records:
```powershell
Get-Content data/processed/processing_report.txt
Get-Content data/processed/web_logs.tsv -TotalCount 5
```

---

## Step 4: Upload Dataset into HDFS
Upload the normalized TSV into HDFS:
```powershell
docker exec namenode hdfs dfs -put -f /data/processed/web_logs.tsv /log-analytics/processed/
```
Verify HDFS block distribution and 2x replication:
```powershell
docker exec namenode hdfs dfs -ls -h /log-analytics/processed
docker exec namenode hdfs fsck /log-analytics/processed/web_logs.tsv -files -blocks -locations
```

---

## Step 5: Execute Hive Distributed Analytics
Initialize the Hive database and external table over HDFS:
```powershell
docker exec hive-server hive -f /hive_scripts/schema.sql
```
Verify Hive table rows:
```powershell
docker exec hive-server hive -e "USE web_log_analytics; SELECT * FROM web_logs LIMIT 5;"
```
Run distributed Hive aggregation queries on YARN:
```powershell
docker exec hive-server hive -e "USE web_log_analytics; SELECT COUNT(*) FROM web_logs;"
```

---

## Step 6: Run MapReduce Sessionization on YARN
Run the 30-minute inactivity sessionization job:
```powershell
powershell -ExecutionPolicy Bypass -File pipeline/run_sessionization.ps1
```
*(On Linux/macOS: `./pipeline/run_sessionization.sh`)*

Verify session results in HDFS:
```powershell
docker exec namenode hdfs dfs -ls /log-analytics/results/sessions
docker exec namenode bash -c "hdfs dfs -cat /log-analytics/results/sessions/part-00000 | head -n 5"
```

---

## Step 7: Run URL Navigation Graph Mining on YARN
Execute the 2-stage transition mining pipeline:
```powershell
powershell -ExecutionPolicy Bypass -File pipeline/run_navigation.ps1
```
*(On Linux/macOS: `./pipeline/run_navigation.sh`)*

Verify mined transitions in HDFS:
```powershell
docker exec namenode hdfs dfs -ls /log-analytics/results/navigation
docker exec namenode bash -c "hdfs dfs -cat /log-analytics/results/navigation/part-00000 | head -n 5"
```

---

## Step 8: Load Results into MongoDB Serving Layer
Ingest MapReduce and Hive results into MongoDB collections:
```powershell
python mongodb/loader.py
```

---

## Step 9: Access FastAPI Backend & Web Dashboard
1. Verify API Health:
   ```powershell
   curl.exe -s http://localhost:8000/api/health
   ```
2. Verify API KPI Summary:
   ```powershell
   curl.exe -s http://localhost:8000/api/summary
   ```
3. Open the interactive Web Dashboard in any browser:
   **`http://localhost:8000/`**

---

## Step 10: Run Scalability Benchmarks & Fault Tolerance Tests
Run benchmark:
```powershell
python experiments/generate_benchmark.py
```
Run fault tolerance test:
```powershell
# Stop DataNode 2
docker stop datanode2
# Verify data remains accessible
docker exec namenode bash -c "hdfs dfs -cat /log-analytics/processed/web_logs.tsv | head -n 5"
# Restart DataNode 2
docker start datanode2
```
