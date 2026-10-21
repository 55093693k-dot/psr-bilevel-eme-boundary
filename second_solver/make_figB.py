# -*- coding: utf-8 -*-
"""make_figB.py — Figure B: the reading moves when the numerical knob moves, not when the device does.

All numbers are from the runs recorded here (second_solver/PROBE_FINDINGS_20261007.md).
Labels are English so the figure is journal-ready without a CJK font.
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figures_pilot")
os.makedirs(OUT, exist_ok=True)

# ---- recorded data ----------------------------------------------------------
cell_len = [5.0, 2.5, 1.0, 0.5]                       # µm  (amplified bend, 20 µm)
cell_cells = [12, 24, 60, 120]                        # = 60 µm / cell_len  (monotonic: finer ->)
cell_col = [0.000085, 0.066112, 0.011501, 0.037840]   # column sum
modes = [2, 4, 8, 16, 32]                             # modes kept (cells fixed 1 µm)
mode_col = [0.002661, 0.000801, 0.011501, 0.001680, 0.034885]
calib_lbl = ["platform\ndefault", "review\nsettings"]
calib_v = [0.9835, 0.9984]

fig, ax = plt.subplots(1, 3, figsize=(7.2, 2.7))

# (a) cell clause -------------------------------------------------------------
ax[0].semilogy(cell_cells, cell_col, "o-", color="C3", lw=1.2, ms=4)
ax[0].set_xlabel("cells along the bend  — finer $\\rightarrow$")
ax[0].set_ylabel("column sum")
ax[0].set_xticks(cell_cells)
ax[0].tick_params(axis="x", labelsize=7)
# panel labels only; all other text goes in the caption
ax[0].set_title("(a)", fontsize=8)
ax[0].grid(True, which="both", alpha=0.25, lw=0.5)

# (b) basis clause ------------------------------------------------------------
ax[1].semilogy(modes, mode_col, "s-", color="C0", lw=1.2, ms=4)
ax[1].set_xlabel("modes kept")
ax[1].set_ylabel("column sum")
ax[1].set_title("(b)", fontsize=8)
ax[1].grid(True, which="both", alpha=0.25, lw=0.5)

# (c) caliber clause ----------------------------------------------------------
ax[2].bar(range(2), calib_v, color="C2", width=0.55)
ax[2].set_xticks(range(2))
ax[2].set_xticklabels(calib_lbl, fontsize=7)
ax[2].set_ylim(0.975, 1.005)
ax[2].set_title("(c)", fontsize=8)
ax[2].grid(True, axis="y", alpha=0.25, lw=0.5)

# reference line only (its meaning is stated in the caption) -------------------
for a in (ax[0], ax[1]):
    a.axhline(1.0, color="0.45", lw=0.9, ls="--")

fig.tight_layout(pad=0.6)
png = os.path.join(OUT, "figB_reading_vs_knob.png")
pdf = os.path.join(OUT, "figB_reading_vs_knob.pdf")
fig.savefig(png, dpi=300)
fig.savefig(pdf)
print("WROTE", png)
print("WROTE", pdf)
