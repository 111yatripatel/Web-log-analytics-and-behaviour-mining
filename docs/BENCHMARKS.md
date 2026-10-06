# Big Data Systems Scalability & Benchmark Report

## 1. Executive Summary
This report documents empirical execution benchmarks conducted on the **Hadoop MapReduce on YARN** distributed computing environment using real-world NASA HTTP access log data.

All metrics recorded in this document represent **actual observed execution times** and cluster counters produced during job execution on YARN.

---

## 2. Experimental Setup
- **Host Hardware**: Windows 11 Host, WSL2, Docker Desktop 29.8.2.
- **Cluster Architecture**:
  - 1 NameNode (`bds-hadoop-namenode:2.7.4`)
  - 2 DataNodes (`bde2020/hadoop-datanode:2.0.0-hadoop2.7.4-java8`)
  - 1 ResourceManager (`bde2020/hadoop-resourcemanager:2.0.0-hadoop2.7.4-java8`)
  - 2 NodeManagers (`bds-hadoop-nodemanager:2.7.4`)
- **Execution Engine**: Hadoop Streaming 2.7.4 via YARN.
- **Storage Subsystem**: HDFS Replication Factor = 2, Block size = 128 MB.

---

## 3. Observed Scalability Measurements

| Workload Scale | Records Processed | Raw TSV Size | HDFS Blocks | Mappers | Reducers | Wall-Clock Time | CPU Time Spent | Peak Memory Usage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1x (Full NASA Logs)** | 3,461,612 | 329.40 MB | 3 | 3 | 2 | **34.20s** | 57.69s | 1.18 GB |
| **Navigation Stage 1** | 3,461,612 | 329.40 MB | 3 | 3 | 2 | **33.80s** | 65.51s | 1.17 GB |
| **Navigation Stage 2** | 3,084,742 | 203.03 MB | 2 | 2 | 2 | **29.10s** | 34.23s | 0.90 GB |
| **Hive Count(*) MR** | 3,461,612 | 329.40 MB | 3 | 2 | 1 | **30.45s** | 16.93s | 1.05 GB |

---

## 4. Analysis of Scaling Behavior

1. **HDFS Split Parallelism**:
   - The 329.40 MB input file was split into three 128 MB blocks in HDFS.
   - Hadoop automatically spawned 3 concurrent Map tasks matching the exact number of block splits (`Launched map tasks=3`).
2. **Shuffle and Sort Efficiency**:
   - In Sessionization, `3,461,612` map output records were shuffled and partitioned across 2 reducers, grouping by `137,978` distinct host keys (`Reduce input groups=137978`).
   - The Shuffle stage achieved 100% throughput with 0 failed shuffles.
3. **CPU Parallelism**:
   - The cumulative CPU time recorded across all tasks was `57.69 seconds`, while actual wall-clock elapsed time was `34.20 seconds`.
   - The wall-clock time was significantly lower than cumulative CPU time, demonstrating that YARN effectively utilized parallel multi-core execution across NodeManagers.
