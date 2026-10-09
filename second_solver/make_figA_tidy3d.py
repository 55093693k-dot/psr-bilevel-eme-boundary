# -*- coding: utf-8 -*-
"""make_figA_tidy3d.py — Figure A: the minimal structure, exported by Tidy3D's OWN plotting.

Uses tidy3d.Simulation.plot_structures (the official renderer), so the figure is solver-exported
rather than hand-drawn.
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import numpy as np
import tidy3d as td

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


def build(dy: float = DY) -> td.Simulation:
    verts = sbend_vertices()
    if dy == 0.0:
        verts[:, 1] = 0.0
    strip = td.Structure(
        geometry=td.PolySlab(vertices=verts, axis=2, slab_bounds=(0.0, 0.22)),
        medium=td.Medium(permittivity=12.25),           # Si
    )
    oxide = td.Structure(
        geometry=td.Box(center=(L_TOT / 2, dy / 2, -0.5), size=(L_TOT, dy + 6.0, 1.0)),
        medium=td.Medium(permittivity=2.085),           # SiO2
    )
    return td.Simulation(
        size=(L_TOT + 8.0, dy + 6.0, 3.0), center=(L_TOT / 2, dy / 2, 0.0),
        grid_spec=td.GridSpec.auto(wavelength=1.55), run_time=1e-13,
        structures=[oxide, strip],
    )


def main() -> None:
    for tag, dy in (("bend", DY), ("straight", 0.0)):
        sim = build(dy)
        ax = sim.plot_structures(z=0.11)
        ax.set_title("")
        f = ax.figure
        f.tight_layout()
        png = os.path.join(OUT, "figA_structure_%s_tidy3d.png" % tag)
        pdf = os.path.join(OUT, "figA_structure_%s_tidy3d.pdf" % tag)
        f.savefig(png, dpi=300)
        f.savefig(pdf)
        print("WROTE", png)


if __name__ == "__main__":
    main()
