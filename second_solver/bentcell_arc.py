# -*- coding: utf-8 -*-
"""bentcell_arc.py — the experiment the paper asserts but has never run.

The manuscript (Sec. 6) states, as a consequence of its own mechanism, that bends should be
modelled with bent cells rather than with straight cells. This script tests that sentence on
the case where the answer is unambiguous: a quarter-circle bend of fixed radius, read two
ways ---
  (A) BENT      : the structure is defined STRAIGHT; each EME cell carries bend_radius,
                  so the curved cross-section is represented exactly.
  (B) STAIRCASE : the same arc is drawn as a polygon and cut into straight cells, so the
                  curve is represented by steps whose size is the cell length.

If (A) returns ~1 and does not move with the cell count while (B) scatters, the paper stops
asserting the remedy and starts showing it.

WHY THE ARC AND NOT THE S-BEND: a bent cell is exact only for a constant radius. An S-bend
has varying curvature, so a bent-cell version of it would itself be an approximation and the
comparison would be muddied. The arc is where "the right representation" is exactly right.

COST DISCIPLINE (repo rule, SIMULATION_SETUP.md): build -> validate_pre_upload() ->
estimate_cost() -> only then submit. Nothing here submits unless asked.
"""
from __future__ import annotations

import numpy as np

import tidy3d as td
import tidy3d.web as web

LAM = 1.55e-6
W = 0.50e-6
T_SI = 0.22e-6
R_BEND = 10e-6
N_MODES = 4
ARC = np.pi * R_BEND / 2.0        # quarter circle: the length of the bent path
PAD = 1.0e-6                      # a little straight run at each end for the ports


def _base(size_x: float, structures: list, store_port_modes: bool = True) -> dict:
    return dict(
        center=(0.0, 0.0, 0.0),
        # the radial span of the mode plane must stay under the bend radius (server check):
        # 12 um here, so half-span 6 um < R = 10 um
        size=(size_x, 12e-6, 2e-6),
        medium=td.Medium(permittivity=1.0),
        structures=structures,
        axis=0,
        freqs=[td.C_0 / LAM],
        store_port_modes=store_port_modes,
    )


def _oxide(size_x: float) -> td.Structure:
    return td.Structure(
        geometry=td.Box(center=(0.0, 0.0, -0.5e-6), size=(size_x, 12e-6, 1e-6)),
        medium=td.Medium(permittivity=2.085),
    )


def bent(num_cells: int = 8, bend_axis: int = 1, store_port_modes: bool = True) -> td.EMESimulation:
    """(A) the exact representation, built the way the vendor's own bent-EME example is built:

    * the waveguide is a strip that runs BEYOND the simulation box (here 4x), never ending on
      the port plane;
    * no port offsets: the ports sit at the ends of the box, where the guide continues;
    * the cross-section mesh, mode target index and PML padding are set explicitly.
    The curvature is carried entirely by the mode spec, on a straight geometry.
    """
    sim_len = ARC                      # the path length of the quarter circle
    strip = td.Structure(
        geometry=td.Box(center=(0.0, 0.0, T_SI / 2), size=(4 * sim_len, W, T_SI)),
        medium=td.Medium(permittivity=12.25),
    )
    spec = td.EMEModeSpec(num_modes=N_MODES, bend_radius=R_BEND, bend_axis=bend_axis,
                          num_pml=(12, 12), target_neff=2.4, precision="double")
    grid = td.EMEUniformGrid(mode_spec=spec, num_cells=num_cells)
    return td.EMESimulation(
        center=(0.0, 0.0, 0.0),
        size=(sim_len, 9e-6, 9e-6),
        medium=td.Medium(permittivity=2.085),      # SiO2 cladding everywhere
        structures=[strip],
        axis=0,
        freqs=[td.C_0 / LAM],
        grid_spec=td.GridSpec.auto(min_steps_per_wvl=30),
        eme_grid_spec=grid,
        store_port_modes=store_port_modes,
    )


def staircase(cell_um: float) -> td.EMESimulation:
    """(B) the same arc drawn as a polygon, cut into straight cells of `cell_um`."""
    n = 401
    s = np.linspace(-ARC / 2, ARC / 2, n)
    # centre-line of a quarter circle of radius R, rotated so it runs along +x
    phi = s / R_BEND
    cx = R_BEND * np.sin(phi)
    cy = R_BEND * (1.0 - np.cos(phi))
    th = phi
    nx, ny = -np.sin(th), np.cos(th)
    top = np.vstack([cx + nx * W / 2, cy + ny * W / 2]).T
    bot = np.vstack([cx - nx * W / 2, cy - ny * W / 2]).T
    verts = np.vstack([top, bot[::-1]])
    L = ARC + 2 * PAD
    # shift the polygon into the simulation frame, add the two straight pads
    strip = td.Structure(
        geometry=td.PolySlab(vertices=verts, axis=2, slab_bounds=(0.0, T_SI)),
        medium=td.Medium(permittivity=12.25),
    )
    pads = [
        td.Structure(geometry=td.Box(center=(-ARC / 2 - PAD / 2, 0, T_SI / 2), size=(PAD, W, T_SI)),
                     medium=td.Medium(permittivity=12.25)),
        td.Structure(geometry=td.Box(center=(ARC / 2 + PAD / 2, R_BEND * (1 - np.cos(np.pi / 2)), T_SI / 2),
                                     size=(PAD, W, T_SI)),
                     medium=td.Medium(permittivity=12.25)),
    ]
    spec = td.EMEModeSpec(num_modes=N_MODES, precision="double")
    grid = td.EMEUniformGrid(mode_spec=spec, num_cells=max(4, int(round(L / (cell_um * 1e-6)))))
    return td.EMESimulation(**_base(L, [_oxide(L), strip] + pads), eme_grid_spec=grid,
                            port_offsets=(PAD, PAD))


def report(sim: td.EMESimulation, tag: str) -> None:
    """Validate, upload (free), then print the price. Does NOT run."""
    sim.validate_pre_upload()
    task_id = web.upload(sim, task_name="arc_" + tag, verbose=False)
    cost = web.estimate_cost(task_id)
    print("%-14s cells=%-4d task=%s  estimated FlexCredit = %.4f"
          % (tag, sim.eme_grid_spec.num_cells, task_id, cost))


if __name__ == "__main__":
    report(bent(8), "bent/8")
    report(staircase(5.0), "stairs/5um")
