import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

data_path = Path("latch_tran.dat")

df = pd.read_csv(
    data_path,
    sep=r"\s+",
    engine="python"
)

def clean_name(name):
    name = str(name).strip()
    name = name.replace("v(", "")
    name = name.replace(")", "")
    name = name.replace("i(", "i_")
    name = name.replace("/", "_")
    return name

df.columns = [clean_name(c) for c in df.columns]

time_col = df.columns[0]
df["time_ns"] = df[time_col] * 1e9

# =========================
# 错层显示数字波形
# =========================

signals = [
    ("d", 0, "D"),
    ("clk", 3, "CLK"),
    ("x", 6, "X"),
    ("q", 9, "Q"),
]

plt.figure(figsize=(12, 6))

for col, offset, label in signals:
    plt.plot(df["time_ns"], df[col] + offset, label=label)

plt.xlabel("Time (ns)")
plt.ylabel("Voltage + offset")
plt.title("Stacked Digital Waveforms")
plt.grid(True)
plt.legend(loc="upper right")
plt.tight_layout()
plt.show()