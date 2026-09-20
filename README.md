# Crystal ES-DE Theme v2

A Crystal-Nova-styled theme for [ES-DE](https://es-de.org/) (EmulationStation
Desktop Edition), built for the **new theme engine (ES-DE 2.0+)** — only the
`system` and `gamelist` views, no legacy basic/detailed/video/grid XML.

**v2 adds the Light variant** — a faithful port of the Crystal Frontend's light
theme (cool white / pale grey, dark navy text, deeper blue accents), selectable
in ES-DE under UI Settings -> Appearance -> Theme Variant. Dark stays the
default, so existing installs keep the v1 look with zero action.

- Blue/cyan accents, small yellow/amber focus accents. Never purple.
- 16:9 layout tuned for 1920x1080 (Retroid Pocket 5 and desktop).
- Per-system artwork for 21 systems (backgrounds + logos + 540px carousel icons);
  all other systems fall back gracefully via `${system.name}` variables and default art.
- Light mode draws each white system logo with a pre-rendered drop shadow
  (`ui/shadows/light/`), matching the frontend's CSS drop-shadow treatment.

## Variants (ES-DE native)

Variants are declared in `capabilities.xml` and applied with ES-DE's native
`<variant name="...">` blocks. The **first declared variant is ES-DE's default**,
so `dark` is listed first.

- `variables.xml` holds the dark base palette plus a `<variant name="light">`
  block that overrides the palette, the asset directories, and adds the logo
  shadow element to the system view.
- `views.xml` and all 21 per-system `theme.xml` files reference
  `./${crystalBgDir}/...` and `./${crystalLogoDir}/...` so both variants resolve.
- Steam has no light source artwork: `backgrounds/light/steam.webp` and
  `logos/light/steam.png` are copies of the dark assets, mirroring the
  frontend resolver's light -> dark fallback rule.

## Layout

```
theme-src/
  crystal/                  # <- this folder is zipped as the theme root
    capabilities.xml        # mandatory: themeName + 16:9 + variant declarations
    theme.xml               # root: includes variables.xml + views.xml
    variables.xml           # Crystal palette variables + light <variant> block
    views.xml               # full system + gamelist view layout
    backgrounds/dark/       # per-system 16:9 backgrounds (+ _default.webp fallback)
    backgrounds/light/      # light-variant backgrounds (steam = dark fallback copy)
    logos/dark/             # per-system logos with transparency
    logos/light/            # light-variant logos (steam = dark fallback copy)
    ui/shadows/light/       # pre-rendered logo drop shadows for light mode
    carousel-icons/         # 231 system carousel icons (540x540)
    ui/                     # focus bar + other chrome
    snes/theme.xml          # per-system overrides (explicit asset paths)
    nes/theme.xml
    ... (21 systems)
```

## Build (deterministic)

```sh
./build.sh   # writes dist/crystal-theme-v1.zip
```

The build is byte-identical across runs (sorted entries, fixed timestamps from
`SOURCE_DATE_EPOCH`, fixed permissions, fixed compression). Run it twice and
compare `sha256sum` before publishing.

## Install manually

Unzip so that `crystal/` lands directly in the ES-DE themes folder:

- Linux: `~/.emulationstation/themes/` (or `~/ES-DE/themes/`)
- Android: `[internal storage]/ES-DE/themes/`

then pick **Crystal** in ES-DE's UI Settings.

## Publishing

Releases carry a rolling `stable` tag with:

- `crystal-theme-v1.zip` — the installable theme
- `catalog.json` — consumed by Crystal Nova Manager for one-tap install:

```json
{"id":"crystal","version":"1.0.0","versionCode":1,
 "zipUrl":"https://github.com/ciaranf3308-star/crystal-esde-theme/releases/download/stable/crystal-theme-v1.zip",
 "zipSha256":"<hex>","zipBytes":123,
 "minManagerVersion":"1.2.4-u48-esdeupdate","history":[]}
```

## Art provenance

- `backgrounds/`, `logos/`, `carousel-icons/`: exported from the author's PC
  ES-DE theme (`~/workspace/Crystal-Frontend-Asset-Pack`).
- `backgrounds/dark/steam.webp`: darkened adaptation of the Crystal iiSU pack v1
  steam hero (the pack had no dark steam background).
- `backgrounds/light/`, `logos/light/`: converted from the Crystal Frontend
  light-theme asset pack (backgrounds PNG -> WebP q82; logos kept as PNG).
  The pack had no light steam assets, so the dark steam background/logo are
  reused there (same fallback the frontend itself used: light -> dark).
- `ui/shadows/light/`: generated from the light logos (alpha -> Gaussian blur ->
  dark navy) to replicate the frontend's CSS drop-shadow on white logos.
- `validate.py`: ES-DE ThemeData.cpp-faithful parser check (include order,
  `<name>value</name>` variable syntax, `<variant>` matching incl. the `all`
  rule, capabilities first-declared default, literal placeholder substitution,
  color validation). Run before every publish:
  `python3 validate.py` — must print `RESULT: PASS`.
