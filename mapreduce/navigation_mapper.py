#!/usr/bin/env python3
"""
mapreduce/navigation_mapper.py
Stage 1 Mapper for URL Navigation & Transition Mining

Compatible with Python 3.4+.
Reads normalized TSV log records from stdin:
  host \t timestamp \t method \t url \t protocol \t status \t response_bytes

Emits:
  host \t epoch \t url
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

MONTHS = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

def parse_epoch(ts_str):
    """Fast conversion of timestamp string to epoch seconds."""
    try:
        day = int(ts_str[0:2])
        month = MONTHS[ts_str[3:6]]
        year = int(ts_str[7:11])
        hour = int(ts_str[12:14])
        minute = int(ts_str[15:17])
        second = int(ts_str[18:20])
        days_before_month = [0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        total_days = (year - 1970) * 365 + ((year - 1969) // 4) + days_before_month[month] + (day - 1)
        return total_days * 86400 + hour * 3600 + minute * 60 + second
    except Exception:
        return 0

def main():
    for line in stdin_stream:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) < 5:
            continue
        
        host = parts[0].strip()
        ts_str = parts[1].strip()
        url = parts[3].strip()
        
        if not host or not url:
            continue
        
        epoch = parse_epoch(ts_str)
        stdout_stream.write("%s\t%d\t%s\n" % (host, epoch, url))

if __name__ == "__main__":
    main()
