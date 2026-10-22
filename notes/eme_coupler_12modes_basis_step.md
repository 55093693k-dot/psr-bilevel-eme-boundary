# Run record: coupler segment, 12 port modes at 1 µm cells (basis step)

**Date**: 2026-10-23. **Purpose**: step the port-mode axis one more time, at the cell length used for the
cell ladder, so that §4.1 of the README rests on a record rather than on a sentence.

## Settings

Single variable changed against the 6-mode run of `notes/eme_coupler_6modes_convergence.md`: the port-mode
count. Everything else is the same scene.

| item | value |
|---|---|
| script | `sim/run_eme_coupler.py --modes 12 --y 6 --cell 1.0` (dry-run first, then submit) |
| EME cells | 305 (1 µm cell over the same length) |
| port modes | 12 per port |
| constraint | `passive` |
| frequency | single, λ = 1.55 µm |
| ports | x = 105 / 405 µm, y-span 6.0 µm |
| cost | 1.769 FlexCredit (dry-run estimate); wall time 545 s |
| output | `sim/data_psr_coupler_eme_m12_y6_c1.hdf5` (59 MB, not in this repo) |

## Readings (|S|², read straight from `smatrix/S21`)

Ports aligned by effective index, not by mode number. Lower-arm TE0 is n_eff = 2.4423 at 12 modes and
2.4424 at 6 modes — the same mode, one index apart from what a centroid-based identifier returns.

| quantity | 6 modes | 12 modes | Δ |
|---|---|---|---|
| TE1 → lower-arm TE0 (key channel) | 0.998445 | **0.998870** | **+0.000425** |
| TE1 → upper-arm TE0 (unwanted) | 0.001281 | 0.001282 | 0 |
| TE0 → its own port (through) | 0.999819 | 0.999729 | −0.000090 |
| TE1 input column sum | 0.999736 | **1.000161** | +0.000425 |
| total reflected power (S11 over all 12 × 12 entries) | — | ≈ 1.1 × 10⁻⁴ | — |

## What the record supports

- Adding port modes does **not** create a deficit: the column sum rises by exactly what the key channel
  gains, and the reflected power stays at the 10⁻⁴ level. Within this basis there is still no
  radiation-loss channel to be read.
- The effect of a basis step is **smaller than a cell-length step** and **changes sign with the cell
  length**: −0.29 points for 4 → 6 at 5 µm, +0.04 points for 6 → 12 at 1 µm. Neither is a convergence
  curve for device loss.

## What the record does not support

- Any statement about a basis larger than 12 modes, or about a basis that can represent radiative content.
- Any absolute insertion loss. Both numbers are port-mode-basis readings, not device efficiencies.
- Any device efficiency: the same quoting rule as §6 of the README applies unchanged.

## Trap hit while producing this record

`sim/analyze_coupler_eme_modes.py` identifies port modes by effective index *and* transverse field centroid.
At 12 modes the centroid test picks mode 9 of the output port (n_eff 1.3775, a higher-order mode) as the
lower-arm fundamental, and the script then reports the key channel as **0.000**. The physical value is
0.998870. The readings above were taken by reading `smatrix/S21` directly and pairing the two ports by
n_eff (2.4423 ↔ 2.4424); the script was not changed, and its 6-mode output — which the rest of the
repository uses — is unaffected.
