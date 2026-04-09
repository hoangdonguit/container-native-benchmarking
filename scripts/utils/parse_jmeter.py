import csv
import glob
import statistics
import os

def parse_jtl(filepath):
    # Đọc trước toàn bộ data
    raw_data = []
    with open(filepath, mode='r', encoding='utf-8') as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            raw_data.append({
                'elapsed': int(row['elapsed']),
                'timeStamp': int(row['timeStamp']),
                'success': row['success'].lower() == 'true'
            })
            
    if not raw_data:
        return None

    # Tìm thời điểm bắt đầu và tính mốc cắt warmup (cộng thêm 35 giây = 35000 ms)
    start_time = min(row['timeStamp'] for row in raw_data)
    warmup_threshold = start_time + 35000 

    # Lọc bỏ 35 giây đầu tiên
    filtered_data = [row for row in raw_data if row['timeStamp'] >= warmup_threshold]

    if not filtered_data:
        print(f"[{filepath}] Cảnh báo: Không có dữ liệu nào sau 35s warmup.")
        return None

    latencies = []
    times = []
    errors = 0
    
    for row in filtered_data:
        latencies.append(row['elapsed'])
        times.append(row['timeStamp'])
        if not row['success']:
            errors += 1
            
    latencies.sort()
    n = len(latencies)
    # Thời gian chạy thực tế của phần dữ liệu đã lọc
    duration_secs = (max(times) - min(times)) / 1000.0
    
    return {
        'rps': n / duration_secs if duration_secs > 0 else 0,
        'p50': latencies[int(n * 0.50)],
        'p95': latencies[int(n * 0.95)],
        'p99': latencies[int(n * 0.99)],
        'err_rate': (errors / n) * 100
    }

files = sorted(glob.glob("results/raw/results_case3c_20krps_run*.jtl"))

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
            # Lấy 6 ký tự trước đuôi .jtl (ví dụ: "run1", "run2") để in cho đẹp
            name_display = filename.split('_')[-1].replace('.jtl', '')
            print(f"{name_display:<10} | {res['rps']:<10.1f} | {res['p50']:<6} | {res['p95']:<6} | {res['p99']:<6} | {res['err_rate']:<6.2f}")
            all_rps.append(res['rps'])
            all_p99.append(res['p99'])
            
    print("=" * 60)
    if all_rps and all_p99:
        print(f"TRUNG BÌNH | RPS: {statistics.mean(all_rps):.1f} | P99: {statistics.mean(all_p99):.1f} ms")