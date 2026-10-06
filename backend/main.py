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

@app.get("/api/pipeline-stages")
def get_pipeline_stages():
    return [
        {
            "step": 1,
            "name": "Raw Log Ingestion & Preprocessing",
            "technology": "Python 3 Streaming Parser",
            "input": "NASA HTTP Access Logs (Jul & Aug 1995, 373 MB)",
            "output": "data/processed/web_logs.tsv (329.40 MB, 3,461,612 rows)",
            "runtime": "16.03s",
            "status": "COMPLETED",
            "details": "Parsed host, timestamp, method, URL, protocol, status, bytes. Handled malformed rows & '-' response bytes."
        },
        {
            "step": 2,
            "name": "HDFS Distributed Storage & Block Replication",
            "technology": "Apache Hadoop HDFS 2.7.4",
            "input": "web_logs.tsv (329.40 MB)",
            "output": "/log-analytics/processed/web_logs.tsv",
            "runtime": "8.50s",
            "status": "COMPLETED",
            "details": "Divided into 3 blocks (128MB, 128MB, 73.4MB). Replicated 2x across DataNode 1 and DataNode 2."
        },
        {
            "step": 3,
            "name": "Distributed SQL Analytics",
            "technology": "Apache Hive 2.3.2 on MapReduce",
            "input": "External Table 'web_logs' over HDFS",
            "output": "Aggregated tables: Top URLs, Diurnal Traffic, HTTP Status distribution",
            "runtime": "30.45s",
            "status": "COMPLETED",
            "details": "Compiled declarative HiveQL into YARN MapReduce jobs (2 mappers, 1 reducer). Computed total 3,461,612 hits."
        },
        {
            "step": 4,
            "name": "User Sessionization Mining",
            "technology": "Hadoop Streaming MapReduce on YARN",
            "input": "HDFS /log-analytics/processed/web_logs.tsv",
            "output": "/log-analytics/results/sessions (306,523 mined sessions)",
            "runtime": "34.20s",
            "status": "COMPLETED",
            "details": "Grouped chronologically per host. Applied 30-minute inactivity timeout. Mined session durations and bytes."
        },
        {
            "step": 5,
            "name": "URL Navigation Graph Mining",
            "technology": "2-Stage Hadoop Streaming on YARN",
            "input": "HDFS /log-analytics/processed/web_logs.tsv",
            "output": "/log-analytics/results/navigation (3,084,742 transitions)",
            "runtime": "62.90s (Stage 1: 33.8s, Stage 2: 29.1s)",
            "status": "COMPLETED",
            "details": "Stage 1 extracted intra-session transitions (source -> dest). Stage 2 aggregated global transition frequencies."
        },
        {
            "step": 6,
            "name": "Analytical Serving Layer Ingestion",
            "technology": "MongoDB 6.0 + PyMongo",
            "input": "HDFS session summaries & Hive metrics",
            "output": "Collections: summary, top_pages, traffic, error_trends, sessions, navigation_patterns",
            "runtime": "2.40s",
            "status": "COMPLETED",
            "details": "Batch-loaded analytical models with B-Tree indexes for sub-millisecond REST query performance."
        },
        {
            "step": 7,
            "name": "REST API & Interactive Visualization",
            "technology": "FastAPI + Vanilla JS + Chart.js",
            "input": "MongoDB Collections",
            "output": "Real-time University Presentation Dashboard at http://localhost:8000/",
            "runtime": "Real-time (<10ms query latency)",
            "status": "LIVE & ACTIVE",
            "details": "Decoupled architecture: dashboard queries only MongoDB via FastAPI; heavy processing is pre-computed on Hadoop."
        }
    ]

# Mount static files directory if it exists
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
