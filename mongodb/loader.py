#!/usr/bin/env python3
"""Load aggregated Hive/MapReduce results into MongoDB (Atlas or local).

Set the connection string via the MONGODB_URI environment variable (a `.env`
file in the project root is loaded automatically). For Atlas use the SRV URI,
e.g. mongodb+srv://user:pass@cluster0.xxxx.mongodb.net/
"""

import os
import subprocess
import time

from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient

import sample_data

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "web_log_analytics")

# Static analytics (precomputed from Hive). Grouped here for readability.
SUMMARY = {
    "dataset_name": "NASA Kennedy Space Center HTTP Logs",
    "total_requests": 3461612,
    "total_sessions": 306523,
    "total_response_bytes": 65499082041,
    "avg_response_bytes": 18921.57,
    "error_rate_percent": 0.61,
    "replication_factor": 2,
    "processing_engine": "Hadoop YARN & Hive & MapReduce",
    "serving_database": "MongoDB Atlas",
}

TOP_PAGES = [
    {"url": "/images/NASA-logosmall.gif", "request_count": 208723, "percentage": 6.03},
    {"url": "/images/KSC-logosmall.gif", "request_count": 164976, "percentage": 4.77},
    {"url": "/images/MOSAIC-logosmall.gif", "request_count": 127916, "percentage": 3.70},
    {"url": "/images/USA-logosmall.gif", "request_count": 127082, "percentage": 3.67},
    {"url": "/images/WORLD-logosmall.gif", "request_count": 125933, "percentage": 3.64},
    {"url": "/images/ksclogo-medium.gif", "request_count": 121580, "percentage": 3.51},
    {"url": "/ksc.html", "request_count": 83912, "percentage": 2.42},
    {"url": "/images/launch-logo.gif", "request_count": 76009, "percentage": 2.20},
    {"url": "/history/apollo/images/apollo-logo1.gif", "request_count": 68898, "percentage": 1.99},
    {"url": "/shuttle/countdown/", "request_count": 64739, "percentage": 1.87},
    {"url": "/", "request_count": 63175, "percentage": 1.83},
    {"url": "/images/ksclogosmall.gif", "request_count": 61395, "percentage": 1.77},
    {"url": "/shuttle/missions/missions.html", "request_count": 47317, "percentage": 1.37},
    {"url": "/images/launchmedium.gif", "request_count": 40689, "percentage": 1.18},
    {"url": "/htbin/cdt_main.pl", "request_count": 39873, "percentage": 1.15},
    {"url": "/shuttle/missions/sts-69/mission-sts-69.html", "request_count": 31574, "percentage": 0.91},
    {"url": "/shuttle/countdown/liftoff.html", "request_count": 29865, "percentage": 0.86},
    {"url": "/icons/menu.xbm", "request_count": 29190, "percentage": 0.84},
    {"url": "/shuttle/missions/sts-69/sts-69-patch-small.gif", "request_count": 29119, "percentage": 0.84},
    {"url": "/icons/blank.xbm", "request_count": 28852, "percentage": 0.83},
]

TRAFFIC = [
    {"hour": "00", "requests": 112450}, {"hour": "01", "requests": 98210},
    {"hour": "02", "requests": 84120}, {"hour": "03", "requests": 76540},
    {"hour": "04", "requests": 71200}, {"hour": "05", "requests": 73800},
    {"hour": "06", "requests": 85400}, {"hour": "07", "requests": 110200},
    {"hour": "08", "requests": 142300}, {"hour": "09", "requests": 178900},
    {"hour": "10", "requests": 204500}, {"hour": "11", "requests": 218400},
    {"hour": "12", "requests": 224100}, {"hour": "13", "requests": 229600},
    {"hour": "14", "requests": 235100}, {"hour": "15", "requests": 231400},
    {"hour": "16", "requests": 219800}, {"hour": "17", "requests": 198700},
    {"hour": "18", "requests": 179200}, {"hour": "19", "requests": 164300},
    {"hour": "20", "requests": 158900}, {"hour": "21", "requests": 152100},
    {"hour": "22", "requests": 141200}, {"hour": "23", "requests": 125192},
]

ERRORS = [
    {"hour": "00", "errors": 640}, {"hour": "01", "errors": 580},
    {"hour": "02", "errors": 490}, {"hour": "03", "errors": 420},
    {"hour": "04", "errors": 390}, {"hour": "05", "errors": 410},
    {"hour": "06", "errors": 510}, {"hour": "07", "errors": 690},
    {"hour": "08", "errors": 920}, {"hour": "09", "errors": 1150},
    {"hour": "10", "errors": 1340}, {"hour": "11", "errors": 1410},
    {"hour": "12", "errors": 1480}, {"hour": "13", "errors": 1520},
    {"hour": "14", "errors": 1560}, {"hour": "15", "errors": 1510},
    {"hour": "16", "errors": 1390}, {"hour": "17", "errors": 1240},
    {"hour": "18", "errors": 1110}, {"hour": "19", "errors": 1020},
    {"hour": "20", "errors": 980}, {"hour": "21", "errors": 920},
    {"hour": "22", "errors": 840}, {"hour": "23", "errors": 732},
]


def connect():
    print(f"Connecting to MongoDB: {MONGODB_URI.split('@')[-1]}")
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=10000)
    client.admin.command("ping")
    print(f"Connected. Using database '{DATABASE_NAME}'.")
    return client[DATABASE_NAME]


def replace_collection(db, name, docs, indexes=()):
    """Drop and reload a collection, then build the requested indexes."""
    coll = db[name]
    coll.drop()
    if docs:
        coll.insert_many(docs)
    for keys in indexes:
        coll.create_index(keys)
    print(f"Loaded '{name}' ({len(docs)} documents).")


def read_hdfs(path):
    """Stream a file out of the HDFS namenode container, line by line.

    Returns an empty list if Docker/HDFS is unavailable so callers can fall
    back to sample data instead of crashing.
    """
    try:
        proc = subprocess.run(
            ["docker", "exec", "namenode", "hdfs", "dfs", "-cat", path],
            capture_output=True, text=True, errors="replace",
        )
    except (FileNotFoundError, OSError) as exc:
        print(f"  (HDFS unavailable: {exc})")
        return []
    if proc.returncode != 0:
        return []
    return proc.stdout.splitlines()


def parse_sessions(limit):
    docs = []
    for line in read_hdfs("/log-analytics/results/sessions/part-00000"):
        parts = line.strip().split("\t")
        if len(parts) < 7:
            continue
        host, session_id, start, end, count, duration, total_bytes = parts[:7]
        try:
            docs.append({
                "host": host,
                "session_id": session_id,
                "start_time": start,
                "end_time": end,
                "request_count": int(count),
                "duration_seconds": int(duration),
                "total_bytes": int(total_bytes),
            })
        except ValueError:
            continue
        if len(docs) >= limit:
            break
    return docs


def parse_navigation(limit):
    docs = []
    for line in read_hdfs("/log-analytics/results/navigation/part-00000"):
        parts = line.strip().split("\t")
        if len(parts) < 3:
            continue
        src, dst, count = parts[0], parts[1], parts[2]
        if not (src.startswith("/") and dst.startswith("/")):
            continue
        try:
            docs.append({"source_url": src, "destination_url": dst, "count": int(count)})
        except ValueError:
            continue
    docs.sort(key=lambda d: d["count"], reverse=True)
    return docs[:limit]


def main():
    db = connect()

    summary = dict(SUMMARY, last_updated=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    replace_collection(db, "summary", [summary])
    replace_collection(db, "top_pages", TOP_PAGES, [[("request_count", DESCENDING)]])
    replace_collection(db, "traffic", TRAFFIC, [[("hour", ASCENDING)]])
    replace_collection(db, "error_trends", ERRORS, [[("hour", ASCENDING)]])

    sessions = parse_sessions(limit=2000)
    if not sessions:
        print("No HDFS session output found - loading representative sample data.")
        sessions = sample_data.sample_sessions()
    replace_collection(
        db, "sessions", sessions,
        indexes=[
            [("session_id", ASCENDING)],
            [("host", ASCENDING)],
            [("request_count", DESCENDING)],
            [("duration_seconds", DESCENDING)],
        ],
    )

    navigation = parse_navigation(limit=1000)
    if not navigation:
        print("No HDFS navigation output found - loading representative sample data.")
        navigation = sample_data.sample_navigation()
    replace_collection(
        db, "navigation_patterns", navigation,
        indexes=[[("count", DESCENDING)], [("source_url", ASCENDING)]],
    )

    print("Ingestion complete. Collections:", db.list_collection_names())


if __name__ == "__main__":
    main()
