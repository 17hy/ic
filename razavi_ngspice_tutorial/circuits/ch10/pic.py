import numpy as np
import matplotlib.pyplot as plt

A0 = 1000
fp1 = 1e3
fz  = 20e3
fp2 = 200e3

wp1 = 2 * np.pi * fp1
wz  = 2 * np.pi * fz
wp2 = 2 * np.pi * fp2

f = np.logspace(1, 7, 2000)
w = 2 * np.pi * f
s = 1j * w

T = A0 * (1 + s / wz) / ((1 + s / wp1) * (1 + s / wp2))

mag_db = 20 * np.log10(np.abs(T))
phase_deg = np.angle(T, deg=True)

idx_cross = np.argmin(np.abs(mag_db))
f_cross = f[idx_cross]

plt.figure(figsize=(8, 7))

# 上图：幅频
plt.subplot(2, 1, 1)
plt.semilogx(f, mag_db, linewidth=2)
plt.axhline(0, linestyle="--", linewidth=1)
plt.axvline(fp1, linestyle="--", linewidth=1)
plt.axvline(fz, linestyle="--", linewidth=1)
plt.axvline(fp2, linestyle="--", linewidth=1)
plt.axvline(f_cross, linestyle=":", linewidth=1)
plt.ylabel("20log10 |βH(jω)| / dB")
plt.title("Bode Plot of βH(jω)")
plt.grid(True, which="both")
plt.text(fp1, max(mag_db)-10, "fp1", ha="center")
plt.text(fz, max(mag_db)-20, "fz", ha="center")
plt.text(fp2, max(mag_db)-30, "fp2", ha="center")
plt.text(f_cross, 5, "gain crossover", ha="center")

# 下图：相频
plt.subplot(2, 1, 2)
plt.semilogx(f, phase_deg, linewidth=2)
plt.axhline(-90, linestyle="--", linewidth=1)
plt.axhline(-180, linestyle="--", linewidth=1)
plt.axvline(fp1, linestyle="--", linewidth=1)
plt.axvline(fz, linestyle="--", linewidth=1)
plt.axvline(fp2, linestyle="--", linewidth=1)
plt.axvline(f_cross, linestyle=":", linewidth=1)
plt.xlabel("Frequency / Hz")
plt.ylabel("∠βH(jω) / degree")
plt.grid(True, which="both")

plt.tight_layout()
plt.show()