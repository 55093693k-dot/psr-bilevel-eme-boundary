# Figures — what each one is, and what it is NOT

The rule applied here: **a figure's evidence grade depends on who drew it.** A solver's own
structure view / field / data export is solver evidence; a matplotlib figure is a human
re-projection and is *not* equivalent. Every matplotlib figure therefore has to say so, **on the
figure** and in its PNG metadata.

| figure | what it is | channel | channel label present? |
|---|---|---|---|
| `colsum_and_conversion_vs_modes.png` | matplotlib **re-plot of tabulated EME results** (column sums + conversion at 4 and 6 port modes) | `external` | ✅ yes — on-figure footer **and** PNG `tEXt` chunk `External-Plot` |
| `device_topview.png` | matplotlib **re-draw from the solver model** — two z-slices of the whole device (partial-etch slab layer and waveguide layer) | `external` | ✅ statement in the PNG `tEXt` chunk `External-Plot` **and in the manuscript caption**; **no on-figure footer** (on purpose, 2026-09-28: it blocked the drawing). Original canvas kept pixel-for-pixel; proportions narrowed to **2.00:1** by white padding |
| `device_cross_section.png` | matplotlib **re-draw from the solver model** — cross-section at the adiabatic coupler | `external` | ✅ statement in the PNG `tEXt` chunk `External-Plot` **and in the manuscript caption**; **no on-figure footer** (2026-09-28). Original canvas kept as it was (1677x637 px) |

**None of these three is a solver export.** Do not quote any of them as "the solver's own view".
For the two referenceable numbers (`99.84%`, `99.233%`), cite §3 and §6 of the README — never a figure.

## State of these figures — 2026-09-28 (later the same day)

The two device figures were **restored to their original canvases**: the code that drew them is
not in this repository, so they cannot be faithfully re-drawn, and an attempt to re-draw them
changed what they show. What was done instead:

- the originals are back (byte-for-byte from git, pixel-for-pixel identical);
- `device_topview.png` was **narrowed in proportions to 2.00:1** (it was 3.46:1) by padding with
  white above and below — **no pixel of the drawing was touched**; `device_cross_section.png` keeps
  its original canvas (1677x637 px);
- the "external plot" statement now lives **in the PNG `tEXt` chunk** and **in the manuscript
  caption** for all three figures, and is **no longer drawn inside the figure** (at the author's
  request, 2026-09-28: the footer blocked the drawing). `fig_index.py` still audits the chunk;
- `colsum_and_conversion_vs_modes.png` was regenerated with **smaller markers and thinner
  strokes** and with no on-figure footer either, and its in-figure values were moved into the
  manuscript caption.

How to regenerate (the generator writes the device id in the name, so rename afterwards):

```bash
python tools/make_structure_fig.py --list
python tools/make_structure_fig.py --device psr_rotator --out figures
mv figures/PSR_ROTATE_ADIABATIC_BLT_v1_topview.png figures/device_topview.png
mv figures/PSR_ROTATE_ADIABATIC_BLT_v1_xsec.png    figures/device_cross_section.png
python tools/make_fig_colsum_vs_modes.py
```

Note: `make_structure_fig.py` draws a *single-slice* top view, i.e. **not** the two-slice figure
shipped here — that is why the shipped file is the original canvas rather than a regeneration.

`tools/make_structure_fig.py` labels every figure it writes (on-figure footer + PNG chunk) if
`fig_channel` is importable, and falls back to a plain save if it is not, so it never breaks.

  (Note: the regenerated top view is a **schematic** — x compressed, no layer split — so it is not a
  drop-in replacement for the two z-slice figures above.)

- Removing or relabelling those two figures is a one-line decision for the repository owner; it is
  left open rather than silently done, because relabelling would mean re-drawing them and the
  original drawing script is not part of this repository.

## One inconsistency to be aware of

`device_topview.png` states a **total length of ≈ 523 µm** in its own title, while the sum of the
segment lengths in the README is **≈ 537.8 µm**. The two numbers come from the same work at
different times; **this repository does not resolve the discrepancy.** Use the segment lengths
(they appear individually in §2 and in the scripts) and re-derive the total if you need it.

## Verify the labels yourself

```bash
# fig_index depends on fig_channel, so put both on PYTHONPATH
PYTHONPATH=tools python /path/to/fig_index.py --figs figures --index figs_index.json
```

`fig_index` reports each figure's channel, bytes, pixels and md5, and flags any `external`-channel
figure whose label chunk is missing. With the current contents it flags **nothing**: the two device
figures were regenerated on 2026-09-28 and now carry the `External-Plot` chunk as well.
