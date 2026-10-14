"""End-to-end pipeline trace simulation for a single log line.

Parses one Common Log Format record and renders the (illustrative) journey it
takes through preprocessing, HDFS, Hive, MapReduce and the MongoDB serving
layer. Used by the dashboard's "simulate trace" feature.
"""

import re
from datetime import datetime

DEFAULT_LOG = '199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245'

_LOG_PATTERN = re.compile(r'^(\S+) - - \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d{3}) (\S+)$')

_HDFS_BLOCKS = [
    {"id": "blk_1073741825_1001", "primary": "datanode1 (172.18.0.9)", "replica": "datanode2 (172.18.0.2)", "offset": "Byte 0 - 134,217,728"},
    {"id": "blk_1073741826_1002", "primary": "datanode1 (172.18.0.9)", "replica": "datanode2 (172.18.0.2)", "offset": "Byte 134,217,729 - 268,435,456"},
    {"id": "blk_1073741827_1003", "primary": "datanode1 (172.18.0.9)", "replica": "datanode2 (172.18.0.2)", "offset": "Byte 268,435,457 - 345,403,634"},
]

_FALLBACK = {
    "host": "199.72.81.55",
    "method": "GET",
    "url": "/history/apollo/",
    "protocol": "HTTP/1.0",
    "status": 200,
    "response_bytes": 6245,
    "epoch": 804571201,
    "iso_time": "1995-07-01 00:00:01",
}


def _parse(log):
    match = _LOG_PATTERN.match(log.strip())
    if not match:
        return dict(_FALLBACK)

    host, raw_time, method, url, protocol, status_str, bytes_str = match.groups()
    try:
        dt = datetime.strptime(raw_time, "%d/%b/%Y:%H:%M:%S %z")
        epoch = int(dt.timestamp())
        iso_time = dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        epoch, iso_time = _FALLBACK["epoch"], _FALLBACK["iso_time"]

    return {
        "host": host,
        "method": method,
        "url": url,
        "protocol": protocol,
        "status": int(status_str),
        "response_bytes": int(bytes_str) if bytes_str.isdigit() else 0,
        "epoch": epoch,
        "iso_time": iso_time,
    }


def simulate(log):
    r = _parse(log)
    host, url, status, iso_time = r["host"], r["url"], r["status"], r["iso_time"]

    block = _HDFS_BLOCKS[abs(hash(host + url)) % len(_HDFS_BLOCKS)]
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
                    "host": host, "timestamp": iso_time, "method": r["method"],
                    "url": url, "protocol": r["protocol"], "status": status,
                    "response_bytes": r["response_bytes"],
                },
                "tsv_representation": f"{host}\t{iso_time}\t{r['method']}\t{url}\t{r['protocol']}\t{status}\t{r['response_bytes']}",
                "description": "Validated against Common Log Format regex with O(1) streaming memory.",
            },
            {
                "stage": 2,
                "name": "HDFS Block Partitioning & 2x Replication",
                "container": "namenode:50070 -> datanode1 & datanode2",
                "technology": "Apache Hadoop HDFS 2.7.4",
                "output_data": {
                    "assigned_block_id": block["id"],
                    "primary_datanode": block["primary"],
                    "secondary_replica": block["replica"],
                    "byte_offset_range": block["offset"],
                    "replication_factor": 2,
                    "checksum_verification": "MD5/CRC32 Verified Healthy",
                },
                "description": "NameNode assigns the record to an HDFS block, pipelined across both DataNodes.",
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
                    "storage_location": "/log-analytics/processed/web_logs.tsv",
                },
                "description": "External Hive table reads the raw TSV from HDFS; HiveQL compiles to MapReduce on YARN.",
            },
            {
                "stage": 4,
                "name": "MapReduce Sessionization Mining",
                "container": f"nodemanager{reducer_id + 1}:8042 (Container executor)",
                "technology": "Hadoop Streaming (session_mapper.py | session_reducer.py)",
                "output_data": {
                    "mapper_output_key": host,
                    "mapper_output_value": f"{r['epoch']}\t{iso_time}\t{url}\t{r['response_bytes']}",
                    "yarn_partition": f"Reducer Task #{reducer_id} via hash('{host}') % 2",
                    "session_timeout_logic": "dt <= 1800s => same session; dt > 1800s => new session",
                    "mined_session_id": f"{host}_s1",
                    "status": "Session Boundary Calculated",
                },
                "description": "Shuffle & sort groups all hits per host to one reducer, which detects the 30-min boundary.",
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
                    "graph_topology": "Directed edge added to web navigation graph",
                },
                "description": "Stage 1 extracts directed click pairs; Stage 2 aggregates transition counts globally.",
            },
            {
                "stage": 6,
                "name": "Analytical Serving Layer Ingestion",
                "container": "MongoDB Atlas (Serving Store)",
                "technology": "MongoDB Document Model & B-Tree Indexes",
                "output_data": {
                    "collection": "sessions & navigation_patterns",
                    "document_stored": {
                        "host": host,
                        "session_id": f"{host}_s1",
                        "request_count": 1,
                        "start_time": iso_time,
                        "end_time": iso_time,
                        "duration_seconds": 0,
                        "total_bytes": r["response_bytes"],
                    },
                    "indexed_fields": ["session_id", "host", "request_count", "duration_seconds"],
                },
                "description": "Batch loader ingests MapReduce/Hive outputs into MongoDB Atlas with B-Tree indexes.",
            },
            {
                "stage": 7,
                "name": "FastAPI Presentation & Visual Dashboard",
                "container": "backend:8000 (FastAPI + Web UI)",
                "technology": "REST API + Chart.js Visualization",
                "output_data": {
                    "endpoint_served": "/api/sessions & /api/navigation",
                    "query_latency_ms": "1.42 ms",
                    "status_code": 200,
                    "dashboard_visual": "KPI cards, line/bar charts, interactive explorer",
                },
                "description": "Browser queries FastAPI directly; precomputed results are served instantly.",
            },
        ],
    }
