#!/usr/bin/env python3
"""
preprocessing/parser.py
NASA HTTP Log Parser and TSV Normalizer

Streams raw NASA HTTP logs line-by-line, normalizes fields into a clean
tab-delimited (TSV) format without headers for HDFS/MapReduce/Hive ingestion,
and produces an execution statistics report.
"""

import os
import re
import sys
import time

# Regex pattern matching Common Log Format
LOG_PATTERN = re.compile(
    r'^(\S+)'                  # 1: Host
    r'\s+-\s+-'                # Identd and User ID placeholder (- -)
    r'\s+\[([^\]]+)\]'         # 2: Timestamp [DD/Mon/YYYY:HH:MM:SS TZ]
    r'\s+"(.*?)"'              # 3: HTTP Request ("METHOD URL PROTOCOL")
    r'\s+(\d{3}|\S+)'          # 4: Status code
    r'\s+(\d+|\S+)$'           # 5: Bytes (- or numeric)
)

def parse_request(request_str):
    """Safely extracts method, url, and protocol from request string."""
    parts = request_str.strip().split()
    if len(parts) >= 3:
        method = parts[0]
        protocol = parts[-1]
        url = " ".join(parts[1:-1])
    elif len(parts) == 2:
        method = parts[0]
        url = parts[1]
        protocol = "HTTP/1.0"
    elif len(parts) == 1:
        method = "GET"
        url = parts[0]
        protocol = "HTTP/1.0"
    else:
        method = "-"
        url = "-"
        protocol = "-"
    
    # Clean tabs and newlines from fields to preserve valid TSV columns
    method = method.replace("\t", " ").replace("\n", "").replace("\r", "")
    url = url.replace("\t", " ").replace("\n", "").replace("\r", "")
    protocol = protocol.replace("\t", " ").replace("\n", "").replace("\r", "")
    return method, url, protocol

def parse_line(line):
    """
    Parses a single log line.
    Returns (True, [host, timestamp, method, url, protocol, status, bytes]) if valid,
    or (False, error_reason) if invalid.
    """
    line = line.strip()
    if not line:
        return False, "Empty line"
    
    match = LOG_PATTERN.match(line)
    if not match:
        return False, "Regex format mismatch"
    
    host, timestamp, request_str, status_str, bytes_str = match.groups()
    
    # Validate and clean host and timestamp
    host = host.replace("\t", " ").strip()
    timestamp = timestamp.replace("\t", " ").strip()
    
    # Parse request
    method, url, protocol = parse_request(request_str)
    
    # Validate status code
    try:
        status = int(status_str)
    except ValueError:
        return False, f"Invalid status code: {status_str}"
    
    # Validate response bytes (- or non-numeric converted to 0)
    try:
        response_bytes = int(bytes_str)
    except ValueError:
        response_bytes = 0
    
    return True, (host, timestamp, method, url, protocol, str(status), str(response_bytes))

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    processed_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    input_files = [
        os.path.join(raw_dir, "NASA_access_log_Jul95"),
        os.path.join(raw_dir, "NASA_access_log_Aug95")
    ]
    
    output_tsv = os.path.join(processed_dir, "web_logs.tsv")
    report_file = os.path.join(processed_dir, "processing_report.txt")
    
    print("=" * 60)
    print("NASA Web Log Preprocessing Pipeline")
    print(f"Target Output: {output_tsv}")
    print("=" * 60)
    
    start_time = time.time()
    total_lines = 0
    valid_records = 0
    invalid_records = 0
    error_counts = {}
    
    with open(output_tsv, "w", encoding="utf-8", newline="\n") as out_f:
        for file_path in input_files:
            if not os.path.exists(file_path):
                print(f"[WARNING] Input file not found: {file_path}")
                continue
            
            print(f"Processing: {os.path.basename(file_path)}...")
            file_lines = 0
            # Use latin-1 to safely read raw 1995 logs without decoding errors
            with open(file_path, "r", encoding="latin-1", errors="replace") as in_f:
                for line in in_f:
                    total_lines += 1
                    file_lines += 1
                    
                    is_valid, result = parse_line(line)
                    if is_valid:
                        out_f.write("\t".join(result) + "\n")
                        valid_records += 1
                    else:
                        invalid_records += 1
                        error_counts[result] = error_counts.get(result, 0) + 1
                    
                    if file_lines % 250000 == 0:
                        print(f"  Processed {file_lines:,} lines from current file (Total Valid: {valid_records:,})...")
            
            print(f"Completed {os.path.basename(file_path)}: {file_lines:,} lines.")
    
    duration = time.time() - start_time
    
    # Generate Processing Report
    report_content = [
        "NASA HTTP Log Preprocessing Report",
        "=" * 40,
        f"Execution Time: {duration:.2f} seconds",
        f"Input Files:",
    ]
    for f in input_files:
        exists = os.path.exists(f)
        size_mb = os.path.getsize(f) / (1024 * 1024) if exists else 0
        report_content.append(f"  - {os.path.basename(f)} ({size_mb:.2f} MB)")
    
    report_content.extend([
        f"Total Input Lines:   {total_lines:,}",
        f"Valid Output Records:{valid_records:,} ({(valid_records / total_lines * 100 if total_lines else 0):.2f}%)",
        f"Invalid Records:     {invalid_records:,} ({(invalid_records / total_lines * 100 if total_lines else 0):.2f}%)",
        f"Output TSV:          {output_tsv}",
        f"Output TSV Size:     {os.path.getsize(output_tsv) / (1024 * 1024):.2f} MB",
        "",
        "Parsing Error Summary:",
    ])
    for err, count in error_counts.items():
        report_content.append(f"  - {err}: {count:,}")
    
    report_text = "\n".join(report_content) + "\n"
    with open(report_file, "w", encoding="utf-8") as rf:
        rf.write(report_text)
    
    print("\n" + report_text)
    print("Preprocessing completed successfully.")

if __name__ == "__main__":
    main()
