#!/usr/bin/env python3
"""make_fig_methods.py -- one nominal structure read three ways.

This figure was previously placed without a generator in the repository, so its
lettering was in a different family from every other figure. Rebuilt here from the
same three recorded readings (Table "three" in the manuscript): EME with straight
cells 0.055, varFDTD with a 2.5-D effective index 0.765, and the exact bent-waveguide
FDE solve 1.000. Nothing is recomputed -- the numbers are the ones the runs produced.

Usage: python make_fig_methods.py [--out DIR]
"""
import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

BARS = [
    ("EME\n(straight cells)", 0.055),
    ("varFDTD\n(2.5-D index)", 0.765),
    ("FDE\n(bent, exact)", 1.000),
]

STYLE = {
    "font.family": "Arial",
    "font.size": 8.0,
    "axes.linewidth": 0.5,
    "axes.labelsize": 8.0,
    "xtick.labelsize": 6.5,
    "ytick.labelsize": 7.0,
    "figure.dpi": 200,
}


def run(out_dir: str) -> dict:
    with plt.rc_context(STYLE):
        fig, ax = plt.subplots(figsize=(2.73, 2.09))
        xs = range(len(BARS))
        ax.bar(xs, [v for _, v in BARS], color=["#b03a2e", "#2e6f9e", "#3f8f5a"], width=0.62)
        ax.axhline(1.0, color="#9a9a9a", linewidth=0.6, linestyle=(0, (4, 3)), zorder=0)
        ax.set_ylim(0.0, 1.06)
        ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
        ax.yaxis.grid(True, color="#dcdcdc", linewidth=0.4, zorder=0)
        ax.set_axisbelow(True)
        ax.set_xticks(list(xs))
        ax.set_xticklabels([k for k, _ in BARS])
        ax.set_ylabel("column sum")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(direction="out", length=2.5, width=0.5)
        ax.tick_params(axis="x", length=0)
        fig.subplots_adjust(left=0.20, right=0.97, bottom=0.235, top=0.965)
        os.makedirs(out_dir, exist_ok=True)
        pdf = os.path.join(out_dir, "fig-methods.pdf")
        eps = os.path.join(out_dir, "fig-methods.eps")
        png = os.path.join(out_dir, "fig-methods.png")
        fig.savefig(pdf)
        fig.savefig(eps, format="eps")
        fig.savefig(png, dpi=300)
        plt.close(fig)

    rec = {"pdf": pdf, "eps": eps, "bars": BARS}
    for k, v in rec.items():
        print("%-6s %s" % (k, v))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=HERE, help="output directory (default: this folder)")
    run(ap.parse_args().out)


if __name__ == "__main__":
    main()
