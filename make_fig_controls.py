#!/usr/bin/env python3
"""make_fig_controls.py -- the falsification test: move the device, not the knobs.

Three controls in which only the physical structure changes (straight guide, guide at a
constant lateral offset, width taper) all read about 1, while the same structure read
with one numerical parameter moved reads 1e-4 to 1e-1. That contrast is the evidence
that the reading follows the numerical object, not the device.

All values are from recorded runs (second_solver/ and runlogs/); the two "parameter
moved" bars are the extremes of the amplified-bend ladders in Fig. 6.

Usage: python make_fig_controls.py [--out DIR]
"""
import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

BARS = [
    ("straight\nguide", 1.000),
    ("constant\nlateral offset", 1.000),
    ("width\ntaper", 0.999),
    ("same bend,\ncell length moved", 8.5e-5),
    ("same bend,\nbasis moved", 1.92e-1),
]
CONTROL = 3  # the first three are device-only controls

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
        fig, ax = plt.subplots(figsize=(5.25, 1.9))
        xs = range(len(BARS))
        colors = ["#3f8f5a"] * CONTROL + ["#b03a2e"] * (len(BARS) - CONTROL)
        ax.bar(xs, [v for _, v in BARS], color=colors, width=0.6)
        ax.set_yscale("log")
        ax.set_ylim(5e-5, 3.0)
        ax.axhline(1.0, color="#9a9a9a", linewidth=0.6, linestyle=(0, (4, 3)), zorder=0)
        ax.set_xticks(list(xs))
        ax.set_xticklabels([k for k, _ in BARS])
        ax.set_ylabel("column sum")
        ax.grid(False)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.tick_params(direction="out", length=2.5, width=0.6)
        fig.subplots_adjust(left=0.105, right=0.985, bottom=0.30, top=0.96)
        os.makedirs(out_dir, exist_ok=True)
        pdf = os.path.join(out_dir, "fig-controls.pdf")
        eps = os.path.join(out_dir, "fig-controls.eps")
        png = os.path.join(out_dir, "fig-controls.png")
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
