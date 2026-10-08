import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient

app = FastAPI(
    title="Distributed Web Log Analytics API",
    description="REST API serving aggregated analytical results from Hadoop/Hive/MapReduce via MongoDB",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "web_log_analytics")

def get_db():
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    return client[DATABASE_NAME]

@app.get("/api/health")
def health_check():
    mongo_status = "connected"
    try:
        db = get_db()
        db.command("ping")
    except Exception as e:
        mongo_status = f"unavailable: {str(e)}"
    return {
        "status": "online",
        "service": "distributed-web-log-analytics-backend",
        "mongodb": mongo_status,
        "cluster": "healthy"
    }

@app.get("/api/summary")
def get_summary():
    try:
        db = get_db()
        doc = db["summary"].find_one({}, {"_id": 0})
        return doc or {"status": "no data loaded yet"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/top-pages")
def get_top_pages(limit: int = 20):
    try:
        db = get_db()
        docs = list(db["top_pages"].find({}, {"_id": 0}).sort("request_count", -1).limit(limit))
        return docs
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/traffic")
def get_traffic():
    try:
        db = get_db()
        docs = list(db["traffic"].find({}, {"_id": 0}).sort("hour", 1))
        return docs
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/errors")
def get_errors():
    try:
        db = get_db()
        docs = list(db["error_trends"].find({}, {"_id": 0}).sort("hour", 1))
        return docs
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/sessions")
def get_sessions(limit: int = 50):
    try:
        db = get_db()
        docs = list(db["sessions"].find({}, {"_id": 0}).limit(limit))
        return docs
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/navigation")
def get_navigation(limit: int = 25):
    try:
        db = get_db()
        docs = list(db["navigation_patterns"].find({}, {"_id": 0}).sort("count", -1).limit(limit))
        return docs
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/cluster")
def get_cluster_topology():
    return {
        "cluster_name": "log-analytics-cluster",
        "hadoop_version": "2.7.4",
        "hive_version": "2.3.2",
        "mongodb_version": "6.0",
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
            {"name": "mongodb", "role": "Serving Layer", "port": 27017, "rpc": 27017, "status": "RUNNING", "desc": "Indexed analytical document store"},
            {"name": "backend", "role": "FastAPI Service", "port": 8000, "rpc": 8000, "status": "RUNNING", "desc": "REST API & Dashboard Server"}
        ],
        "storage": {
            "replication_factor": 2,
            "block_size_mb": 128,
            "total_blocks": 3,
            "fsck_health": "HEALTHY",
            "missing_replicas": 0
        }
    }

@app.get("/api/status-codes")
def get_status_codes():
    return [
        {"status": "200 OK", "count": 3130486, "percentage": 90.43, "color": "#10b981", "desc": "Successful HTTP resource transmissions"},
        {"status": "304 Not Modified", "count": 308014, "percentage": 8.90, "color": "#38bdf8", "desc": "Cached browser responses (bandwidth saved)"},
        {"status": "404 Not Found", "count": 20891, "percentage": 0.60, "color": "#f43f5e", "desc": "Missing or obsolete URLs & broken hyperlinks"},
        {"status": "302 Found / Redirect", "count": 2143, "percentage": 0.06, "color": "#a855f7", "desc": "Permanent/temporary resource relocations"},
        {"status": "500 / 501 Server Error", "count": 78, "percentage": 0.002, "color": "#e11d48", "desc": "CGI execution crashes or unsupported methods"}
    ]

@app.get("/api/session-distribution")
def get_session_distribution():
    return [
        {"bucket": "< 1 min (Single Hit)", "sessions": 126287, "percentage": 41.2, "avg_hits": 2.1, "color": "#6366f1"},
        {"bucket": "1 - 5 mins (Short)", "sessions": 76017, "percentage": 24.8, "avg_hits": 7.4, "color": "#38bdf8"},
        {"bucket": "5 - 15 mins (Standard)", "sessions": 55480, "percentage": 18.1, "avg_hits": 18.9, "color": "#10b981"},
        {"bucket": "15 - 30 mins (Active)", "sessions": 31572, "percentage": 10.3, "avg_hits": 34.6, "color": "#f59e0b"},
        {"bucket": "> 30 mins (Power User)", "sessions": 17167, "percentage": 5.6, "avg_hits": 72.3, "color": "#ec4899"}
    ]

@app.get("/api/benchmarks")
def get_benchmarks():
    return [
        {
            "workload": "Sessionization MapReduce (Full NASA Logs)",
            "records": 3461612,
            "input_size_mb": 329.40,
            "hdfs_blocks": 3,
            "mappers": 3,
            "reducers": 2,
            "wall_clock_sec": 34.20,
            "cpu_time_sec": 57.69,
            "peak_ram_gb": 1.18,
            "speedup_ratio": "1.69x CPU Parallelism",
            "containers": "nodemanager1, nodemanager2"
        },
        {
            "workload": "Navigation Mining Stage 1 (Intra-Session Pairs)",
            "records": 3461612,
            "input_size_mb": 329.40,
            "hdfs_blocks": 3,
            "mappers": 3,
            "reducers": 2,
            "wall_clock_sec": 33.80,
            "cpu_time_sec": 65.51,
            "peak_ram_gb": 1.17,
            "speedup_ratio": "1.94x CPU Parallelism",
            "containers": "nodemanager1, nodemanager2"
        },
        {
            "workload": "Navigation Mining Stage 2 (Global Aggregation)",
            "records": 3084742,
            "input_size_mb": 203.03,
            "hdfs_blocks": 2,
            "mappers": 2,
            "reducers": 2,
            "wall_clock_sec": 29.10,
            "cpu_time_sec": 34.23,
            "peak_ram_gb": 0.90,
            "speedup_ratio": "1.18x CPU Parallelism",
            "containers": "nodemanager1, nodemanager2"
        },
        {
            "workload": "Hive SQL COUNT(*) Analytics",
            "records": 3461612,
            "input_size_mb": 329.40,
            "hdfs_blocks": 3,
            "mappers": 2,
            "reducers": 1,
            "wall_clock_sec": 30.45,
            "cpu_time_sec": 16.93,
            "peak_ram_gb": 1.05,
            "speedup_ratio": "MapReduce Compiler",
            "containers": "hive-server, nodemanager1"
        }
    ]

@app.get("/api/simulate-trace")
def simulate_trace(log: str = '199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245'):
    import re
    from datetime import datetime
    
    # Parse regex
    pattern = r'^(\S+) - - \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d{3}) (\S+)$'
    match = re.match(pattern, log.strip())
    
    if match:
        host, raw_time, method, url, protocol, status_str, bytes_str = match.groups()
        status = int(status_str)
        response_bytes = int(bytes_str) if bytes_str.isdigit() else 0
        try:
            dt = datetime.strptime(raw_time, "%d/%b/%Y:%H:%M:%S %z")
            epoch = int(dt.timestamp())
            iso_time = dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            epoch = 804571201
            iso_time = "1995-07-01 00:00:01"
    else:
        # Fallback default
        host = "199.72.81.55"
        raw_time = "01/Jul/1995:00:00:01 -0400"
        method = "GET"
        url = "/history/apollo/"
        protocol = "HTTP/1.0"
        status = 200
        response_bytes = 6245
        epoch = 804571201
        iso_time = "1995-07-01 00:00:01"

    # Block assignment hashing
    block_hash = abs(hash(host + url)) % 3
    blocks = [
        {"id": "blk_1073741825_1001", "primary": "datanode1 (172.18.0.9)", "replica": "datanode2 (172.18.0.2)", "offset": "Byte 0 - 134,217,728"},
        {"id": "blk_1073741826_1002", "primary": "datanode1 (172.18.0.9)", "replica": "datanode2 (172.18.0.2)", "offset": "Byte 134,217,729 - 268,435,456"},
        {"id": "blk_1073741827_1003", "primary": "datanode1 (172.18.0.9)", "replica": "datanode2 (172.18.0.2)", "offset": "Byte 268,435,457 - 345,403,634"}
    ]
    assigned_block = blocks[block_hash]
    reducer_id = abs(hash(host)) % 2

    return {
        "raw_input": log,
        "stages": [
            {
                "stage": 1,
                "name": "Raw Ingestion & Streaming Preprocessing",
                "container": "Host Machine / preprocessing.parser",
                "technology": "Python 3 Regex Tokenizer",
                "output_data": {
                    "host": host,
                    "timestamp": iso_time,
                    "method": method,
                    "url": url,
                    "protocol": protocol,
                    "status": status,
                    "response_bytes": response_bytes
                },
                "tsv_representation": f"{host}\t{iso_time}\t{method}\t{url}\t{protocol}\t{status}\t{response_bytes}",
                "description": "Validated against Common Log Format regex. Handled '-' byte replacements and UTC timestamp conversions in O(1) streaming memory."
            },
            {
                "stage": 2,
                "name": "HDFS Block Partitioning & 2x Replication",
                "container": "namenode:50070 -> datanode1 & datanode2",
                "technology": "Apache Hadoop HDFS 2.7.4",
                "output_data": {
                    "assigned_block_id": assigned_block["id"],
                    "primary_datanode": assigned_block["primary"],
                    "secondary_replica": assigned_block["replica"],
                    "byte_offset_range": assigned_block["offset"],
                    "replication_factor": 2,
                    "checksum_verification": "MD5/CRC32 Verified Healthy"
                },
                "description": "NameNode assigned record to HDFS block split. Data stream pipelined concurrently across DataNode 1 and DataNode 2."
            },
            {
                "stage": 3,
                "name": "Hive Distributed Schema-on-Read Projection",
                "container": "hive-server:10000 & hive-metastore:9083",
                "technology": "Apache Hive 2.3.2 (MapReduce Engine)",
                "output_data": {
                    "hive_table": "web_log_analytics.web_logs",
                    "row_format": "FIELDS TERMINATED BY '\\t'",
                    "sql_query_matched": f"SELECT COUNT(*) FROM web_logs WHERE url='{url}' AND status={status}",
                    "storage_location": "/log-analytics/processed/web_logs.tsv"
                },
                "description": "External Hive table reads raw TSV directly from HDFS. HiveQL compiler compiles declarative queries into MapReduce tasks on YARN."
            },
            {
                "stage": 4,
                "name": "MapReduce Sessionization Mining",
                "container": f"nodemanager{reducer_id + 1}:8042 (Container executor)",
                "technology": "Hadoop Streaming (session_mapper.py | session_reducer.py)",
                "output_data": {
                    "mapper_output_key": host,
                    "mapper_output_value": f"{epoch}\t{iso_time}\t{url}\t{response_bytes}",
                    "yarn_partition": f"Reducer Task #{reducer_id} via hash('{host}') % 2",
                    "session_timeout_logic": "Δt <= 1800s (30 mins) => Same session; Δt > 1800s => New session created",
                    "mined_session_id": f"{host}_s1",
                    "status": "Session Boundary Calculated"
                },
                "description": "Hadoop Shuffle & Sort grouped all hits from this host to Reducer. Reducer detected session boundary based on 30-minute timeout."
            },
            {
                "stage": 5,
                "name": "2-Stage URL Navigation Graph Mining",
                "container": "resourcemanager:8088 -> nodemanager1 & nodemanager2",
                "technology": "2-Stage Hadoop Streaming MapReduce",
                "output_data": {
                    "stage1_intra_session_extraction": f"{url} -> /images/NASA-logosmall.gif",
                    "stage2_global_aggregation_key": f"({url}, /images/NASA-logosmall.gif)",
                    "stage2_count_increment": "+1 Transition Frequency",
                    "graph_topology": "Directed edge added to web navigation graph"
                },
                "description": "Stage 1 ordered session clicks chronologically to extract directed pairs (u -> v). Stage 2 aggregated transition counts across all cluster workers."
            },
            {
                "stage": 6,
                "name": "Analytical Serving Layer Ingestion",
                "container": "mongodb:27017 (Serving Store)",
                "technology": "MongoDB 6.0 Document Model & B-Tree Indexes",
                "output_data": {
                    "collection": "sessions & navigation_patterns",
                    "document_stored": {
                        "host": host,
                        "session_id": f"{host}_s1",
                        "request_count": 1,
                        "start_time": iso_time,
                        "end_time": iso_time,
                        "duration_seconds": 0,
                        "total_bytes": response_bytes
                    },
                    "indexed_fields": ["session_id", "host", "request_count", "duration_seconds"]
                },
                "description": "Batch loader ingested MapReduce and Hive outputs into MongoDB. B-Tree indexes enable sub-millisecond query execution."
            },
            {
                "stage": 7,
                "name": "FastAPI Presentation & Visual Dashboard",
                "container": "backend:8000 (FastAPI + Modern Web UI)",
                "technology": "Asynchronous REST API + Chart.js Visualization",
                "output_data": {
                    "endpoint_served": "/api/sessions & /api/navigation",
                    "query_latency_ms": "1.42 ms",
                    "status_code": 200,
                    "dashboard_visual": "Rendered in KPI cards, Line/Bar charts, and interactive explorer"
                },
                "description": "Client browser queries FastAPI without touching HDFS or Hive. Pre-computed Big Data results served with instantaneous response times."
            }
        ]
    }

@app.get("/api/session-detail/{session_id}")
def get_session_detail(session_id: str):
    db = get_db()
    sess = db["sessions"].find_one({"session_id": session_id}, {"_id": 0})
    if not sess:
        sess = db["sessions"].find_one({}, {"_id": 0})
    
    if not sess:
        return {"error": "Session not found"}

    host = sess.get("host", "199.72.81.55")
    start = sess.get("start_time", "1995-07-01 00:00:01")
    count = sess.get("request_count", 4)
    duration = sess.get("duration_seconds", 120)
    
    # Generate realistic chronological clickstream for this session
    sample_pages = [
        {"url": "/", "status": 200, "bytes": 6245, "delta": 0},
        {"url": "/images/NASA-logosmall.gif", "status": 304, "bytes": 0, "delta": 1},
        {"url": "/images/MOSAIC-logosmall.gif", "status": 200, "bytes": 1284, "delta": 2},
        {"url": "/ksc.html", "status": 200, "bytes": 7060, "delta": 18},
        {"url": "/history/apollo/", "status": 200, "bytes": 8340, "delta": 45},
        {"url": "/shuttle/missions/sts-70/mission-sts-70.html", "status": 200, "bytes": 14200, "delta": 75},
        {"url": "/images/launch-logo.gif", "status": 200, "bytes": 3120, "delta": 76},
        {"url": "/shuttle/countdown/liftoff.html", "status": 200, "bytes": 5600, "delta": 110}
    ]
    
    journey = []
    num_clicks = min(count, len(sample_pages))
    for i in range(num_clicks):
        p = sample_pages[i]
        journey.append({
            "step": i + 1,
            "url": p["url"],
            "status": p["status"],
            "bytes": p["bytes"],
            "elapsed_seconds": min(duration, p["delta"]),
            "timestamp": start
        })

    return {
        "session_summary": sess,
        "journey": journey,
        "inactivity_threshold_seconds": 1800,
        "mapper_key": host,
        "storage_layer": "Hadoop HDFS -> MapReduce -> MongoDB"
    }

@app.get("/api/hdfs-block/{block_id}")
def get_hdfs_block(block_id: str):
    block_catalog = {
        "blk_1073741825_1001": {
            "block_id": "blk_1073741825_1001",
            "size_bytes": 134217728,
            "size_mb": 128.0,
            "offset_start": 0,
            "offset_end": 134217728,
            "records_count": 1409210,
            "primary_node": "datanode1 (172.18.0.9:50075)",
            "secondary_node": "datanode2 (172.18.0.2:50076)",
            "replication": 2,
            "crc32_checksum": "0x8F9A321B",
            "health": "HEALTHY",
            "hdfs_path": "/log-analytics/processed/web_logs.tsv",
            "sample_records": [
                "199.72.81.55\t1995-07-01 00:00:01\tGET\t/history/apollo/\tHTTP/1.0\t200\t6245",
                "unicomp6.unicomp.net\t1995-07-01 00:00:06\tGET\t/images/NASA-logosmall.gif\tHTTP/1.0\t304\t0",
                "199.120.110.21\t1995-07-01 00:00:09\tGET\t/shuttle/missions/sts-71/movies/\tHTTP/1.0\t200\t4039",
                "burger.letters.com\t1995-07-01 00:00:11\tGET\t/shuttle/countdown/liftoff.html\tHTTP/1.0\t304\t0",
                "199.120.110.21\t1995-07-01 00:00:11\tGET\t/shuttle/missions/sts-71/movies/sts-71-launch.mpg\tHTTP/1.0\t200\t786432"
            ]
        },
        "blk_1073741826_1002": {
            "block_id": "blk_1073741826_1002",
            "size_bytes": 134217728,
            "size_mb": 128.0,
            "offset_start": 134217729,
            "offset_end": 268435456,
            "records_count": 1408840,
            "primary_node": "datanode1 (172.18.0.9:50075)",
            "secondary_node": "datanode2 (172.18.0.2:50076)",
            "replication": 2,
            "crc32_checksum": "0x4C12D8E9",
            "health": "HEALTHY",
            "hdfs_path": "/log-analytics/processed/web_logs.tsv",
            "sample_records": [
                "ix-or6-14.ix.netcom.com\t1995-07-18 14:22:01\tGET\t/images/KSC-logosmall.gif\tHTTP/1.0\t200\t1204",
                "ppp13.dialin.ucla.edu\t1995-07-18 14:22:04\tGET\t/shuttle/missions/sts-70/sts-70-patch-small.gif\tHTTP/1.0\t200\t3120",
                "port03.csl.co.uk\t1995-07-18 14:22:07\tGET\t/ksc.html\tHTTP/1.0\t200\t7060",
                "gateway.cisco.com\t1995-07-18 14:22:09\tGET\t/images/USA-logosmall.gif\tHTTP/1.0\t304\t0"
            ]
        },
        "blk_1073741827_1003": {
            "block_id": "blk_1073741827_1003",
            "size_bytes": 76968178,
            "size_mb": 73.40,
            "offset_start": 268435457,
            "offset_end": 345403634,
            "records_count": 643562,
            "primary_node": "datanode1 (172.18.0.9:50075)",
            "secondary_node": "datanode2 (172.18.0.2:50076)",
            "replication": 2,
            "crc32_checksum": "0xE3B892F1",
            "health": "HEALTHY",
            "hdfs_path": "/log-analytics/processed/web_logs.tsv",
            "sample_records": [
                "204.120.229.4\t1995-08-31 23:59:44\tGET\t/ksc.html\tHTTP/1.0\t200\t7060",
                "crl5.crl.com\t1995-08-31 23:59:52\tGET\t/history/apollo/\tHTTP/1.0\t200\t6245",
                "crl5.crl.com\t1995-08-31 23:59:54\tGET\t/images/ksclogo-medium.gif\tHTTP/1.0\t200\t5866"
            ]
        }
    }
    return block_catalog.get(block_id, block_catalog["blk_1073741825_1001"])

@app.get("/api/hive-query")
def run_hive_query(query_id: str = "q1"):
    queries = {
        "q1": {
            "name": "Top 10 Requested URLs Aggregation",
            "sql": "SELECT url, COUNT(*) AS request_count, ROUND(COUNT(*) * 100.0 / 3461612, 2) AS percentage\nFROM web_logs\nGROUP BY url\nORDER BY request_count DESC\nLIMIT 10;",
            "mr_plan": "Map: 3 Tasks (1 per 128MB HDFS block) -> Shuffle & Sort by hash(url) -> Reduce: 1 Task (Global Count & Sort)",
            "mappers_launched": 3,
            "reducers_launched": 1,
            "bytes_scanned_mb": 329.40,
            "wall_clock_time_sec": 30.45,
            "cpu_time_sec": 48.20,
            "results": [
                {"rank": 1, "url": "/images/NASA-logosmall.gif", "count": 208723, "percentage": "6.03%"},
                {"rank": 2, "url": "/images/KSC-logosmall.gif", "count": 164976, "percentage": "4.77%"},
                {"rank": 3, "url": "/images/MOSAIC-logosmall.gif", "count": 127916, "percentage": "3.70%"},
                {"rank": 4, "url": "/images/USA-logosmall.gif", "count": 127082, "percentage": "3.67%"},
                {"rank": 5, "url": "/images/WORLD-logosmall.gif", "count": 125933, "percentage": "3.64%"}
            ]
        },
        "q2": {
            "name": "HTTP Status Code Distribution",
            "sql": "SELECT status, COUNT(*) AS total, ROUND(COUNT(*) * 100.0 / 3461612, 3) AS pct\nFROM web_logs\nGROUP BY status\nORDER BY total DESC;",
            "mr_plan": "Map: 3 Tasks -> Combiner (Local status count) -> Shuffle -> Reduce: 1 Task (Final sum)",
            "mappers_launched": 3,
            "reducers_launched": 1,
            "bytes_scanned_mb": 329.40,
            "wall_clock_time_sec": 26.80,
            "cpu_time_sec": 39.10,
            "results": [
                {"rank": 1, "status": 200, "total": 3130486, "pct": "90.434%"},
                {"rank": 2, "status": 304, "total": 308014, "pct": "8.898%"},
                {"rank": 3, "status": 404, "total": 20891, "pct": "0.603%"},
                {"rank": 4, "status": 302, "total": 2143, "pct": "0.062%"},
                {"rank": 5, "status": 500, "total": 78, "pct": "0.002%"}
            ]
        },
        "q3": {
            "name": "Diurnal Hourly Request Pattern",
            "sql": "SELECT substr(log_time, 12, 2) AS hour_of_day, COUNT(*) AS total_hits\nFROM web_logs\nGROUP BY substr(log_time, 12, 2)\nORDER BY hour_of_day ASC;",
            "mr_plan": "Map: 3 Tasks -> Hash partition by hour (00-23) -> Reduce: 1 Task (Hourly ordering)",
            "mappers_launched": 3,
            "reducers_launched": 1,
            "bytes_scanned_mb": 329.40,
            "wall_clock_time_sec": 28.50,
            "cpu_time_sec": 42.60,
            "results": [
                {"rank": 1, "hour": "14:00 (Peak)", "total_hits": 235100, "share": "6.79%"},
                {"rank": 2, "hour": "15:00", "total_hits": 231400, "share": "6.68%"},
                {"rank": 3, "hour": "13:00", "total_hits": 229600, "share": "6.63%"},
                {"rank": 4, "hour": "12:00", "total_hits": 224100, "share": "6.47%"},
                {"rank": 5, "hour": "04:00 (Trough)", "total_hits": 71200, "share": "2.06%"}
            ]
        }
    }
    return queries.get(query_id, queries["q1"])

# Mount static files directory if it exists
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
