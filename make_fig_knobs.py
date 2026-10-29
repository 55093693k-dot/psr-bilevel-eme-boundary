#!/usr/bin/env python3
"""make_fig_knobs.py -- what the reading follows: cells, basis, caliber, and the bend.

Four panels, all from recorded runs:
  (a) the cell ladder on the amplified bend, at TWO basis sizes (8 and 32 port modes),
      because the ladder's span is conditional on the basis (Table 14 of the paper);
  (b) the mode ladder at a fixed 1 um cell;
  (c) the taper segment read in two port calibers;
  (d) the reading ordered by cells-per-bend N = L_bend/ell, for two lateral offsets,
      which is where the "one peak at N = 8" reading is falsified.

Sources (all in this repository):
  (a) runlogs/ for 8 modes; the 32-mode points are in notes/knob_nonseparability_20261028.md
  (b) second_solver/ampmodes_m*_p0.log
  (c) the taper re-measurement, notes/log_taper_recheck_20261006.txt
  (d) notes/knob_nonseparability_20261028.md

Usage: python make_fig_knobs.py [--out DIR]
"""
import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as ticker  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# (cells along the bend, column sum) -- one entry per basis size
CELLS_8 = [(12, 8.5e-5), (24, 6.6e-2), (60, 1.15e-2), (120, 3.8e-2)]
CELLS_32 = [(12, 2.228e-2), (24, 1.557e-1), (60, 3.489e-2), (120, 2.161e-2)]
# (port modes kept, column sum) at 1 um cells
MODES = [(2, 2.7e-3), (4, 8.0e-4), (8, 1.15e-2), (16, 1.7e-3), (32, 3.5e-2)]
# taper segment in two calibers
CALIBER = [("platform\ndefault", 0.9835), ("review\nsettings", 0.9984)]
# (N = L_bend / ell, column sum) for two lateral offsets, at a fixed 5 um cell
N_5UM = [(4, 8.5e-5), (8, 8.45e-2), (16, 5.51e-2)]
N_3UM = [(4, 1.163e-1), (8, 5.04e-2), (16, 7.8e-3)]

STYLE = {
    "font.family": "sans-serif",
    "font.size": 8.0,
    "axes.linewidth": 0.5,
    "axes.labelsize": 8.0,
    "xtick.labelsize": 7.0,
    "ytick.labelsize": 7.0,
    "legend.fontsize": 7.0,
    "legend.frameon": False,
    "figure.dpi": 200,
}


def _letter(ax, s):
    ax.text(0.015, 0.965, s, transform=ax.transAxes, fontsize=7.5,
            fontweight="bold", va="top", ha="left")


def run(out_dir: str) -> dict:
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(2, 2, figsize=(5.25, 3.9))
        axA, axB = axes[0][0], axes[0][1]
        axC, axD = axes[1][0], axes[1][1]

        # (a) two bases
        axA.semilogy([c for c, _ in CELLS_8], [v for _, v in CELLS_8], "o-",
                     color="#1a1a1a", markersize=4.0, linewidth=0.9, label="8 modes")
        axA.semilogy([c for c, _ in CELLS_32], [v for _, v in CELLS_32], "s--",
                     color="#7a7a7a", markersize=4.0, linewidth=0.9,
                     markerfacecolor="none", label="32 modes")
        axA.set_xlabel("cells along the bend")
        axA.set_ylabel("column sum")
        axA.set_xticks([12, 24, 60, 120])
        axA.legend(loc="lower right", handlelength=2.0)
        _letter(axA, "(a)")

        # (b) mode ladder
        axB.semilogy([m for m, _ in MODES], [v for _, v in MODES], "o-",
                     color="#1a1a1a", markersize=4.0, linewidth=0.9)
        axB.set_xscale("log")
        axB.set_xticks([2, 4, 8, 16, 32])
        axB.set_xticklabels(["2", "4", "8", "16", "32"])
        axB.xaxis.set_minor_locator(ticker.NullLocator())
        axB.set_xlabel("port modes kept")
        axB.set_ylabel("column sum")
        _letter(axB, "(b)")

        # (c) caliber
        xs = range(len(CALIBER))
        axC.bar(xs, [v for _, v in CALIBER], color=["#3b6ea5", "#3f8f5a"], width=0.55)
        axC.set_xticks(list(xs))
        axC.set_xticklabels([k for k, _ in CALIBER])
        axC.set_ylim(0.975, 1.0005)
        axC.set_ylabel("reading")
        axC.axhline(1.0, color="#9a9a9a", linewidth=0.6, linestyle=(0, (4, 3)))
        _letter(axC, "(c)")

        # (d) N ordering, two offsets
        axD.semilogx([n for n, _ in N_5UM], [v for _, v in N_5UM], "o-",
                     color="#1a1a1a", markersize=4.0, linewidth=0.9, label="5 $\\mu$m offset")
        axD.semilogx([n for n, _ in N_3UM], [v for _, v in N_3UM], "s--",
                     color="#7a7a7a", markersize=4.0, linewidth=0.9,
                     markerfacecolor="none", label="3 $\\mu$m offset")
        axD.set_yscale("log")
        axD.set_xticks([4, 8, 16])
        axD.set_xticklabels(["4", "8", "16"])
        axD.xaxis.set_minor_locator(ticker.NullLocator())
        axD.set_xlabel("cells per bend, $N = L_{\\rm bend}/\\ell$")
        axD.set_ylabel("column sum")
        axD.legend(loc="lower left", handlelength=2.0)
        _letter(axD, "(d)")

        for ax in (axA, axB, axC, axD):
            ax.grid(False)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            ax.tick_params(direction="out", length=2.5, width=0.6)
        fig.subplots_adjust(left=0.11, right=0.985, bottom=0.11, top=0.975,
                            wspace=0.34, hspace=0.42)
        os.makedirs(out_dir, exist_ok=True)
        pdf = os.path.join(out_dir, "fig-knobs.pdf")
        eps = os.path.join(out_dir, "fig-knobs.eps")
        png = os.path.join(out_dir, "fig-knobs.png")
        fig.savefig(pdf)
        fig.savefig(eps, format="eps")
        fig.savefig(png, dpi=300)
        plt.close(fig)

    rec = {"pdf": pdf, "eps": eps, "cells_8": CELLS_8, "cells_32": CELLS_32,
           "modes": MODES, "caliber": CALIBER, "n_5um": N_5UM, "n_3um": N_3UM}
    for k, v in rec.items():
        print("%-10s %s" % (k, v))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=HERE, help="output directory (default: this folder)")
    run(ap.parse_args().out)


if __name__ == "__main__":
    main()
