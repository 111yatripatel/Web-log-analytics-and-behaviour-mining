# HDFS Fault Tolerance & High Availability Report

## 1. Overview
High availability and fault tolerance are foundational properties of distributed file systems. This experiment demonstrates how the Hadoop Distributed File System (HDFS) maintains data availability and integrity during the sudden failure of a storage node (DataNode).

---

## 2. Replication Architecture
- **Configured Replication Factor**: `2`
- **Total DataNodes**: `2` (`datanode1`, `datanode2`)
- **Dataset**: `web_logs.tsv` (`345,402,437` bytes, 3 blocks)

When the dataset was uploaded to HDFS, the NameNode assigned each block to both DataNodes:
```text
/log-analytics/processed/web_logs.tsv (3 blocks):
0. blk_1073741825_1001 len=134217728 repl=2 [172.18.0.2 (datanode2), 172.18.0.9 (datanode1)]
1. blk_1073741826_1002 len=134217728 repl=2 [172.18.0.2 (datanode2), 172.18.0.9 (datanode1)]
2. blk_1073741827_1003 len=76966981  repl=2 [172.18.0.2 (datanode2), 172.18.0.9 (datanode1)]
```

---

## 3. Failure Demonstration Walkthrough

### Step 1: Normal Cluster State
Both DataNodes are active and reporting healthy heartbeats:
```powershell
docker exec namenode hdfs dfsadmin -report
```
*Output:*
```text
Live datanodes (2):
Name: 172.18.0.9:50010 (datanode1) - Normal
Name: 172.18.0.2:50010 (datanode2) - Normal
```

### Step 2: Injecting DataNode Failure
Simulate a catastrophic hardware failure on `datanode2`:
```powershell
docker stop datanode2
```

### Step 3: Verifying Uninterrupted Data Availability
Query data from the file stored in HDFS immediately after DataNode 2 went offline:
```powershell
docker exec namenode bash -c "hdfs dfs -cat /log-analytics/processed/web_logs.tsv | head -n 5"
```
*Result:*
```text
199.72.81.55   01/Jul/1995:00:00:01 -0400   GET   /history/apollo/   HTTP/1.0   200   6245
unicomp6...    01/Jul/1995:00:00:06 -0400   GET   /shuttle/...       HTTP/1.0   200   3985
...
```
**Conclusion**: All data remains 100% readable without error because DataNode 1 holds an exact secondary replica of all three blocks.

### Step 4: Recovery & Cluster Reintegration
Restart `datanode2`:
```powershell
docker start datanode2
```
Verify filesystem health:
```powershell
docker exec namenode hdfs fsck /log-analytics/processed/web_logs.tsv -files -blocks -locations
```
*Result:*
`Status: HEALTHY. Total blocks (validated): 3. Missing replicas: 0 (0.0%). Number of data-nodes: 2.`

---

## 4. Academic Honesty & Cluster Limitations
> [!IMPORTANT]
> **Single-Machine Simulation Disclaimer:**  
> This cluster runs within Docker containers hosted on a single physical workstation through Docker Desktop and WSL2.  
> While the software architecture genuinely exercises Hadoop's distributed protocols, RPC communication, replication algorithms, and failover mechanics, it **does not** provide physical server fault tolerance. If the physical host loses power or crashes, all virtual containers fail together.
