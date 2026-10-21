# Run record 2026-10-07 -- coupler EME cell-length ladder (runs reported here)

Purpose: test whether the coupler number depends on the EME cell length (bias family C).
Single variable: coupler cell length only (junction cells fixed at 0.5 um); everything else identical.
Command (per point):  python sim/run_eme_coupler.py --modes 6 --y 6 --cell <L> --submit
Domain x = 100...410 um; ports at x = 105 (in) / 405 (out); constraint = passive; single frequency 1.55 um; 6 modes.

| coupler cell | TE1 -> lower-arm TE0 | TE0 -> upper-arm TE0 | EME cells | billed-ish cost (estimate) |
|---|---|---|---|---|
| 5 um (previous run) | 0.99233 | 0.99805 | 157 | (earlier) |
| 1 um (this run)    | **0.99840** | **0.99983** | **305** | 1.477 FlexCredit (estimate) |
| 0.31 um            | not reachable | not reachable | 962 > 500 cap | not run |

Findings:
- One step of the ladder moves the key channel by about +0.6 % (0.99233 -> 0.99840), in the same direction as the
  external review reported (0.99162 -> 0.99870). This is a measurement reported here, not a restatement.
- Monotonicity cannot be judged from two points; the rule (take 3-4 points where the tool allows) stands.
- HARD BOUND (verified here): Tidy3D rejects more than 500 EME cells. On this 300 um-long domain a uniform
  0.31 um cell length needs 962 cells, so the finer points of the review table are NOT reachable here as a
  uniform-cell ladder. This is a tool-side limit, not a physics result.

Row sums at 1 um (out x in), from the console output: rows 0.9998 / 0.9996 / 0.9839 / 0.9858 / 0.9988 / 0.9779
(all <= 1, passive). Raw matrix and the run log are in the console output of 2026-10-07 14:46; the solver
data file is sim/data_psr_coupler_eme_m6_y6_c1.hdf5.

Known trap hit again (failure library, entry for the port-mode read path; index entry T-022): reading the port modes from
`data.modes_in` fails with AttributeError; the port mode solutions live in `data.monitor_data["<monitor>"].n_complex`.
Neff values were therefore not printed by the script this run; the fix is booked for the script.
