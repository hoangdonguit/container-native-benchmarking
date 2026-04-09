#!/usr/bin/env python3
"""Phân tích tail latency không cần pandas — chỉ stdlib."""
import csv
import glob
import statistics
from collections import defaultdict

CASES = [
    ('1c', 'Bare-metal 20k 1KB'),
    ('2c', 'Docker Host 20k 1KB'),
    ('3c', 'Docker Bridge 20k 1KB'),
]
WARMUP_MS = 35000

def percentile(sorted_data, p):
    """Tính percentile từ list đã sort (p là 0-1)."""
    if not sorted_data:
        return 0
    k = (len(sorted_data) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_data) - 1)
    if f == c:
        return sorted_data[f]
    return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)

def load_case(case_id):
    files = sorted(glob.glob(f'results/raw/results_case{case_id}_20krps_run*.jtl'))
    if not files:
        return None
    all_elapsed = []
    min_ts = None
    # Pass 1: tìm min timestamp
    for f in files:
        with open(f) as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                ts = int(row['timeStamp'])
                if min_ts is None or ts < min_ts:
                    min_ts = ts
    # Pass 2: load elapsed, loại warmup
    for f in files:
        with open(f) as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                ts = int(row['timeStamp'])
                if ts >= min_ts + WARMUP_MS:
                    all_elapsed.append(int(row['elapsed']))
    return sorted(all_elapsed)

# Load tất cả
results = {}
for case_id, label in CASES:
    data = load_case(case_id)
    if data:
        results[case_id] = (label, data)
        print(f"✓ Loaded {case_id}: {len(data)} samples")
    else:
        print(f"⚠ Không tìm thấy case {case_id}")

if not results:
    print("Không có dữ liệu để phân tích")
    exit(1)

# Bảng percentile
print()
print(f"{'Case':<25} {'Samples':>10} {'Mean':>10} {'P50':>8} {'P90':>8} {'P95':>8} {'P99':>8} {'P99.9':>9} {'P99.99':>9} {'Max':>7} {'Std':>10}")
print('-' * 120)
for case_id, (label, data) in results.items():
    n = len(data)
    mean = statistics.mean(data)
    std = statistics.stdev(data) if n > 1 else 0
    print(f"{label:<25} {n:>10} "
          f"{mean:>8.4f}ms "
          f"{percentile(data, 0.50):>6.1f}ms "
          f"{percentile(data, 0.90):>6.1f}ms "
          f"{percentile(data, 0.95):>6.1f}ms "
          f"{percentile(data, 0.99):>6.1f}ms "
          f"{percentile(data, 0.999):>7.2f}ms "
          f"{percentile(data, 0.9999):>7.2f}ms "
          f"{data[-1]:>6}ms "
          f"{std:>9.4f}")

# Delta analysis
print()
print("=" * 70)
print("DELTA ANALYSIS (so với Bare-metal)")
print("=" * 70)
if '1c' in results:
    base_data = results['1c'][1]
    base_mean = statistics.mean(base_data)
    for case_id in ['2c', '3c']:
        if case_id not in results:
            continue
        label, cur_data = results[case_id]
        cur_mean = statistics.mean(cur_data)
        print(f"\n{label}:")
        print(f"  Δ Mean:    {cur_mean - base_mean:+.4f} ms")
        print(f"  Δ P99:     {percentile(cur_data, 0.99) - percentile(base_data, 0.99):+.2f} ms")
        print(f"  Δ P99.9:   {percentile(cur_data, 0.999) - percentile(base_data, 0.999):+.2f} ms")
        print(f"  Δ P99.99:  {percentile(cur_data, 0.9999) - percentile(base_data, 0.9999):+.2f} ms")
        print(f"  Δ Max:     {cur_data[-1] - base_data[-1]:+d} ms")

# Histogram
print()
print("=" * 70)
print("HISTOGRAM (% samples per latency bucket)")
print("=" * 70)
header = f"{'Bucket':<14}"
for case_id, (label, _) in results.items():
    header += f"{label[:18]:>20}"
print(header)
print('-' * len(header))

buckets = [(0, 1), (1, 2), (2, 3), (3, 5), (5, 10), (10, 20), (20, 50), (50, 100), (100, 10**9)]
for lo, hi in buckets:
    bucket_label = f"[{lo}-{hi})ms" if hi < 10**9 else f">={lo}ms"
    line = f"{bucket_label:<14}"
    for case_id, (_, data) in results.items():
        cnt = sum(1 for x in data if lo <= x < hi)
        pct = cnt / len(data) * 100
        line += f"{pct:>18.3f}% "
    print(line)
