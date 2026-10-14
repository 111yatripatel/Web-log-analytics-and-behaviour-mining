"""FastAPI service exposing aggregated web-log analytics stored in MongoDB.

Connects to MongoDB Atlas (or any MongoDB) via the MONGODB_URI environment
variable. Static demo data for cluster/benchmark views lives in `demo_data.py`.
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import PyMongoError

import demo_data
import trace as trace_demo

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "web_log_analytics")

app = FastAPI(
    title="Distributed Web Log Analytics API",
    description="REST API serving aggregated analytics from Hadoop/Hive/MapReduce via MongoDB.",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A single pooled client is reused across requests (thread-safe by design).
_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)


def get_db():
    return _client[DATABASE_NAME]


def read_collection(name, *, sort=None, limit=0):
    """Return documents from a collection, hiding the Mongo `_id` field."""
    try:
        cursor = get_db()[name].find({}, {"_id": 0})
        if sort:
            cursor = cursor.sort(*sort)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    except PyMongoError as exc:
        return {"error": str(exc)}


@app.get("/api/health")
def health_check():
    try:
        get_db().command("ping")
        mongo_status = "connected"
    except PyMongoError as exc:
        mongo_status = f"unavailable: {exc}"
    return {
        "status": "online",
        "service": "distributed-web-log-analytics-backend",
        "mongodb": mongo_status,
    }


@app.get("/api/summary")
def get_summary():
    try:
        doc = get_db()["summary"].find_one({}, {"_id": 0})
    except PyMongoError as exc:
        return {"error": str(exc)}
    return doc or {"status": "no data loaded yet"}


@app.get("/api/top-pages")
def get_top_pages(limit: int = 20):
    return read_collection("top_pages", sort=("request_count", DESCENDING), limit=limit)


@app.get("/api/traffic")
def get_traffic():
    return read_collection("traffic", sort=("hour", ASCENDING))


@app.get("/api/errors")
def get_errors():
    return read_collection("error_trends", sort=("hour", ASCENDING))


@app.get("/api/sessions")
def get_sessions(limit: int = 50):
    return read_collection("sessions", limit=limit)


@app.get("/api/navigation")
def get_navigation(limit: int = 25):
    return read_collection("navigation_patterns", sort=("count", DESCENDING), limit=limit)


@app.get("/api/session-detail/{session_id}")
def get_session_detail(session_id: str):
    try:
        sessions = get_db()["sessions"]
        sess = sessions.find_one({"session_id": session_id}, {"_id": 0}) or sessions.find_one({}, {"_id": 0})
    except PyMongoError as exc:
        return {"error": str(exc)}
    if not sess:
        return {"error": "Session not found"}
    return demo_data.build_session_detail(sess)


# --- Static demo endpoints (precomputed cluster/benchmark views) ---------

@app.get("/api/cluster")
def get_cluster_topology():
    return demo_data.CLUSTER_TOPOLOGY


@app.get("/api/status-codes")
def get_status_codes():
    return demo_data.STATUS_CODES


@app.get("/api/session-distribution")
def get_session_distribution():
    return demo_data.SESSION_DISTRIBUTION


@app.get("/api/benchmarks")
def get_benchmarks():
    return demo_data.BENCHMARKS


@app.get("/api/hdfs-block/{block_id}")
def get_hdfs_block(block_id: str):
    catalog = demo_data.HDFS_BLOCKS
    return catalog.get(block_id, next(iter(catalog.values())))


@app.get("/api/hive-query")
def run_hive_query(query_id: str = "q1"):
    return demo_data.HIVE_QUERIES.get(query_id, demo_data.HIVE_QUERIES["q1"])


@app.get("/api/simulate-trace")
def simulate_trace(log: str = trace_demo.DEFAULT_LOG):
    return trace_demo.simulate(log)


# --- Static dashboard files ----------------------------------------------

_static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static_path):
    app.mount("/", StaticFiles(directory=_static_path, html=True), name="static")
