# -*- coding: utf-8 -*-
"""make_fig_colsum.py -- per-input column sums, one marker per input mode.

Replaces the earlier figure3 that had no generator of its own (2026-10-24). The old version
plotted the modes as circles at one x position, so three of the four 4-mode values (0.99996--
0.99999) fell on top of each other and two of the six 6-mode values were identical: the figure
showed fewer markers than there are modes, which contradicts the text. Here each input mode gets
its own row, so the count is the count.

Recorded values (repository notes/eme_coupler_4modes.md, notes/eme_coupler_6modes_convergence.md;
5 um cells, single frequency 1.55 um):

    4 modes   TE0 0.99999 | TE1 0.99996 | TM0 0.99999 | hybrid 0.99889
    6 modes   TE0 0.99999 | TE1 0.99996 | TM0 0.99999 | hybrid 1 0.99991
              hybrid 2 0.99995 | near cutoff 0.99973

Usage: python make_fig_colsum.py [--out DIR]
"""
from __future__ import annotations

import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

RUNS = [
    ("(a)", 4, [("TE0", 0.99999), ("TE1", 0.99996), ("TM0", 0.99999), ("hybrid", 0.99889)]),
    ("(b)", 6, [("TE0", 0.99999), ("TE1", 0.99996), ("TM0", 0.99999),
                ("hybrid 1", 0.99991), ("hybrid 2", 0.99995), ("near cutoff", 0.99973)]),
]

STYLE = {
    "font.family": "sans-serif",
    "font.size": 8.0,
    "axes.linewidth": 0.5,
    "axes.labelsize": 8.0,
    "xtick.labelsize": 7.0,
    "ytick.labelsize": 7.0,
}


def run(out_dir: str) -> dict:
    with plt.rc_context(STYLE):
        # 5.25 in = full text width, which is where this figure is placed
        fig, axes = plt.subplots(2, 1, figsize=(5.25, 2.6), sharex=True)

        for ax, (letter, n, rows) in zip(axes, RUNS):
            ys = list(range(len(rows)))[::-1]
            ax.plot([r[1] for r in rows], ys, "o", color="#1a1a1a", markersize=4.5)
            ax.set_yticks(ys)
            ax.set_yticklabels([r[0] for r in rows])
            ax.set_ylim(-0.7, len(rows) - 0.3)
            ax.axvline(1.0, color="#9a9a9a", linewidth=0.6, linestyle=(0, (4, 3)), zorder=1)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            ax.tick_params(direction="out", length=2.5, width=0.5)
            ax.tick_params(axis="y", length=0)
            ax.text(0.012, 0.94, letter, transform=ax.transAxes, fontsize=7.5,
                    fontweight="bold", va="top", ha="left")
            ax.set_xlim(0.9986, 1.0003)
            ax.set_xticks([0.9986, 0.9990, 0.9994, 0.9998, 1.0000, 1.0002])
            ax.set_xticklabels(["0.9986", "0.9990", "0.9994", "0.9998", "1.0000", "1.0002"])

        axes[1].set_xlabel("column sum")
        fig.subplots_adjust(left=0.155, right=0.965, bottom=0.145, top=0.965, hspace=0.55)

        os.makedirs(out_dir, exist_ok=True)
        pdf = os.path.join(out_dir, "figure3.pdf")
        eps = os.path.join(out_dir, "figure3.eps")
        png = os.path.join(out_dir, "figure3.png")
        fig.savefig(pdf)
        fig.savefig(eps, format="eps")
        fig.savefig(png, dpi=300)
        plt.close(fig)

    print("pdf", pdf)
    for letter, n, rows in RUNS:
        print("  %s n=%d %s" % (letter, n, rows))
    return {"pdf": pdf, "eps": eps}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=HERE)
    run(ap.parse_args().out)


if __name__ == "__main__":
    main()
