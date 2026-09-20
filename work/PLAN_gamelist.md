# Crystal gamelist / library view — design plan (vNext)

Target: Nova 1280x960 (4:3), ES-DE **3.4.1** (pinned — never master).
Reference: `workspace/user/media_library/image/33/33f4ac29df03111560f52081bd19a5393def876f45251646ebfa4934a93487ce.png`

## 3.4.1 hard constraints (verified against the real v3.4.1 source, /tmp/esde-src)

1. **One primary per gamelist view.** First of `carousel`/`grid`/`textlist` wins;
   any second is skipped with a warning. The bottom physical-media strip IS the
   navigable gamelist: a `<carousel>` element in the gamelist view becomes
   `mPrimary` (GamelistView.cpp:182-189). Left/right navigate, A launches.
2. **carousel/grid imageType limited to 2 entries** (CarouselComponent.h:1325,
   GridComponent.h:1002 — "Only allow two imageType entries due to performance
   reasons"). Extra entries are silently dropped. ImageComponent (hero/marquee/
   fanart slots) has NO such limit.
3. **No name labels under imaged carousel/grid items.** The entry's text item is
   REPLACED by the image when art is found (CarouselComponent updateEntry). Text
   labels render ONLY for items with no art (and no defaultImage). The carousel
   `text` theme property is not even read in 3.4.1. Consequence: neighbour names
   come from the physical-media label art itself; the selected game is identified
   by the marquee/title + left panel. This is a platform limit, surfaced to the user.
4. **Valid imageType values** (ImageComponent.h:167): `image miximage marquee
   screenshot titlescreen cover backcover 3dbox physicalmedia fanart`.
   `physicalmedia` is a REAL scraped media type (FileData::getPhysicalMediaPath,
   ScreenScraper "support" media). No hand-authored cart scans needed.
5. **imageType takes a comma/space list, searched in order**; blank when nothing
   found unless `default`/`defaultImage` is set (THEMES.md:2479).
6. **metadata keys** (MetaData.cpp): name, desc, rating, releasedate, developer,
   publisher, genre, players, playcount, playtime, lastplayed. `playtime` renders
   Steam-style ("42 hours") via FileData::getPlayTimeString. datetime with time 0
   renders "unknown"/"never" (or defaultValue) — releasedate "19700101T000000"
   parses to epoch 0, so unscraped release shows "unknown", not "1970".
7. **systemdata**: gamecountGamesNoText (number only) + static "GAMES" text.
8. **Carousel zIndex is forced to 50** (setDefaultZIndex/setZIndex). Overlays that
   must sit above it need zIndex > 50; the stage sits below.
9. **Per-system theme.xml merges at element level** — a per-system
   `<view name="gamelist">` containing only `<helpsystem name="help">` overrides
   just that element. Used to hide the live helpsystem on the 14 systems whose
   backgrounds have the footer baked in.
10. **rotation is in degrees**; non-90° rotations auto-enable linear interpolation.

## The three dynamic slots (user's defensive design)

1. **Marquee** — `<image imageType="marquee">` (no default → blank if missing),
   layered OVER a Nova-styled `<text metadata="name">` fallback in the same box.
   Missing marquee ⇒ blank ⇒ fallback title shows. (Transparent marquees may let
   a little of the backing title peek through — accepted, standard pattern.)
2. **Fanart hero** — `<image imageType="fanart screenshot">` fullscreen, NO default
   (blank ⇒ static per-system comic background shows through, which is the final
   fallback). Duotone: `saturation 0` + blue `color` multiply + `opacity ~0.5`,
   so the comic canvas reads through = collage look from the reference.
3. **Physical media** — hero `<image imageType="physicalmedia 3dbox cover">`
   (3 types OK on ImageComponent) + bottom `<carousel imageType="physicalmedia
   3dbox">` (2-type limit) — both with `default`/`defaultImage` =
   `./media_fallbacks/${system.name}.png` (authored per-system cart/disc/card
   silhouettes; final fallback in the user's chain).

## Layout (normalized, 1280x960)

- z1: static per-system background (baked NOVA logo top-left on all systems).
- z2: fanartHero fullscreen duotone wash.
- z5: carousel stage = reused `art/carousel_vignette.png` (1 x 0.375 @ y 0.625).
- z10-19: left panel text inside the baked blue panel (x 0.032–0.19 — fits even
  the narrow gb panel): system pill (`${system.name}`, uppercase), title
  (metadata=name), desc, rows (Last Played / Play Time / Players / Genre /
  Release / Developer as label+value pairs), rating element, game count
  (systemdata gamecountGamesNoText + "GAMES").
- z20/21: marquee fallback text + marquee image, centered (0.52, 0.22),
  maxSize 0.40 x 0.24 — the game takes over the baked system graffiti.
- z25: mediaHero, center-right (0.74, 0.38), maxSize 0.34 x 0.40, rotation -8.
- z50: gameCarousel (primary): pos 0 0.66, size 1 0.27, type horizontal,
  itemSize 0.125 0.13, itemScale 1.3, maxItemCount 7, unfocusedItemDimming 0.5,
  unfocusedItemSaturation 0.7, text colors for artless items.
- z60: helpsystem bottom-left (live on the 7 systems without baked footer;
  hidden per-system on the 14 with).

## Fallback silhouettes (media_fallbacks/)

- Cart: gb gbc gba nes snes n64 genesis megadrive (+ _default)
- Disc: psx ps2 dreamcast xbox xbox360 wii wiiu
- Mini-disc: gc
- UMD: psp
- Card: nds n3ds
- Steam/windows: disc
White-on-transparent duotone shapes drawn in PIL (work/make_media_fallbacks.py).

## Proof

work/proof_gamelist.py renders 1280x960 PIL mocks: full-scrape state + three
fallback states (no marquee / no fanart / no physical media). Inspect before
any release. Nova hardware remains the acceptance gate.
