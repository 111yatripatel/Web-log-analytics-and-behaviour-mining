#!/usr/bin/env python3
"""
mapreduce/transition_mapper.py
Stage 2 Mapper for Aggregating URL Transitions

Reads extracted transitions from Stage 1:
  source_url \t destination_url \t count

Emits:
  source_url \t destination_url \t count
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
    for line in stdin_stream:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split('\t')
        if len(parts) < 3:
            continue
        
        source = parts[0].strip()
        dest = parts[1].strip()
        count = parts[2].strip()
        
        if source and dest:
            stdout_stream.write("%s\t%s\t%s\n" % (source, dest, count))

if __name__ == "__main__":
    main()
