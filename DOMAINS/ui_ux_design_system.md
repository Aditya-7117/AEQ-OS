# UI/UX Design System — Domain Invariants

For frontends, dashboards, terminal interfaces, and design systems. Default register: **institutional, high-density, matte.** The UI of a trading terminal is an instrument panel, not a brochure. Rule IDs: `UIUX-n`.

## 1. Aesthetic defaults

- **UIUX-1** — The default aesthetic is mature and institutional. Playful, casual, or generic-colorful boilerplate (pastel gradient heroes, emoji-decorated buttons, rounded-everything template looks, default component-library styling shipped unmodified) is prohibited unless the user explicitly requests it (see UIUX-20). Shipping the framework's default look is a design failure, not a neutral choice.
- **UIUX-2 — Matte-black canvas tokens (defaults; brand may re-tint, structure may not change):**

      --bg-canvas:     #0B0B0D;  /* near-black matte — never pure #000 (UIUX-4) */
      --bg-surface-1:  #121215;  /* each elevation step ≈ +4% luminance          */
      --bg-surface-2:  #18181C;
      --bg-surface-3:  #1E1E23;
      --edge-hairline: #26262C;  /* 1px borders carry structure                  */
      --edge-highlight: rgba(255,255,255,0.04);  /* 1px top edge = key light     */
      --text-primary:  #E9E9EC;
      --text-secondary:#9B9BA4;
      --text-muted:    #5D5D67;
      --accent:        #5B8DEF;  /* exactly one accent hue per product           */
      --pos:           #2FBF71;  /* gains / healthy                              */
      --neg:           #E5484D;  /* losses / errors                              */
      --warn:          #F5A524;

- **UIUX-3 — Elevation by lighting, not decoration.** Depth comes from the luminance ladder (UIUX-2), hairline borders, and the subtle top-edge highlight — cinematic and quiet. Shadows are short and soft where used. No glassmorphism, no neon glow, no gradient washes by default.
- **UIUX-4** — Pure `#000` and pure `#FFF` are forbidden as large fields. Contrast still meets WCAG AA: ≥ 4.5:1 body text, ≥ 3:1 large text and secondary UI.
- **UIUX-5 — Geometry.** 8px base grid, 4px sub-grid for dense tables. Radii small and uniform: one radius token per surface class, 0–6px. Sharp structural alignment is mandatory — every edge sits on the grid; no optical eyeballing.
- **UIUX-6 — Typography.** One UI sans (Inter or system stack) + one monospace for data. All numerals in data contexts use tabular figures (`font-variant-numeric: tabular-nums`). A fixed type scale (e.g., 11/12/13/14/16/20/28), max two families, line-height 1.25–1.4 for density, slight positive letter-spacing on small all-caps labels only.
- **UIUX-7 — Numbers behave like instruments.** Right-aligned in columns, fixed decimal places per asset class (from instrument metadata, CONST-11), thousands separators, explicit sign on deltas (+/−). Column widths never wobble as values tick.

## 2. Data hierarchy & alert urgency

- **UIUX-8** — Hierarchy encodes importance: primary metrics largest and brightest, metadata muted (`--text-muted`). Color is reserved for meaning — state, PnL, alerts. A colored element must be decodable by the viewer; decoration-color is banned.
- **UIUX-9 — Urgency ladder,** each level a distinct multi-channel cue (color + icon + weight — never color alone):
  - INFO: muted accent, inline, no motion.
  - WARN: `--warn`, persistent until acknowledged, no motion.
  - CRITICAL: `--neg`, pinned to a dedicated status strip, at most one pulse on arrival — infinite blinking is forbidden (it trains blindness).
  - HALT/KILL: the status strip takes over; nothing else on screen may compete with it (LIVE-21 events land here).
- **UIUX-10 — State honesty.** Stale data looks stale: visible timestamp plus dimming past the staleness threshold (QT-WS-3). Unknown is never rendered as zero or empty — an unknown value shows as an em-dash with a reason on hover (CONST-6 applied to pixels). Loading, empty, and error are three different designed states.
- **UIUX-11** — Trading/ops surfaces keep system status permanently visible: feed state (`LIVE/DEGRADED` per QT-WS-1), latency, clock skew, and kill-switch arm state. If the operator must click to learn the feed is degraded, the layout is wrong.

## 3. Density & layout

- **UIUX-12** — High-density terminal layouts are the default for operational tooling: panel grids with fixed headers, table rows 28–32px, marketing whitespace patterns collapsed. Density with alignment is professionalism; density without alignment is clutter — UIUX-5 is what separates them.
- **UIUX-13 — Layout stability.** Live data causes zero layout shift: reserved column widths, fixed panel dimensions, CLS ≈ 0. Tick-change flashes highlight only the changed cell and decay within ~300ms.

## 4. Low-latency rendering for live data

- **UIUX-14** — Stream messages never bind directly to the DOM. Updates coalesce through a `requestAnimationFrame` batch: at most one paint per frame, rendering the *latest* state (conflation — intermediate ticks are dropped, not queued).
- **UIUX-15** — High-frequency surfaces (order books, tapes, depth charts, sparklines) render to canvas/WebGL, not DOM nodes. DOM tables virtualize beyond ~200 rows.
- **UIUX-16 — Repaint discipline.** Memoized components; keyed lists; animations use transform/opacity only (compositor path); style reads and writes are batched, never interleaved (layout thrashing). A profiler trace, not intuition, decides what re-renders.
- **UIUX-17 — Performance budgets are tested numbers** (VER-4 evidence, not vibes): interaction latency < 100ms; no long tasks > 50ms during steady-state streaming; main thread < 50% utilization at the expected tick rate.

## 5. Implementation discipline

- **UIUX-18** — Every color, spacing, radius, and type value flows from design tokens (CSS custom properties / theme file). A hardcoded hex or px literal in a component is a lint failure. Theming is a token swap, never a component edit.
- **UIUX-19** — Every interactive component defines all states: default, hover, active, focus-visible, disabled, loading, error, empty. Keyboard navigation and visible focus rings are mandatory — institutional software is operated under pressure, often without a mouse.
- **UIUX-20 — Exception path.** Playful or casual styling happens only on explicit user request, recorded in the project's spec/SDR. Even then, the data rules (UIUX-6, UIUX-7, UIUX-10) still bind — a whimsical brand does not excuse wobbling numerals or dishonest zeros.
