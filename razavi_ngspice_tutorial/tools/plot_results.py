from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
PLOTS = ROOT / "plots"


def read_table(path: Path) -> tuple[list[str], np.ndarray]:
    with path.open("r", encoding="utf-8", errors="ignore") as f:
        header = f.readline().strip().split()
    data = np.loadtxt(path, skiprows=1)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    return header, data


def plot_file(path: Path) -> None:
    header, data = read_table(path)
    if data.shape[1] < 2:
        return

    x = data[:, 0]
    ycols = data.shape[1] - 1
    fig, axes = plt.subplots(
        ycols,
        1,
        figsize=(8, max(3.2, 2.1 * ycols)),
        dpi=140,
        sharex=True,
        squeeze=False,
    )

    for col in range(1, data.shape[1]):
        label = header[col] if col < len(header) else f"col{col}"
        ax = axes[col - 1, 0]
        ax.plot(x, data[:, col], linewidth=1.3)
        ax.set_ylabel(label)
        ax.grid(True, alpha=0.3)

    xlabel = header[0] if header else "x"
    axes[-1, 0].set_xlabel(xlabel)
    fig.suptitle(path.stem)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    plt.savefig(PLOTS / f"{path.stem}.png")
    plt.close()


def main() -> None:
    PLOTS.mkdir(exist_ok=True)
    count = 0
    for path in sorted(RESULTS.glob("*.dat")):
        plot_file(path)
        count += 1
    print(f"wrote {count} plots to {PLOTS}")


if __name__ == "__main__":
    main()
