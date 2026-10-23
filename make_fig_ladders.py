# -*- coding: utf-8 -*-
"""make_fig_ladders.py -- the two device-level ladders, drawn from recorded runs.

Nothing here is computed or fitted: every point is a number that already exists in the
repository, and the two sets are drawn side by side so that "converged within one
implementation" and "not converged across two" can be read off one figure.

    key channel          = |S(out0 <- in0)|^2, the port-basis conversion at x = 405 um
    our cell ladder      = runlogs/ (five runs; 69 / 128 / 207 / 305 / 404 EME cells)
    our mode ladder      = runlogs/run_m20_c5.md, run_m40_c5.md, run_m120_c1_m12.md
    the review's values  = tidy3d discussion #3391, quoted in the paper, not re-measured

Usage:
    python make_fig_ladders.py                # writes fig-ladders.pdf/.eps next to this file
    python make_fig_ladders.py --out <dir>    # writes into <dir> instead

The vertical axis deliberately does not start at zero: the argument rests on the last one
or two digits, and a zero-based axis would hide it.  The caption in the paper says so.
"""
from __future__ import annotations

import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- recorded readings -------------------------------------------------------
# (cell length in um, key channel) -- five runs on the original platform
OURS_CELLS = [(5.0, 0.99233), (2.5, 0.99732), (1.5, 0.99760), (1.0, 0.99840), (0.75, 0.99840)]
# (cell length, key channel) -- the review's own ladder; 0.31 um was never reproducible here
REVIEW_CELLS = [(5.0, 0.99162), (0.31, 0.99875)]
# (port modes, key channel) at 5 um cells
OURS_MODES = [(4, 0.99525), (6, 0.99233), (20, 0.98897), (40, 0.98894)]
REVIEW_MODES = [(4, 0.99525), (6, 0.99233), (20, 0.99162), (40, 0.99106)]
COINCIDING_MODES = (4, 6)  # the two implementations agree to five decimals here

STYLE = dict(
    **{
        "font.family": "serif",
        "font.size": 8.0,
        "axes.linewidth": 0.6,
        "axes.labelsize": 8.0,
        "xtick.labelsize": 7.5,
        "ytick.labelsize": 7.5,
        "legend.fontsize": 7.0,
    }
)
C_OURS = "#1a1a1a"
C_REVIEW = "#7a7a7a"


def _panel(ax, xs, ys, label, style, filled=True, offset=0.0):
    ax.plot([x * (1.0 + offset) for x in xs], ys, style, label=label,
            color=C_OURS if filled else C_REVIEW,
            marker="o" if filled else "s",
            markerfacecolor=C_OURS if filled else "none",
            markeredgecolor=C_OURS if filled else C_REVIEW,
            markersize=4.0 if filled else 4.5,
            linewidth=1.0 if filled else 0.9,
            zorder=3 if filled else 2)


def run(out_dir: str) -> dict:
    with plt.rc_context(STYLE):
        fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.6, 2.45))

        # ---------------- left: against the cell length ----------------
        _panel(axL, [c for c, _ in OURS_CELLS], [v for _, v in OURS_CELLS], "this work", "-")
        _panel(axL, [c for c, _ in REVIEW_CELLS], [v for _, v in REVIEW_CELLS],
               "the review (quoted)", "--", filled=False, offset=0.02)
        axL.annotate("quoted, not reproduced\n(962 cells > solver limit)",
                     xy=(0.31 * 1.02, 0.99875), xytext=(0.62, 0.9898),
                     fontsize=6.5, color=C_REVIEW, ha="left", va="center",
                     arrowprops=dict(arrowstyle="-", color=C_REVIEW, linewidth=0.5,
                                     shrinkA=2, shrinkB=3))
        axL.set_xscale("log")
        axL.invert_xaxis()  # finer cells to the right
        axL.set_xticks([5.0, 2.5, 1.5, 1.0, 0.75, 0.31])
        axL.set_xticklabels(["5", "2.5", "1.5", "1", "0.75", "0.31"])
        # a log axis would otherwise add its own minor labels ("4x10^0", "6x10^-1", ...),
        # which collide with the six values that matter here
        axL.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
        axL.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        axL.set_xticklabels(["5", "2.5", "1.5", "1", "0.75", "0.31"])
        axL.set_xlabel("cell length along the propagation direction (µm)  — finer →")
        axL.set_ylabel("key channel  |S(out0 ← in0)|$^2$")

        # ---------------- right: against the port-mode count ----------------
        _panel(axR, [m for m, _ in OURS_MODES], [v for _, v in OURS_MODES], "this work", "-")
        _panel(axR, [m for m, _ in REVIEW_MODES], [v for _, v in REVIEW_MODES],
               "the review (quoted)", "--", filled=False, offset=-0.03)
        for m in COINCIDING_MODES:
            axR.annotate("", xy=(m * 0.97, 0.99525 if m == 4 else 0.99233),
                         xytext=(m * 1.03, 0.99525 if m == 4 else 0.99233),
                         arrowprops=dict(arrowstyle="-", color=C_REVIEW, linewidth=0.5))
        axR.set_xticks([4, 6, 20, 40])
        axR.set_xticklabels(["4", "6", "20", "40"])
        axR.set_xlabel("port modes kept at each plane (5 µm cells)")
        axR.text(12.5, 0.99520, "coincide to five decimals", fontsize=6.5, color=C_REVIEW)
        axR.set_ylabel("key channel  |S(out0 ← in0)|$^2$")

        for ax in (axL, axR):
            ax.axhline(1.0, color="#9a9a9a", linewidth=0.6, linestyle=(0, (4, 3)), zorder=1)
            ax.set_ylim(0.9865, 1.0004)
            ax.grid(False)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            ax.tick_params(direction="out", length=2.5, width=0.6)
        axL.text(0.02, 0.94, "1.0000 = lossless", transform=axL.transAxes,
                 fontsize=6.5, color="#6a6a6a", va="top")
        axL.legend(loc="lower right", frameon=False, handlelength=2.2)
        axR.legend(loc="lower left", frameon=False, handlelength=2.2)

        fig.tight_layout(pad=0.4)
        os.makedirs(out_dir, exist_ok=True)
        pdf = os.path.join(out_dir, "fig-ladders.pdf")
        eps = os.path.join(out_dir, "fig-ladders.eps")
        png = os.path.join(out_dir, "fig-ladders.png")  # preview only; not used by LaTeX
        fig.savefig(pdf)
        fig.savefig(eps, format="eps")
        fig.savefig(png, dpi=220)
        plt.close(fig)

    record = {
        "pdf": pdf,
        "eps": eps,
        "ours_cells": OURS_CELLS,
        "review_cells": REVIEW_CELLS,
        "ours_modes": OURS_MODES,
        "review_modes": REVIEW_MODES,
    }
    for k, v in record.items():
        print("%-13s %s" % (k, v))
    return record


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=HERE, help="output directory (default: this folder)")
    a = ap.parse_args()
    run(a.out)


if __name__ == "__main__":
    main()
