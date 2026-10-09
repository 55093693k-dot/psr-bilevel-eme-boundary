# -*- coding: utf-8 -*-
"""make_figC.py — Figure C: one nominal structure, three methods, three readings.

Same minimal S-bend (5 µm offset over 100 µm). Recorded runs: EME column sum ~0.055 (PROBE record);
varFDTD converged key channel ~0.765; FDE bent-waveguide solve says the bend is lossless (~1.000).
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figures_pilot")
os.makedirs(OUT, exist_ok=True)

labels = ["EME\n(straight cells)", "varFDTD\n(2.5D effective index)", "FDE bent mode\n(exact)"]
vals = [0.055, 0.765, 1.000]
colors = ["C3", "C0", "C2"]

fig, ax = plt.subplots(figsize=(3.4, 2.6))
ax.bar(range(3), vals, color=colors, width=0.6)
ax.set_xticks(range(3))
ax.set_xticklabels(labels, fontsize=7)
ax.set_ylabel("reading for the same S-bend")
ax.set_ylim(0, 1.15)
ax.grid(True, axis="y", alpha=0.25, lw=0.5)
ax.axhline(1.0, color="0.45", lw=0.9, ls="--")

fig.tight_layout(pad=0.5)
fig.savefig(os.path.join(OUT, "figC_three_methods.png"), dpi=300)
fig.savefig(os.path.join(OUT, "figC_three_methods.pdf"))
print("WROTE figC_three_methods.png / .pdf")
