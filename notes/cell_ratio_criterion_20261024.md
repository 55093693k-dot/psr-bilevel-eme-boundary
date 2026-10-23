# The obvious dimensionless group does not order the readings (2026-10-24, 0 FlexCredit)

**Question.** The report says a port-basis column sum is not a device insertion loss. Can that be
compressed into one number a reader can check on their own model — the **per-cell lateral shift divided
by the guide width**, `r = Δ_cell / w`? If `r` ordered the readings, the clause would become "unreliable
above `r = …`", which would carry to other devices instead of staying a case report.

**What was done.** Every record already on disk was reused; **nothing was run** (0 FlexCredit).
`Δ_cell` is the largest lateral displacement between adjacent cell centres. For a cosine S-bend
`y = Δy (1 − cos(πx/L)) / 2` the maximum slope is `πΔy / (2L)`, so `Δ_cell = πΔy/(2L) × cell length`.
Guide width `w = 0.5 µm` in every case below.

| family | Δy | bend length | cell | cells | `Δ_cell` | `r = Δ_cell/w` | reading (column sum) |
|---|---|---|---|---|---|---|---|
| amplified S-bend (2nd solver) | 5 µm | 20 µm | 5 µm | 12 | 1.96 µm | **3.93** | 8.5×10⁻⁵ |
| amplified S-bend | 5 µm | 20 µm | 2.5 µm | 24 | 0.98 µm | **1.96** | 0.0661 |
| amplified S-bend | 5 µm | 20 µm | 1 µm | 60 | 0.39 µm | **0.785** | 0.0115 |
| amplified S-bend | 5 µm | 20 µm | 0.5 µm | 120 | 0.20 µm | **0.393** | 0.0378 |
| gentle S-bend (2nd solver) | 5 µm | 100 µm | 5 µm | — | 0.39 µm | **0.785** | 0.0090 |
| gentle S-bend | 5 µm | 100 µm | 2.5 µm | — | 0.20 µm | **0.393** | 0.0116 |
| gentle S-bend | 5 µm | 100 µm | 1 µm | — | 0.079 µm | **0.157** | 0.0115 |
| gentle S-bend (original platform) | 5 µm | 100 µm | 5 µm | 40 | 0.39 µm | **0.785** | 4.8×10⁻⁵ |
| gentle S-bend (original platform) | 5 µm | 100 µm | 1 µm | 200 | 0.079 µm | **0.157** | 4.3×10⁻³ |

## Verdict

- **Within the amplified family** the reading goes 8.5×10⁻⁵ → 6.6 % → 1.15 % → 3.8 % while `r` falls
  monotonically 3.93 → 0.393. **Not monotone** (up, down, up).
- **Within the gentle family on the second solver** `r` falls 0.785 → 0.157 and the reading is
  **flat** (0.90 / 1.16 / 1.15 %).
- **The same gentle structure on the original platform** moves **90×** (4.8×10⁻⁵ → 4.3×10⁻³) over the
  same change of `r`.
- ⇒ `r` does not order these readings, neither within one structure nor across the two platforms.
  **No threshold on `r` is proposed**, here or in the paper.

## What this does *not* show

- It does **not** show that no criterion exists. The physically right quantity is the **radiation
  content the port basis cannot represent**, and measuring it needs a basis wide enough to carry it —
  a run, not an analysis of recorded numbers.
- It does not change any scope statement: the transferable object stays the four-feature checklist
  (two offset port planes / a finite basis / a discretised propagation direction / a calibration plane
  set by defaults), not a number.
- It **does** reproduce, independently and from geometry alone, the cross-platform disagreement
  recorded in the paper's "what remains unexplained" list.

## Reproduction

- amplified: `second_solver/probe_amp.py`, readings in `second_solver/PROBE_FINDINGS_20261007.md`
  (§ "continuation 10", table of 12 / 24 / 60 / 120 cells);
- gentle, second solver: `PROBE_FINDINGS_20261007.md` (0.90 / 1.16 / 1.15 %);
- gentle, original platform: `PERSONAL_BRAND/BUILDS/iop_build/runs/sbend.log` and
  `runlogs/run_sbend_fix_20261023.md`.
