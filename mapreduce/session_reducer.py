#!/usr/bin/env python3
"""
mapreduce/session_reducer.py
Reducer for Web Sessionization Analysis

Receives partitioned & sorted records for each host from Hadoop Shuffle:
  host \t epoch \t timestamp \t url \t bytes

Groups requests per host, sorts chronologically, segments sessions using
the 30-minute (1800-second) inactivity threshold, and emits session metrics:
  host \t session_id \t start_time \t end_time \t request_count \t duration_seconds \t total_bytes
"""

import sys
import io

# Ensure UTF-8 streaming with safe fallback across all OS/locale environments
if hasattr(sys.stdin, 'buffer'):
    stdin_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
else:
    stdin_stream = sys.stdin

if hasattr(sys.stdout, 'buffer'):
    stdout_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
else:
    stdout_stream = sys.stdout

SESSION_TIMEOUT_SECONDS = 1800  # 30 minutes

def process_host_sessions(host, requests, out=None):
    """
    Given a host and all its requests [(epoch, timestamp, url, bytes), ...]:
    Sorts chronologically, partitions by 30-min inactivity gap, and outputs session summaries.
    """
    if not requests:
        return
    
    if out is None:
        out = stdout_stream
    
    requests.sort(key=lambda r: r[0])
    
    session_num = 1
    session_id = "%s_s%d" % (host, session_num)
    start_epoch, start_ts, _, start_bytes = requests[0]
    last_epoch = start_epoch
    last_ts = start_ts
    request_count = 1
    total_bytes = start_bytes
    
    for epoch, ts, url, bytes_val in requests[1:]:
        gap = epoch - last_epoch
        if gap > SESSION_TIMEOUT_SECONDS:
            duration = max(0, last_epoch - start_epoch)
            out.write("%s\t%s\t%s\t%s\t%d\t%d\t%d\n" % (
                host, session_id, start_ts, last_ts, request_count, duration, total_bytes
            ))
            
            session_num += 1
            session_id = "%s_s%d" % (host, session_num)
            start_epoch = epoch
            start_ts = ts
            last_epoch = epoch
            last_ts = ts
            request_count = 1
            total_bytes = bytes_val
        else:
            request_count += 1
            total_bytes += bytes_val
            last_epoch = epoch
            last_ts = ts
    
    duration = max(0, last_epoch - start_epoch)
    out.write("%s\t%s\t%s\t%s\t%d\t%d\t%d\n" % (
        host, session_id, start_ts, last_ts, request_count, duration, total_bytes
    ))

def main():
    current_host = None
    host_requests = []
    
    for line in stdin_stream:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) < 5:
            continue
        
        host = parts[0]
        try:
            epoch = int(parts[1])
            ts = parts[2]
            url = parts[3]
            bytes_val = int(parts[4])
        except (ValueError, IndexError):
            continue
        
        if current_host == host:
            host_requests.append((epoch, ts, url, bytes_val))
        else:
            if current_host is not None:
                process_host_sessions(current_host, host_requests)
            current_host = host
            host_requests = [(epoch, ts, url, bytes_val)]
            
    if current_host is not None:
        process_host_sessions(current_host, host_requests)

if __name__ == "__main__":
    main()
