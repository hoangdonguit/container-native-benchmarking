# scripts/utils/analyze_phase4.py
import csv, glob, statistics

CASES = [
    ("results_case11_vu50",  "Case 11 | Bridge+20ms      | VU=50 "),
    ("results_case11_vu100", "Case 11 | Bridge+20ms      | VU=100"),
    ("results_case11_vu200", "Case 11 | Bridge+20ms      | VU=200"),
    ("results_case11_vu500", "Case 11 | Bridge+20ms      | VU=500"),
    ("results_case12_vu50",  "Case 12 | +HAProxy+20ms    | VU=50 "),
    ("results_case12_vu100", "Case 12 | +HAProxy+20ms    | VU=100"),
    ("results_case12_vu200", "Case 12 | +HAProxy+20ms    | VU=200"),
    ("results_case12_vu500", "Case 12 | +HAProxy+20ms    | VU=500"),
]

def percentile(data, p):
    if not data: return 0
    k = (len(data) - 1) * p
    f = int(k); c = min(f + 1, len(data) - 1)
    if f == c: return data[f]
    return data[f] * (c - k) + data[c] * (k - f)

print(f"{'Kịch bản':<38} | {'N':>7} | {'Mean':>6} | "
      f"{'P50':>5} | {'P95':>5} | {'P99':>6} | {'P99.9':>7} | "
      f"{'Max':>6} | {'Err%':>5}")
print("-" * 115)

for pattern, label in CASES:
    files = glob.glob(f"results/raw/{pattern}.jtl")
    if not files:
        print(f"{label:<38} | {'NO DATA':>7}")
        continue

    elapsed, errors, total = [], 0, 0
    with open(files[0]) as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows: continue
    min_ts = int(rows[0]['timeStamp'])

    for row in rows:
        ts = int(row['timeStamp'])
        if ts >= min_ts + 15000:
            elapsed.append(int(row['elapsed']))
            total += 1
            if row.get('success', 'true').lower() == 'false':
                errors += 1

    elapsed.sort()
    if not elapsed: continue

    mean = statistics.mean(elapsed)
    err_pct = errors / total * 100 if total > 0 else 0

    print(f"{label:<38} | {len(elapsed):>7} | {mean:>6.1f} | "
          f"{percentile(elapsed, 0.50):>5.0f} | "
          f"{percentile(elapsed, 0.95):>5.0f} | "
          f"{percentile(elapsed, 0.99):>6.0f} | "
          f"{percentile(elapsed, 0.999):>7.0f} | "
          f"{elapsed[-1]:>6} | {err_pct:>5.2f}")
