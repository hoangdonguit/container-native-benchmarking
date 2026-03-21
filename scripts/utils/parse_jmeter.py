import csv
import glob
import statistics
import os

def parse_jtl(filepath):
    latencies = []
    times = []
    errors = 0
    
    with open(filepath, mode='r', encoding='utf-8') as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            latencies.append(int(row['elapsed']))
            times.append(int(row['timeStamp']))
            if row['success'].lower() == 'false':
                errors += 1
                
    if not latencies:
        return None
        
    latencies.sort()
    n = len(latencies)
    duration_secs = (max(times) - min(times)) / 1000.0
    
    return {
        'rps': n / duration_secs,
        'p50': latencies[int(n * 0.50)],
        'p95': latencies[int(n * 0.95)],
        'p99': latencies[int(n * 0.99)],
        'err_rate': (errors / n) * 100
    }

# Tìm tất cả các file jtl của Case 1
files = sorted(glob.glob("results/raw/results_case1_100vu_run*.jtl"))

if not files:
    print("Chưa tìm thấy file .jtl nào. Hãy chắc chắn bạn đã chép file Đăng gửi vào results/raw/")
else:
    print(f"{'Run':<10} | {'RPS':<10} | {'P50':<6} | {'P95':<6} | {'P99':<6} | {'Err%':<6}")
    print("-" * 60)
    
    all_p99, all_rps = [], []
    
    for f in files:
        res = parse_jtl(f)
        if res:
            filename = os.path.basename(f)
            print(f"{filename[-10:-4]:<10} | {res['rps']:<10.1f} | {res['p50']:<6} | {res['p95']:<6} | {res['p99']:<6} | {res['err_rate']:<6.2f}")
            all_rps.append(res['rps'])
            all_p99.append(res['p99'])
            
    print("=" * 60)
    print(f"TRUNG BÌNH | RPS: {statistics.mean(all_rps):.1f} | P99: {statistics.mean(all_p99):.1f} ms")