#!/usr/bin/env python3
"""
mapreduce/navigation_reducer.py
Stage 1 Reducer for URL Navigation & Transition Mining

Receives partitioned and grouped records for each host from Hadoop Shuffle:
  host \t epoch \t url

Sorts requests chronologically per host, tracks session continuity using the 30-minute
(1800s) timeout, and emits consecutive page transitions within each session:
  source_url \t destination_url \t 1
"""

import sys
import io

if hasattr(sys.stdin, 'buffer'):
    stdin_stream = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')
else:
    stdin_stream = sys.stdin

if hasattr(sys.stdout, 'buffer'):
    stdout_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
else:
    stdout_stream = sys.stdout

SESSION_TIMEOUT_SECONDS = 1800  # 30 minutes

def process_host_transitions(host, requests, out=None):
    """
    Sorts requests chronologically and emits consecutive URL transitions
    whenever requests occur within the same 30-minute session window.
    """
    if len(requests) < 2:
        return
    
    if out is None:
        out = stdout_stream
    
    requests.sort(key=lambda r: r[0])
    
    last_epoch, prev_url = requests[0]
    
    for epoch, url in requests[1:]:
        gap = epoch - last_epoch
        if gap <= SESSION_TIMEOUT_SECONDS:
            # Valid transition within the same active session
            if prev_url and url and prev_url != url:
                out.write("%s\t%s\t1\n" % (prev_url, url))
        
        last_epoch = epoch
        prev_url = url

def main():
    current_host = None
    host_requests = []
    
    for line in stdin_stream:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) < 3:
            continue
        
        host = parts[0]
        try:
            epoch = int(parts[1])
            url = parts[2]
        except (ValueError, IndexError):
            continue
        
        if current_host == host:
            host_requests.append((epoch, url))
        else:
            if current_host is not None:
                process_host_transitions(current_host, host_requests)
            current_host = host
            host_requests = [(epoch, url)]
            
    if current_host is not None:
        process_host_transitions(current_host, host_requests)

if __name__ == "__main__":
    main()
