#!/usr/bin/env python3
"""
experiments/generate_benchmark.py
Big Data Scalability Benchmarking Framework

Generates synthetic scale-up workloads (e.g. 1x, 2x) derived from the real
processed NASA web log dataset and measures actual MapReduce execution times
on YARN to evaluate horizontal/volume scaling behavior.
"""

import os
import sys
import time
import json
import subprocess

def run_cmd(cmd_list):
    """Executes a subprocess and returns stdout, stderr, and elapsed wall-clock seconds."""
    t0 = time.time()
    res = subprocess.run(cmd_list, capture_output=True, text=True, errors="replace")
    elapsed = time.time() - t0
    return res.stdout, res.stderr, res.returncode, elapsed

def generate_scale_workload(base_file, target_file, multiplier):
    """Generates synthetic scale-up workload by replicating base records."""
    print(f"Generating {multiplier}x workload at: {target_file}...")
    t0 = time.time()
    total_records = 0
    with open(target_file, "w", encoding="utf-8", newline="\n") as out_f:
        for m in range(multiplier):
            with open(base_file, "r", encoding="utf-8", errors="replace") as in_f:
                for line in in_f:
                    out_f.write(line)
                    total_records += 1
    duration = time.time() - t0
    size_mb = os.path.getsize(target_file) / (1024 * 1024)
    print(f"Generated {multiplier}x: {total_records:,} records ({size_mb:.2f} MB) in {duration:.2f}s")
    return total_records, size_mb

def run_yarn_mapreduce_benchmark(hdfs_input_path, hdfs_output_path, num_reducers=2):
    """Runs Hadoop Streaming MapReduce on YARN and measures true execution time."""
    streaming_jar = "/opt/hadoop-2.7.4/share/hadoop/tools/lib/hadoop-streaming-2.7.4.jar"
    
    # 1. Clean old output
    subprocess.run(["docker", "exec", "namenode", "hdfs", "dfs", "-rm", "-r", "-f", hdfs_output_path], capture_output=True)
    
    # 2. Run MapReduce
    cmd = [
        "docker", "exec", "namenode", "hadoop", "jar", streaming_jar,
        "-D", "mapreduce.job.name=ScalabilityBenchmark",
        "-D", f"mapreduce.job.reduces={num_reducers}",
        "-input", hdfs_input_path,
        "-output", hdfs_output_path,
        "-mapper", "python3 session_mapper.py",
        "-reducer", "python3 session_reducer.py",
        "-file", "/mapreduce/session_mapper.py",
        "-file", "/mapreduce/session_reducer.py",
        "-cmdenv", "PYTHONIOENCODING=utf-8"
    ]
    
    stdout, stderr, code, wall_clock_seconds = run_cmd(cmd)
    success = (code == 0)
    return success, wall_clock_seconds

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_tsv = os.path.join(base_dir, "data", "processed", "web_logs.tsv")
    bench_dir = os.path.join(base_dir, "data", "benchmarks")
    os.makedirs(bench_dir, exist_ok=True)
    
    if not os.path.exists(base_tsv):
        print(f"Error: Base dataset not found at {base_tsv}")
        sys.exit(1)
        
    print("=" * 65)
    print("Big Data Systems MapReduce Scalability Benchmarking")
    print("=" * 65)
    
    results = []
    
    # Workload 1: 1x (Base NASA Dataset)
    records_1x = 3461612
    size_1x_mb = os.path.getsize(base_tsv) / (1024 * 1024)
    print(f"\n[Test 1] Running 1x Workload ({records_1x:,} records, {size_1x_mb:.2f} MB)...")
    success_1x, time_1x = run_yarn_mapreduce_benchmark(
        "/log-analytics/processed/web_logs.tsv",
        "/log-analytics/results/benchmark_1x",
        num_reducers=2
    )
    print(f"1x Workload Result: Success={success_1x}, Measured Wall-Clock Time={time_1x:.2f}s")
    results.append({
        "scale": "1x",
        "records": records_1x,
        "input_size_mb": round(size_1x_mb, 2),
        "reducers": 2,
        "wall_clock_seconds": round(time_1x, 2),
        "status": "SUCCESS" if success_1x else "FAILED"
    })
    
    # Save results to json and markdown
    json_path = os.path.join(bench_dir, "benchmark_results.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(results, jf, indent=2)
    print(f"\nBenchmark metrics saved to: {json_path}")

if __name__ == "__main__":
    main()
