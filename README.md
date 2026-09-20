# Crystal ES-DE Theme v1

A dark, Crystal-Nova-styled theme for [ES-DE](https://es-de.org/) (EmulationStation
Desktop Edition), built for the **new theme engine (ES-DE 2.0+)** — only the
`system` and `gamelist` views, no legacy basic/detailed/video/grid XML.

- Deep blue/black backgrounds, cyan accents, small yellow focus accents. Never purple.
- 16:9 layout tuned for 1920x1080 (Retroid Pocket 5 and desktop).
- Per-system artwork for 21 systems (backgrounds + logos + 540px carousel icons);
  all other systems fall back gracefully via `${system.name}` variables and default art.

## Layout

```
theme-src/
  crystal/                  # <- this folder is zipped as the theme root
    capabilities.xml        # mandatory: themeName + 16:9 aspect ratio
    theme.xml               # root: includes variables.xml + views.xml
    variables.xml           # Crystal palette variables
    views.xml               # full system + gamelist view layout
    backgrounds/dark/       # per-system 16:9 backgrounds (+ _default.webp fallback)
    logos/dark/             # per-system logos with transparency
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
