#!/usr/bin/env python3
"""
mapreduce/navigation_aggregate_reducer.py
Stage 2 Reducer for Aggregating URL Transitions

Receives grouped transitions from Hadoop Shuffle:
  source_url \t destination_url \t count

Aggregates transition frequencies and outputs:
  source_url \t destination_url \t total_count
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

def main():
    current_key = None
    current_count = 0
    
    for line in stdin_stream:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) < 3:
            continue
        
        source = parts[0]
        dest = parts[1]
        try:
            count = int(parts[2])
        except ValueError:
            continue
        
        key = (source, dest)
        if current_key == key:
            current_count += count
        else:
            if current_key is not None:
                stdout_stream.write("%s\t%s\t%d\n" % (current_key[0], current_key[1], current_count))
            current_key = key
            current_count = count
            
    if current_key is not None:
        stdout_stream.write("%s\t%s\t%d\n" % (current_key[0], current_key[1], current_count))

if __name__ == "__main__":
    main()
