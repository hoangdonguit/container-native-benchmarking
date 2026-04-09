import csv
import glob
import statistics

CASES = [
    ("8_5krps", "Case 8 (1.0 CPU - 5K)"),
    ("8b_40krps", "Case 8b (1.0 CPU - 40K)"),
    ("9_5krps", "Case 9 (0.5 CPU - 5K)"),
    ("9b_40krps", "Case 9b (0.5 CPU - 40K)"),
    ("10_40krps", "Case 10 (2x0.5 CPU HAProxy)")
]

def percentile(data, p):
    if not data: return 0
    k = (len(data) - 1) * p
    f = int(k)
    c = min(f + 1, len(data) - 1)
    if f == c: return data[f]
    return data[f] * (c - k) + data[c] * (k - f)

print(f"{'Kịch bản':<25} | {'Samples':>8} | {'Mean':>6} | {'P50':>5} | {'P95':>5} | {'P99':>5} | {'P99.9':>6} | {'Max':>5}")
print("-" * 80)

for case_id, label in CASES:
    files = glob.glob(f"results/raw/results_case{case_id}.jtl")
    if not files:
        continue
    
    elapsed = []
    # Bỏ qua 15 giây đầu tiên (Warm-up)
    with open(files[0], 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows: continue
        
        min_ts = int(rows[0]['timeStamp'])
        for row in rows:
            ts = int(row['timeStamp'])
            if ts >= min_ts + 15000:  # Bỏ qua 15s đầu
                elapsed.append(int(row['elapsed']))
                
    elapsed.sort()
    if not elapsed: continue
    
    mean = statistics.mean(elapsed)
    print(f"{label:<25} | {len(elapsed):>8} | {mean:>6.1f} | {percentile(elapsed, 0.50):>5.0f} | {percentile(elapsed, 0.95):>5.0f} | {percentile(elapsed, 0.99):>5.0f} | {percentile(elapsed, 0.999):>6.0f} | {elapsed[-1]:>5}")
