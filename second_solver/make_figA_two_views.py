# -*- coding: utf-8 -*-
"""make_figA_two_views.py — Figure A: the structure, two views, both official exports.

Both panels come from tidy3d.Simulation.plot_structures (the solver's own
renderer), so the figure is solver-exported rather than hand-drawn:
  (a) top view            -- the in-plane S-bend
  (b) cross-section       -- the layer stack the guide sits on

No text is added beyond the two panel letters; the description lives in the
figure caption. (An earlier attempt used a Lumerical layout export as the
second panel; it came out on an opaque black backdrop and badly framed, so it
is not used.)
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import tidy3d as td  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figures_pilot")
os.makedirs(OUT, exist_ok=True)

L_TOT, L_BEND, L_STR, W, DY = 200.0, 100.0, 50.0, 0.5, 5.0


def sbend_vertices(n: int = 401) -> np.ndarray:
    x = np.linspace(0.0, L_TOT, n)
    y = np.zeros_like(x)
    inb = (x > L_STR) & (x < L_STR + L_BEND)
    y[inb] = DY * (1 - np.cos(np.pi * (x[inb] - L_STR) / L_BEND)) / 2.0
    y[x >= L_STR + L_BEND] = DY
    th = np.arctan(np.gradient(y, x))
    nx, ny = -np.sin(th), np.cos(th)
    top = np.vstack([x + nx * W / 2, y + ny * W / 2]).T
    bot = np.vstack([x - nx * W / 2, y - ny * W / 2]).T
    return np.vstack([top, bot[::-1]])


def build() -> td.Simulation:
    strip = td.Structure(
        geometry=td.PolySlab(vertices=sbend_vertices(), axis=2, slab_bounds=(0.0, 0.22)),
        medium=td.Medium(permittivity=12.25),           # Si
    )
    oxide = td.Structure(
        geometry=td.Box(center=(L_TOT / 2, DY / 2, -0.5), size=(L_TOT, DY + 6.0, 1.0)),
        medium=td.Medium(permittivity=2.085),           # SiO2
    )
    return td.Simulation(
        size=(L_TOT + 8.0, DY + 6.0, 3.0), center=(L_TOT / 2, DY / 2, 0.0),
        grid_spec=td.GridSpec.auto(wavelength=1.55), run_time=1e-13,
        structures=[oxide, strip],
    )


def main() -> None:
    sim = build()
    fig, ax = plt.subplots(2, 1, figsize=(6.4, 4.6))

    sim.plot_structures(z=0.11, ax=ax[0])
    ax[0].set_title("(a)", fontsize=8)

    sim.plot_structures(x=L_STR + L_BEND / 2.0, ax=ax[1])
    ax[1].set_title("(b)", fontsize=8)

    fig.tight_layout(pad=0.4)
    png = os.path.join(OUT, "figA_structure_two_views.png")
    fig.savefig(png, dpi=300)
    fig.savefig(os.path.join(OUT, "figA_structure_two_views.pdf"))
    print("WROTE", png)


if __name__ == "__main__":
    main()
