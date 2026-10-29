# -*- coding: utf-8 -*-
"""make_fig_numbers.py -- the two effects measured here, as two dumbbells.

Replaces the ad-hoc fig-numbers figure that had no generator of its own (2026-10-24). Drawn at
its printed size (half the 5.25 in text width), in DejaVu Sans 8 pt like every other figure in
the paper, and with no text inside the axes: the numbers and the marker mapping live in the
caption (TRAINING/02_WRITING_STYLE_OPTICA.md Sec. 8).

    row 1  taper segment, TM0 -> TE1:  98.35 % with the default port settings,
                                       99.84 % with the corrected ones
    row 2  coupler key channel, TE1 -> lower-arm TE0:  99.233 % at 5 um cells,
                                       99.840 % at 1 um cells

Usage: python make_fig_numbers.py [--out DIR]
"""
from __future__ import annotations

import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

ROWS = [
    ("taper", 98.35, 99.84),
    ("coupler", 99.233, 99.840),
]

STYLE = {
    "font.family": "Arial",
    "font.size": 8.0,
    "axes.linewidth": 0.5,
    "axes.labelsize": 8.0,
    "xtick.labelsize": 7.0,
    "ytick.labelsize": 7.0,
}
C_LEFT = "#8a8a8a"
C_RIGHT = "#1a1a1a"


def run(out_dir: str) -> dict:
    with plt.rc_context(STYLE):
        # half the text width: this figure is placed at 0.52\textwidth, so drawing it at
        # 0.52 x 5.25 in means it prints at 100 %
        fig, ax = plt.subplots(figsize=(2.73, 1.55))
        ys = list(range(len(ROWS)))[::-1]
        for y, (name, a, b) in zip(ys, ROWS):
            ax.plot([a, b], [y, y], color="#c8c8c8", linewidth=1.0, zorder=1, solid_capstyle="round")
            ax.plot([a], [y], marker="o", markersize=4.0, markerfacecolor="none",
                    markeredgecolor=C_LEFT, markeredgewidth=1.0, zorder=3)
            ax.plot([b], [y], marker="o", markersize=4.0, markerfacecolor=C_RIGHT,
                    markeredgecolor=C_RIGHT, zorder=4)
        ax.set_yticks(ys)
        ax.set_yticklabels([r[0] for r in ROWS])
        ax.set_ylim(-0.6, len(ROWS) - 0.4)
        ax.set_xlim(98.0, 100.5)
        ax.set_xticks([98.0, 98.5, 99.0, 99.5, 100.0, 100.5])
        ax.set_xlabel("percent")
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.tick_params(direction="out", length=2.5, width=0.5)
        ax.tick_params(axis="y", length=0)
        fig.tight_layout(pad=0.3)

        os.makedirs(out_dir, exist_ok=True)
        pdf = os.path.join(out_dir, "fig-numbers.pdf")
        eps = os.path.join(out_dir, "fig-numbers.eps")
        png = os.path.join(out_dir, "fig-numbers.png")
        fig.savefig(pdf)
        fig.savefig(eps, format="eps")
        fig.savefig(png, dpi=300)
        plt.close(fig)

    print("pdf", pdf)
    print("rows", ROWS)
    return {"pdf": pdf, "eps": eps}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=HERE)
    run(ap.parse_args().out)


if __name__ == "__main__":
    main()
