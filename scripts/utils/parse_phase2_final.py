import json
import glob

# Danh sách ánh xạ file và tên kịch bản theo Kịch bản v3 
mapping = [
    ("tcp_case4_cubic_clean_p4.json", "Case 4: CUBIC Clean (-P 4)"),
    ("tcp_case5_bbr_clean_p4.json",  "Case 5: BBR Clean   (-P 4)"),
    ("tcp_case4b_cubic_loss_p1.json", "Case 4b: CUBIC Loss1% (-P 1)"),
    ("tcp_case5b_bbr_loss_p1.json",  "Case 5b: BBR Loss1%  (-P 1)"),
    ("tcp_case6_cubic_bad_p1.json",  "Case 6: CUBIC Bad (50ms/2%)"),
    ("tcp_case7_bbr_bad_p1.json",    "Case 7: BBR Bad   (50ms/2%)")
]

print(f"{'Kịch bản (Phase 2)':<30} | {'Băng thông':<15} | {'Retransmits'}")
print("-" * 65)

for filename, label in mapping:
    # Tìm file trong results/raw/ hoặc thư mục hiện tại [cite: 107]
    files = glob.glob(f"results/raw/{filename}") or glob.glob(filename)
    if not files:
        continue
        
    with open(files[0]) as fp:
        d = json.load(fp)
        # Tính toán throughput từ kết quả nhận được (sum_received) [cite: 341]
        bw = d['end']['sum_received']['bits_per_second'] / 1e6
        # Lấy số lượng gói tin truyền lại [cite: 342]
        retx = d['end']['sum_sent'].get('retransmits', 0)
        print(f"{label:<30} | {bw:>10.2f} Mbps | {retx:>12}")