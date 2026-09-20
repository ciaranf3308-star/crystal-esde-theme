# Crystal ES-DE v4.0.0 — carousel + panel text redesign plan

Date: 2026-09-20. Status: PLAN ONLY — no build until the user approves.

## What the Nova photo + ES-DE 3.4.1 source proved

1. **The "small" carousel is my design, rendered faithfully.** Measured the
   photo: unfocused cards 9.4% of screen width (expected 118/1280 = 9.2%),
   selected 12.6% (expected 157/1280 = 12.3%). The engine did exactly what I
   asked — I just asked for cards that are too small. The v3.6 proof mock
   flattered the design; device approval never happened.
2. **The clipping is real and I can see it.** The selected N64 poster's top
   edge is sliced dead flat in the photo. Root cause in 3.4.1 source
   (`CarouselComponent.h::render`): the carousel pushes an OpenGL scissor
   rect over its own bounds, and my selected card (1.33x + 19px lift)
   overflows the top by ~36px. My PIL mocks never simulated the scissor
   rect, so I never saw it. Process failure.
3. **The GIFs do not animate — and cannot, in the carousel.** 3.4.1's
   `ImageComponent.cpp` contains zero GIF/animation handling, and the
   carousel hard-creates plain `ImageComponent` items (no `itemTemplate`
   support in 3.4.1). The v3.8 "animated carousel" is static frame-0 on the
   Nova. Graceful fallback, but the feature as sold does not exist.
4. **The panel text is weak.** 15px badge / 29px title / 15px dim description
   / 40px count / 14px facts, clustered in the top half of a tall panel.
   Small, sparse, poor hierarchy.

## v4.0.0 design

### Carousel — bigger, verified no-clip (screen 1280x960)

- `itemSize` 0.130 0.215 → 166x206px cards (was 118x154, +41% unfocused)
- `itemScale` 1.25 → selected 208x258 (was 157x205, +32%)
- `selectedItemOffset` 0 -0.010 → 10px lift (was 19px)
- `selectedItemMargins` 0.010 0.010 (keep — breathing gap)
- `reflections` false (was true). The 3.4.1 layout math reserves 2x item
  height for reflections; at these card sizes that would force a half-screen
  carousel zone and eat the hero. The glossy stage stays as the floor.
- `maxItemCount` 7, `ascendingRaised`, `unfocusedItemOpacity` 0.90,
  `unfocusedItemSaturation` 0.55, `unfocusedItemDimming` 0.18,
  `imageCornerRadius` 0.008, `imageInterpolation` linear — all keep.
- `pos` 0 0.700, `size` 1 0.300 → zone y 672..960 (was 622..944).
- No-clip proof from the engine's own formulas:
  yOff = (288-206)/2 = 41; selected top overflow = (258-206)/2 + 10 = 36;
  41 >= 36 ✓. Selected bottom = 263 <= 288 ✓. Unfocused 166x206 fits ✓.
- Spacing: (1280 - 7*166)/7 + 166 = 183px slots; selected 208 wide vs
  183 slots + 13px margins each side → no overlap, ascendingRaised on top.
- Stage: `carousel_vignette.png` rebuilt, `pos` 0 1 `size` 1 0.340, spotlight
  recentered on the new selected slot (x 0.5, y 0.85 → stage-fraction 0.558).
  z40 stage, z45 carousel, transparent carousel color (unchanged).

### Cards — back to static, full quality

- `staticImage` → `./cards/${system.name}.png` (v3.6 trading cards, 400x424,
  real alpha — zero black-bar risk at 208x258).
- All 21 systems use the trading-card design for strip consistency.
- `cards_anim/*.gif` stay in the repo (1.3MB; the user's poster art, kept for
  the animation follow-up below) — or drop from ZIP if the user prefers.

### Panel text — bigger, real hierarchy (fractions of 1280x960)

Panel on supplied heroes: x 0.014..0.285, y 0.17..1.0.

- mfrBadge: pos 0.030 0.195, fontSize 0.018 (was 0.016) — white pill, uppercase.
- sysName: pos 0.030 0.230, size 0.24 0.055, fontSize 0.040 (was 0.030).
  FULL re-measure of every system's fullName at 0.040 against its panel
  width with DejaVu Sans Bold metrics; per-system overrides (nes/snes
  two-line, gb narrow) re-verified with positioned 1280x960 mocks.
- sysDesc: pos 0.030 0.305, size 0.20 0.14, fontSize 0.019 (was 0.0155),
  color crystalText white (was dim) — actually readable.
- countNum: pos 0.030 0.460, size 0.20 0.07, fontSize 0.055 (was 0.042).
- factsLine: pos 0.030 0.535, size 0.20 0.04, fontSize 0.017 (was 0.015),
  accent yellow, uppercase.
- Optional: thin divider rule image between title and description
  (white 40%, 0.20 x 0.002 at y ~0.295) — theme-legal, no hero art touched.

### Proof process (the part that failed last time)

- Rebuild the PIL proof mock WITH the scissor clip rect simulated
  (clip children to carousel bounds exactly as pushClipRect does).
- Render at 1280x960 with true z-order, per-frame scale/saturation/dimming
  math from the 3.4.1 source, and LOOK at it before shipping.
- Positioned text mocks for all 21 systems at the new sizes.

## The animation question — honest answer

The strip cannot animate on ES-DE 3.4.1 (source-verified, see point 3).
Follow-up offer, NOT in v4.0.0: ES-DE's `<animation>` theme element plays
animated images elsewhere in the view. If it resolves `${system.name}` and
refreshes on system change (to be verified against source before building),
the 7 animated posters could live as a large "now showing" animated feature
in the gamelist view. The user's call.

## Build steps (after approval)

1. Edit views.xml carousel + text (numbers above).
2. Rebuild carousel_vignette.png with spotlight at new slot center.
3. Re-measure all 21 system names at 0.040; update per-system overrides.
4. Clip-simulating proof mock at 1280x960; inspect; iterate.
5. Validator (pinned 3.4.1) → deterministic build → stable release,
   download-verified. Version 4.0.0, code 22.
