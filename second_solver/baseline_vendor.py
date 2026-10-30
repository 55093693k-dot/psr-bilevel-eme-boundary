# -*- coding: utf-8 -*-
"""baseline_vendor.py — the vendor's own bent-EME example, run almost verbatim.

Purpose: separate "this machine/account cannot run bent EME" from "my model is wrong".
Only the two malformed material names (the export has broken escaped quotes) are simplified;
every physical and numerical setting is the vendor's.
"""
import numpy as np

import tidy3d as td
import tidy3d.web as web

sio2 = td.PoleResidue(
    name="SiO2_Palik_LowLoss",
    frequency_range=[59958491600000, 1998616386666666.8],
    eps_inf=1.5385442336875639,
    poles=[[(-11504139.374277674 - 15951967407837750j), (7507685.43042605 + 4535416182817100j)],
           [(-249390.3565044153 - 172280738540723.53j), (46272.506981344035 + 99704543223121.88j)],
           ],
)
linbo3 = td.PoleResidue(
    name="LiNbO3_Y",
    frequency_range=[59958491600000, 749481145000000],
    poles=[[(0 + 14182450644861764j), (0 - 18957681776986720j)],
           [(0 + 7745686426535269j), (0 - 4759724309105923j)],
           [(0 + 86464275012302.47j), (0 - 545330182502591.7j)],
           ],
)
ln = td.AnisotropicMedium(name="LiNbO3_Zelmon1997_Y", xx=linbo3, yy=linbo3, zz=linbo3)

structure_0 = td.Structure(
    geometry=td.PolySlab(slab_bounds=[-0.2, 0.2],
                         vertices=[[-1e15, -0.3], [-1e15, 0.3], [1e15, 0.3], [1e15, -0.3]]),
    name="structure_0",
    medium=ln,
)
modes = td.EMEModeSolverMonitor(size=[td.inf, td.inf, td.inf], name="modes", num_modes=6)

sim = td.EMESimulation(
    size=[15.707963267948966, 9, 9],
    freqs=[193414489032258.06],
    axis=0,
    medium=sio2,
    structures=[structure_0],
    monitors=[modes],
    grid_spec=td.GridSpec.auto(min_steps_per_wvl=30),
    subpixel=td.SubpixelSpec(dielectric=td.PolarizedAveraging(), metal=td.Staircasing(),
                             pec=td.PECConformal(), pmc=td.Staircasing(),
                             lossy_metal=td.SurfaceImpedance()),
    eme_grid_spec=td.EMEUniformGrid(
        num_cells=5,
        mode_spec=td.EMEModeSpec(num_modes=10, target_neff=1.65, num_pml=[12, 12],
                                 bend_radius=5, bend_axis=1,
                                 sort_spec=td.ModeSortSpec(
                                     bounding_box={"center": [0, 0, 0], "size": [td.inf, 0.6, 0.4]},
                                     sort_key="fill_fraction_box", sort_order="descending"),
                                 interp_spec=td.ModeInterpSpec(
                                     sampling_spec=td.ChebSampling(num_points=5), method="poly",
                                     reduce_data=True),
                                 increasing_mode_tolerance=0.001),
    ),
    sweep_spec=td.EMEModeSweep(num_modes=[1, 2, 3, 4, 5, 6, 6, 7, 8, 9, 10]),
)

print("estimate:", web.estimate_cost(web.upload(sim, task_name="vendor_baseline", verbose=False)))
data = web.run(sim, task_name="vendor_baseline", path="vendor_baseline.hdf5", verbose=False)
print("OK data:", type(data).__name__)
