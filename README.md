# 🚀 Container-Native Benchmarking Lab

Đồ án: **Đánh giá Hiệu năng Mạng và Chi phí Ảo hóa trong Kiến trúc Container-Native: So sánh TCP Congestion Control, Docker Network Stack và Reverse Proxy dưới điều kiện mạng suy giảm và CPU Throttling.**

## 👥 Nhóm Thực Hiện (Nhóm 9)
* **Hoàng Xuân Đồng** (MSSV: 23520297) - *Server Setup & System Monitoring*
* **Trần Hải Đăng** (MSSV: 23520237) - *Client Load Generation & Network Emulation*
* **Giảng viên hướng dẫn:** Đặng Lê Bảo Chương

---

## 📖 Giới thiệu (Introduction)
Dự án này xây dựng một phòng thí nghiệm đo lường hiệu năng (Benchmarking Lab) trên môi trường Bare-metal thực tế. Mục tiêu cốt lõi là định lượng chính xác độ trễ (đặc biệt là Tail Latency - P99) và "chi phí tàng hình" (Overhead) của từng lớp trừu tượng trong hệ thống mạng hiện đại (Docker Network, Reverse Proxy, CPU Throttling bằng cgroups v2, TCP Congestion Control).

Dự án áp dụng chặt chẽ **Lý thuyết Hàng đợi (Queueing Theory)** và **Định luật Little ($L = \lambda \times W$)** để giải mã các hiện tượng "bùng nổ độ trễ" (Latency Explosion) và thắt cổ chai (Bottleneck) trong các hệ thống phân tán.

## 🛠 Công cụ & Công nghệ (Tech Stack)
* **Ảo hóa & Cân bằng tải:** Docker Engine, Nginx, HAProxy, cgroups v2.
* **Load Generation:** Apache JMeter, iperf3.
* **Network Emulation:** Linux Traffic Control (`tc` / `NetEm`).
* **Observability (Giám sát):** Prometheus, Grafana, cAdvisor, Node Exporter, `dstat`, `ss`, `mpstat`.
* **Phân tích dữ liệu:** Python 3 (built-in libraries để tối ưu hiệu năng xử lý hàng triệu mẫu).

---

## 📊 Ma Trận Thực Nghiệm (Experimental Matrix)
Dự án được chia thành 4 giai đoạn với 12 kịch bản (Cases) test khắt khe:

### Phase 1: Baseline Network Stack
Đo lường chi phí ảo hóa mạng qua việc bắn 20,000 RPS tĩnh.
* **Kết quả:** Overhead của Docker Bridge path tốn khoảng ~11µs so với Bare-metal, làm dịch chuyển phân phối độ trễ (Tail Latency Shift) nhưng không đáng kể ở tải thấp. Host mode gần như không có overhead mạng.

### Phase 2: TCP Congestion Control (CUBIC vs. BBR)
Ép băng thông TCP dưới điều kiện mạng lý tưởng và mạng suy giảm (Delay 50ms, Loss 2% qua NetEm).
* **Kết quả:** Ở mạng LAN sạch, cả hai đạt ~941 Mbps. Khi có Loss 2%, CUBIC sụp đổ hoàn toàn (còn ~2.37 Mbps) do cơ chế Multiplicative Decrease. Google BBR tỏa sáng khi duy trì được băng thông vượt trội (~341 Mbps) nhờ mô hình BDP (Bandwidth-Delay Product).

### Phase 3: CPU Throttling & Reverse Proxy
Sử dụng cgroups v2 giới hạn Nginx ở mức 1.0 CPU và 0.5 CPU, sau đó phân tán tải qua HAProxy.
* **Kết quả:** Khi Nginx (0.5 CPU) gánh 40,000 RPS, hệ thống bão hòa, P99 Latency vọt lên 182ms. HAProxy giải cứu thành công bằng cách chia đều tải cho 2 backend (2x 0.5 CPU), kéo P99 về lại mức ổn định (~76ms).

### Phase 4: Full Stress / Combined Stress
Kết hợp Mạng suy giảm (Delay 20ms) và Tải cao (500 Virtual Users) có và không có HAProxy.
* **Kết quả:** Khám phá ra hiện tượng "Tự giới hạn tốc độ mạng" (Network-induced Self-throttling) dựa trên Định luật Little. Delay mạng khiến giới hạn RPS của Client bị khóa ở mức ~23.5K RPS, giữ hệ thống Server không bị sụp đổ. Qua đó, đo lường được chi phí (Overhead Tax) của HAProxy là làm tăng độ trễ thêm ~6ms (P99).

---

## 📂 Cấu trúc Thư mục (Directory Structure)
Dự án sử dụng `.gitignore` để loại bỏ các file raw logs (`.jtl`, `.csv` thô, `.log`) do dung lượng lên tới hàng triệu mẫu, chỉ giữ lại mã nguồn, cấu hình và kết quả đã xử lý.

```text
container-native-benchmarking/
├── configs/
│   ├── haproxy/           # Cấu hình HAProxy Load Balancer
│   └── nginx_lb.conf      # Cấu hình dự phòng
├── scripts/
│   └── utils/             # Các script Python xử lý JTL/JSON logs
│       ├── parse_jmeter.py
│       ├── parse_phase2_final.py
│       ├── tail_analysis_nopandas.py
│       └── analyze_phase4.py
├── results/
│   └── processed/         # Kết quả CSV đã qua tổng hợp
├── test_plan_v3.jmx       # Kịch bản JMeter (Bắn tải động)
├── test_plan_v3_1kb.jmx   # Kịch bản JMeter (Bắn tải tĩnh 1KB)
├── README.md
└── .gitignore
```

---

## ⚙️ Hướng dẫn Chạy Script Phân Tích
Các script Python được thiết kế bằng thư viện tiêu chuẩn để chạy trực tiếp không cần cài thêm dependencies:

```bash
# Phân tích TCP BBR vs CUBIC (Phase 2)
python3 scripts/utils/parse_phase2_final.py

# Phân tích Tail Latency chi tiết không dùng Pandas (Phase 1 & 3)
python3 scripts/utils/tail_analysis_nopandas.py

# Phân tích Điểm bùng nổ độ trễ (Phase 4)
python3 scripts/utils/analyze_phase4.py
```
