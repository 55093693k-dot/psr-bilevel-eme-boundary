# second_solver — the minimal S-bend read by Lumerical MODE (EME, varFDTD, FDE)

This folder is the record of the **second solver** runs quoted in the report *The boundary of a
mode-expansion insertion loss* (Sec. 9 of the manuscript). They exist for one reason: the boundary is
stated for a **class** of devices, so the case it came from had to be re-read somewhere that shares
none of the first solver's code.

**Structure** (one that carries the boundary's features and nothing else): straight input guide →
**one S-bend**, 5 µm lateral offset over 100 µm → straight output guide. Silicon 500 × 220 nm on SiO₂
(Palik), single wavelength λ = 1.55 µm, ports x-normal at both ends. Total length 200 µm
(50 + 100 + 50).

## What it shows

**One nominal structure, three engines, three answers.** The exact cross-sectional solve says the
bend is lossless; the two propagation solvers disagree with it and with each other.

| method | reading for the same S-bend | where |
|---|---|---|
| EME, straight cells stacked along the bend | column sum **≈ 0.055** | `run_min_sbend_eme.py`, `min_sbend_eme_*um_p0.log` |
| varFDTD (2.5-D effective index) | key channel **0.765** (same-caliber straight control 0.975) | `ready_varfdtd.py`, `read_varfdtd.py`, `sweep_varfdtd.py` |
| FDE, bent-waveguide mode at R = 405 µm (the S-bend's minimum radius) | **7.6 × 10⁻¹⁰** — lossless within numerical precision | `probe_bentfde.py` |

**Each clause moves the reading when it is amplified.** On the *gentle* 100 µm S-bend the EME column
sum barely moves with the cell length (0.90 % / 1.16 % / 1.15 % for 5 / 2.5 / 1 µm cells). Shortening
the bend to 20 µm at the same 5 µm offset magnifies the per-cell lateral jump, and there:

| knob swept | readings | spread |
|---|---|---|
| cell length (12 / 24 / 60 / 120 cells) | 0.0085 % / 6.6 % / 1.15 % / 3.8 % | ≈ **800×** |
| modes kept, cells fixed at 1 µm (2 / 4 / 8 / 16 / 32) | 0.27 % / 0.080 % / 1.15 % / 0.17 % / 3.5 % | ≈ **44×** |

Both tables are in `PROBE_FINDINGS_20261007.md` (the mode sweep is also transcribed, point by point,
in `make_figB.py` and appears in `probe.log` / `probe_results.json`).

**Controls: change only the device and the reading does not move.** Straight guide 1.000000 (at 2 and
at 24 modes); straight guide **held at a constant** 5 µm lateral offset 1.000000; width taper
500 → 600 nm 0.998908. The collapse therefore tracks the one step in which the guide **moves
laterally** — a step the vendor's own advice says to model with bent cells, not with stacked straight
ones.

## Calibers — read these with every number above

- **Nothing here is converged.** The EME readings are non-monotonic in both knobs and still moving at
  the finest setting used. They are evidence that the knobs dominate the reading — not convergence
  curves, and not device transmission.
- **varFDTD's straight control is a different caliber from its bend reading** (the straight run was
  early-stopped at 21 %, the bend run at 92 %; auto-shutoff 7.6 × 10⁻⁶ vs 1.7 × 10⁻⁵), so the ratio
  ≈ 0.785 is indicative only; the bend's spectrum carries noise (0.53–1.07, with entries above 1).
- **The FDE bent solve is exact only where the solver is trustworthy**: at R = 405 µm it is clean; at
  R = 5 µm the solver returns an unphysical mode (see `PROBE_FINDINGS_20261007.md`).
- **The port-mode count could not be set through the script interface** (`addemeport()` objects are
  not addressable by name, and reading their numeric properties hangs the process), so the EME column
  sums above use the default port sampling; adding two EME ports widened the S-matrix from 2 × 2 to
  4 × 4 and lifted the column sum from 0.054922 to 0.164754, still far from 1.
- **The `.lms` projects are not shipped** — 31 MB, 55 MB and 127 MB; the largest is over GitHub's
  per-file limit, and they are results rather than dependencies. The scripts in this folder rebuild
  them.

## What is in the folder

- `run_min_sbend_eme.py`, `run_min_sbend_eme_probe.py` — build and run the EME model (cell ladder,
  mode ladder).
- `probe_*.py` — the probe series: port discovery (`probe_ports.py`), the cross-section check
  (`probe_fde.py`), the mechanism test (`probe_taper.py`), the mesh and cell-group exclusions
  (`probe_mesh.py`, `probe_mesh2.py`), the amplified model (`probe_amp.py`), the bent FDE solve
  (`probe_bentfde.py`), and the property-discovery helpers.
- `ready_varfdtd.py`, `read_varfdtd.py`, `sweep_varfdtd.py`, `probe_varfdtd.py` — the varFDTD route.
- `PROBE_FINDINGS_20261007.md` — the round-by-round record (Chinese, as originally written): what was
  measured, what was ruled out, and the calibers.
- `*_p0.log`, `probe.log`, `run.log`, `console.out/.err` — the engine and session logs the readings
  were read from.
- `results.json`, `results.csv`, `probe_results.json` — the machine-readable readings.
- `make_figA_two_views.py`, `make_figA_tidy3d.py`, `make_figA_lumerical.py`, `make_figB.py`,
  `make_figC.py` — the scripts that drew the report's three figures from these records. The first
  solver drew the structure figure; `make_figA_lumerical.py` is the abandoned attempt to export the
  same view from the second solver (the export needs a visible session and framed the view badly),
  kept because the failure is part of the record.
