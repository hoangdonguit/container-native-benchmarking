import csv, os
import matplotlib.pyplot as plt

WARMUP_MS = 35000
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../results/raw')

def percentile(data, p):
    if not data: return 0
    k = (len(data) - 1) * p
    f = int(k); c = min(f + 1, len(data) - 1)
    if f == c: return data[f]
    return data[f] * (c - k) + data[c] * (k - f)

def parse_jtl(filepath):
    elapsed = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows: return []
    min_ts = min(int(r['timeStamp']) for r in rows)
    for row in rows:
        if int(row['timeStamp']) >= min_ts + WARMUP_MS:
            elapsed.append(int(row['elapsed']))
    elapsed.sort()
    return elapsed

vus = [50, 100, 200, 500]
p99_11, p999_11, rps_11 = [], [], []
p99_12, p999_12, rps_12 = [], [], []

dur = (120000 - WARMUP_MS) / 1000

for vu in vus:
    d11 = parse_jtl(f"{BASE}/results_case11_vu{vu}.jtl")
    d12 = parse_jtl(f"{BASE}/results_case12_vu{vu}.jtl")
    p99_11.append(percentile(d11, 0.99))
    p999_11.append(percentile(d11, 0.999))
    p99_12.append(percentile(d12, 0.99))
    p999_12.append(percentile(d12, 0.999))
    rps_11.append(round(len(d11) / dur))
    rps_12.append(round(len(d12) / dur))

print("=== DEBUG ===")
for i, vu in enumerate(vus):
    print(f"VU={vu}: C11 P99={p99_11[i]:.1f} P99.9={p999_11[i]:.1f} | C12 P99={p99_12[i]:.1f} P99.9={p999_12[i]:.1f}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle('P99 Latency vs Virtual Users — Phase 4 (Hockey-Stick Curve)', fontsize=13, y=1.01)

ax1 = axes[0]
ax1.plot(vus, p99_11,  'o-',  color='#378add', lw=2, label='Case 11 — P99')
ax1.plot(vus, p999_11, 's--', color='#7f77dd', lw=2, label='Case 11 — P99.9')
ax1.plot(vus, p99_12,  'o-',  color='#1d9e75', lw=2, label='Case 12 — P99')
ax1.plot(vus, p999_12, 's--', color='#5dcaa5', lw=2, label='Case 12 — P99.9')

# Knee point Case 11 P99.9: gãy mạnh tại VU=100
ax1.annotate(
    'Case 11 P99.9\nknee point (~VU=100)',
    xy=(100, p999_11[1]),
    xytext=(130, p999_11[1] - 10),
    fontsize=8, color='#534ab7',
    arrowprops=dict(arrowstyle='->', color='#534ab7', lw=1.2)
)
ax1.axvline(x=100, color='#7f77dd', linestyle=':', alpha=0.45, lw=1)

# Knee point Case 12 P99.9: bắt đầu tăng sau VU=200
ax1.annotate(
    'Case 12 P99.9\nknee point (~VU=200)',
    xy=(200, p999_12[2]),
    xytext=(260, p999_12[2] + 4),
    fontsize=8, color='#0f6e56',
    arrowprops=dict(arrowstyle='->', color='#0f6e56', lw=1.2)
)
ax1.axvline(x=200, color='#5dcaa5', linestyle=':', alpha=0.45, lw=1)

# Ghi chú Case 11 P99 phẳng
ax1.text(
    310, min(p99_11) - 1.8,
    'Case 11 P99 phẳng:\nthroughput tự giới hạn\ndo delay 20ms',
    fontsize=7.5, color='#185fa5', style='italic',
    bbox=dict(boxstyle='round,pad=0.35', fc='#e6f1fb', ec='#b5d4f4', lw=0.8)
)

ax1.set_xlabel('Virtual Users (VU)', fontsize=11)
ax1.set_ylabel('Latency (ms)', fontsize=11)
ax1.set_title('P99 & P99.9 Latency vs Load', fontsize=11)
ax1.legend(fontsize=9, loc='upper left')
ax1.grid(True, alpha=0.25)

ax2 = axes[1]
ax2.plot(rps_11, p99_11, 'o-', color='#378add', lw=2, label='Case 11 (1×1.0CPU)')
ax2.plot(rps_12, p99_12, 'o-', color='#1d9e75', lw=2, label='Case 12 (2×0.5CPU+HAProxy)')

for i, vu in enumerate(vus):
    ax2.annotate(f'VU={vu}', (rps_11[i], p99_11[i]),
                 textcoords='offset points', xytext=(5, 4),
                 fontsize=7.5, color='#185fa5')
    ax2.annotate(f'VU={vu}', (rps_12[i], p99_12[i]),
                 textcoords='offset points', xytext=(5, -11),
                 fontsize=7.5, color='#0f6e56')

ax2.set_xlabel('Throughput (RPS)', fontsize=11)
ax2.set_ylabel('P99 Latency (ms)', fontsize=11)
ax2.set_title('P99 Latency vs Throughput', fontsize=11)
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.25)

plt.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../results/hockey_stick_phase4.png')
plt.savefig(out, dpi=150, bbox_inches='tight')
print(f"Saved: {out}")
