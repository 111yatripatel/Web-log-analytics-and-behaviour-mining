"""Precomputed, static view data for cluster/benchmark/demo endpoints.

These values describe the (fixed) local Hadoop/Hive cluster and the results
measured during the project run. Keeping them here keeps `main.py` focused on
request handling and MongoDB access.
"""

CLUSTER_TOPOLOGY = {
    "cluster_name": "log-analytics-cluster",
    "hadoop_version": "2.7.4",
    "hive_version": "2.3.2",
    "mongodb_version": "Atlas (6.0+)",
    "nodes": [
        {"name": "namenode", "role": "HDFS Master", "port": 50070, "rpc": 8020, "status": "RUNNING", "desc": "Namespace metadata & block allocation"},
        {"name": "datanode1", "role": "HDFS Worker 1", "port": 50075, "rpc": 50010, "status": "RUNNING", "desc": "128MB block storage (replica 1)"},
        {"name": "datanode2", "role": "HDFS Worker 2", "port": 50076, "rpc": 50010, "status": "RUNNING", "desc": "128MB block storage (replica 2)"},
        {"name": "resourcemanager", "role": "YARN Master", "port": 8088, "rpc": 8032, "status": "RUNNING", "desc": "Cluster scheduler & resource arbiter"},
        {"name": "nodemanager1", "role": "YARN Worker 1", "port": 8042, "rpc": 40027, "status": "RUNNING", "desc": "Container executor (2 vCores, 4GB RAM)"},
        {"name": "nodemanager2", "role": "YARN Worker 2", "port": 8043, "rpc": 44707, "status": "RUNNING", "desc": "Container executor (2 vCores, 4GB RAM)"},
        {"name": "historyserver", "role": "MapReduce History", "port": 19888, "rpc": 10020, "status": "RUNNING", "desc": "Job execution timeline metrics"},
        {"name": "hive-server", "role": "HiveServer2", "port": 10000, "rpc": 10002, "status": "RUNNING", "desc": "Distributed SQL query engine"},
        {"name": "hive-metastore", "role": "Hive Metastore", "port": 9083, "rpc": 9083, "status": "RUNNING", "desc": "Schema-on-read catalog service"},
        {"name": "postgres", "role": "Metastore RDBMS", "port": 5432, "rpc": 5432, "status": "RUNNING", "desc": "Relational schema metadata store"},
        {"name": "mongodb-atlas", "role": "Serving Layer", "port": 27017, "rpc": 27017, "status": "RUNNING", "desc": "Managed cloud document store (MongoDB Atlas)"},
        {"name": "backend", "role": "FastAPI Service", "port": 8000, "rpc": 8000, "status": "RUNNING", "desc": "REST API & Dashboard Server"},
    ],
    "storage": {
        "replication_factor": 2,
        "block_size_mb": 128,
        "total_blocks": 3,
        "fsck_health": "HEALTHY",
        "missing_replicas": 0,
    },
}

STATUS_CODES = [
    {"status": "200 OK", "count": 3130486, "percentage": 90.43, "color": "#10b981", "desc": "Successful HTTP resource transmissions"},
    {"status": "304 Not Modified", "count": 308014, "percentage": 8.90, "color": "#38bdf8", "desc": "Cached browser responses (bandwidth saved)"},
    {"status": "404 Not Found", "count": 20891, "percentage": 0.60, "color": "#f43f5e", "desc": "Missing or obsolete URLs & broken hyperlinks"},
    {"status": "302 Found / Redirect", "count": 2143, "percentage": 0.06, "color": "#a855f7", "desc": "Permanent/temporary resource relocations"},
    {"status": "500 / 501 Server Error", "count": 78, "percentage": 0.002, "color": "#e11d48", "desc": "CGI execution crashes or unsupported methods"},
]

SESSION_DISTRIBUTION = [
    {"bucket": "< 1 min (Single Hit)", "sessions": 126287, "percentage": 41.2, "avg_hits": 2.1, "color": "#6366f1"},
    {"bucket": "1 - 5 mins (Short)", "sessions": 76017, "percentage": 24.8, "avg_hits": 7.4, "color": "#38bdf8"},
    {"bucket": "5 - 15 mins (Standard)", "sessions": 55480, "percentage": 18.1, "avg_hits": 18.9, "color": "#10b981"},
    {"bucket": "15 - 30 mins (Active)", "sessions": 31572, "percentage": 10.3, "avg_hits": 34.6, "color": "#f59e0b"},
    {"bucket": "> 30 mins (Power User)", "sessions": 17167, "percentage": 5.6, "avg_hits": 72.3, "color": "#ec4899"},
]

BENCHMARKS = [
    {"workload": "Sessionization MapReduce (Full NASA Logs)", "records": 3461612, "input_size_mb": 329.40, "hdfs_blocks": 3, "mappers": 3, "reducers": 2, "wall_clock_sec": 34.20, "cpu_time_sec": 57.69, "peak_ram_gb": 1.18, "speedup_ratio": "1.69x CPU Parallelism", "containers": "nodemanager1, nodemanager2"},
    {"workload": "Navigation Mining Stage 1 (Intra-Session Pairs)", "records": 3461612, "input_size_mb": 329.40, "hdfs_blocks": 3, "mappers": 3, "reducers": 2, "wall_clock_sec": 33.80, "cpu_time_sec": 65.51, "peak_ram_gb": 1.17, "speedup_ratio": "1.94x CPU Parallelism", "containers": "nodemanager1, nodemanager2"},
    {"workload": "Navigation Mining Stage 2 (Global Aggregation)", "records": 3084742, "input_size_mb": 203.03, "hdfs_blocks": 2, "mappers": 2, "reducers": 2, "wall_clock_sec": 29.10, "cpu_time_sec": 34.23, "peak_ram_gb": 0.90, "speedup_ratio": "1.18x CPU Parallelism", "containers": "nodemanager1, nodemanager2"},
    {"workload": "Hive SQL COUNT(*) Analytics", "records": 3461612, "input_size_mb": 329.40, "hdfs_blocks": 3, "mappers": 2, "reducers": 1, "wall_clock_sec": 30.45, "cpu_time_sec": 16.93, "peak_ram_gb": 1.05, "speedup_ratio": "MapReduce Compiler", "containers": "hive-server, nodemanager1"},
]

HDFS_BLOCKS = {
    "blk_1073741825_1001": {
        "block_id": "blk_1073741825_1001", "size_bytes": 134217728, "size_mb": 128.0,
        "offset_start": 0, "offset_end": 134217728, "records_count": 1409210,
        "primary_node": "datanode1 (172.18.0.9:50075)", "secondary_node": "datanode2 (172.18.0.2:50076)",
        "replication": 2, "crc32_checksum": "0x8F9A321B", "health": "HEALTHY",
        "hdfs_path": "/log-analytics/processed/web_logs.tsv",
        "sample_records": [
            "199.72.81.55\t1995-07-01 00:00:01\tGET\t/history/apollo/\tHTTP/1.0\t200\t6245",
            "unicomp6.unicomp.net\t1995-07-01 00:00:06\tGET\t/images/NASA-logosmall.gif\tHTTP/1.0\t304\t0",
            "199.120.110.21\t1995-07-01 00:00:09\tGET\t/shuttle/missions/sts-71/movies/\tHTTP/1.0\t200\t4039",
            "burger.letters.com\t1995-07-01 00:00:11\tGET\t/shuttle/countdown/liftoff.html\tHTTP/1.0\t304\t0",
            "199.120.110.21\t1995-07-01 00:00:11\tGET\t/shuttle/missions/sts-71/movies/sts-71-launch.mpg\tHTTP/1.0\t200\t786432",
        ],
    },
    "blk_1073741826_1002": {
        "block_id": "blk_1073741826_1002", "size_bytes": 134217728, "size_mb": 128.0,
        "offset_start": 134217729, "offset_end": 268435456, "records_count": 1408840,
        "primary_node": "datanode1 (172.18.0.9:50075)", "secondary_node": "datanode2 (172.18.0.2:50076)",
        "replication": 2, "crc32_checksum": "0x4C12D8E9", "health": "HEALTHY",
        "hdfs_path": "/log-analytics/processed/web_logs.tsv",
        "sample_records": [
            "ix-or6-14.ix.netcom.com\t1995-07-18 14:22:01\tGET\t/images/KSC-logosmall.gif\tHTTP/1.0\t200\t1204",
            "ppp13.dialin.ucla.edu\t1995-07-18 14:22:04\tGET\t/shuttle/missions/sts-70/sts-70-patch-small.gif\tHTTP/1.0\t200\t3120",
            "port03.csl.co.uk\t1995-07-18 14:22:07\tGET\t/ksc.html\tHTTP/1.0\t200\t7060",
            "gateway.cisco.com\t1995-07-18 14:22:09\tGET\t/images/USA-logosmall.gif\tHTTP/1.0\t304\t0",
        ],
    },
    "blk_1073741827_1003": {
        "block_id": "blk_1073741827_1003", "size_bytes": 76968178, "size_mb": 73.40,
        "offset_start": 268435457, "offset_end": 345403634, "records_count": 643562,
        "primary_node": "datanode1 (172.18.0.9:50075)", "secondary_node": "datanode2 (172.18.0.2:50076)",
        "replication": 2, "crc32_checksum": "0xE3B892F1", "health": "HEALTHY",
        "hdfs_path": "/log-analytics/processed/web_logs.tsv",
        "sample_records": [
            "204.120.229.4\t1995-08-31 23:59:44\tGET\t/ksc.html\tHTTP/1.0\t200\t7060",
            "crl5.crl.com\t1995-08-31 23:59:52\tGET\t/history/apollo/\tHTTP/1.0\t200\t6245",
            "crl5.crl.com\t1995-08-31 23:59:54\tGET\t/images/ksclogo-medium.gif\tHTTP/1.0\t200\t5866",
        ],
    },
}

HIVE_QUERIES = {
    "q1": {
        "name": "Top 10 Requested URLs Aggregation",
        "sql": "SELECT url, COUNT(*) AS request_count, ROUND(COUNT(*) * 100.0 / 3461612, 2) AS percentage\nFROM web_logs\nGROUP BY url\nORDER BY request_count DESC\nLIMIT 10;",
        "mr_plan": "Map: 3 Tasks (1 per 128MB HDFS block) -> Shuffle & Sort by hash(url) -> Reduce: 1 Task (Global Count & Sort)",
        "mappers_launched": 3, "reducers_launched": 1, "bytes_scanned_mb": 329.40,
        "wall_clock_time_sec": 30.45, "cpu_time_sec": 48.20,
        "results": [
            {"rank": 1, "url": "/images/NASA-logosmall.gif", "count": 208723, "percentage": "6.03%"},
            {"rank": 2, "url": "/images/KSC-logosmall.gif", "count": 164976, "percentage": "4.77%"},
            {"rank": 3, "url": "/images/MOSAIC-logosmall.gif", "count": 127916, "percentage": "3.70%"},
            {"rank": 4, "url": "/images/USA-logosmall.gif", "count": 127082, "percentage": "3.67%"},
            {"rank": 5, "url": "/images/WORLD-logosmall.gif", "count": 125933, "percentage": "3.64%"},
        ],
    },
    "q2": {
        "name": "HTTP Status Code Distribution",
        "sql": "SELECT status, COUNT(*) AS total, ROUND(COUNT(*) * 100.0 / 3461612, 3) AS pct\nFROM web_logs\nGROUP BY status\nORDER BY total DESC;",
        "mr_plan": "Map: 3 Tasks -> Combiner (Local status count) -> Shuffle -> Reduce: 1 Task (Final sum)",
        "mappers_launched": 3, "reducers_launched": 1, "bytes_scanned_mb": 329.40,
        "wall_clock_time_sec": 26.80, "cpu_time_sec": 39.10,
        "results": [
            {"rank": 1, "status": 200, "total": 3130486, "pct": "90.434%"},
            {"rank": 2, "status": 304, "total": 308014, "pct": "8.898%"},
            {"rank": 3, "status": 404, "total": 20891, "pct": "0.603%"},
            {"rank": 4, "status": 302, "total": 2143, "pct": "0.062%"},
            {"rank": 5, "status": 500, "total": 78, "pct": "0.002%"},
        ],
    },
    "q3": {
        "name": "Diurnal Hourly Request Pattern",
        "sql": "SELECT substr(log_time, 12, 2) AS hour_of_day, COUNT(*) AS total_hits\nFROM web_logs\nGROUP BY substr(log_time, 12, 2)\nORDER BY hour_of_day ASC;",
        "mr_plan": "Map: 3 Tasks -> Hash partition by hour (00-23) -> Reduce: 1 Task (Hourly ordering)",
        "mappers_launched": 3, "reducers_launched": 1, "bytes_scanned_mb": 329.40,
        "wall_clock_time_sec": 28.50, "cpu_time_sec": 42.60,
        "results": [
            {"rank": 1, "hour": "14:00 (Peak)", "total_hits": 235100, "share": "6.79%"},
            {"rank": 2, "hour": "15:00", "total_hits": 231400, "share": "6.68%"},
            {"rank": 3, "hour": "13:00", "total_hits": 229600, "share": "6.63%"},
            {"rank": 4, "hour": "12:00", "total_hits": 224100, "share": "6.47%"},
            {"rank": 5, "hour": "04:00 (Trough)", "total_hits": 71200, "share": "2.06%"},
        ],
    },
}

_SAMPLE_JOURNEY = [
    {"url": "/", "status": 200, "bytes": 6245, "delta": 0},
    {"url": "/images/NASA-logosmall.gif", "status": 304, "bytes": 0, "delta": 1},
    {"url": "/images/MOSAIC-logosmall.gif", "status": 200, "bytes": 1284, "delta": 2},
    {"url": "/ksc.html", "status": 200, "bytes": 7060, "delta": 18},
    {"url": "/history/apollo/", "status": 200, "bytes": 8340, "delta": 45},
    {"url": "/shuttle/missions/sts-70/mission-sts-70.html", "status": 200, "bytes": 14200, "delta": 75},
    {"url": "/images/launch-logo.gif", "status": 200, "bytes": 3120, "delta": 76},
    {"url": "/shuttle/countdown/liftoff.html", "status": 200, "bytes": 5600, "delta": 110},
]


def build_session_detail(sess):
    """Build a demo clickstream journey around a real session summary."""
    host = sess.get("host", "199.72.81.55")
    start = sess.get("start_time", "1995-07-01 00:00:01")
    count = sess.get("request_count", 4)
    duration = sess.get("duration_seconds", 120)

    journey = [
        {
            "step": i + 1,
            "url": p["url"],
            "status": p["status"],
            "bytes": p["bytes"],
            "elapsed_seconds": min(duration, p["delta"]),
            "timestamp": start,
        }
        for i, p in enumerate(_SAMPLE_JOURNEY[: min(count, len(_SAMPLE_JOURNEY))])
    ]

    return {
        "session_summary": sess,
        "journey": journey,
        "inactivity_threshold_seconds": 1800,
        "mapper_key": host,
        "storage_layer": "Hadoop HDFS -> MapReduce -> MongoDB Atlas",
    }
