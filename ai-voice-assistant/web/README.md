# AI Voice Assistant web viewer

The viewer uses the 30 committed Hype PNGs to preserve slide typography and order.
The viewer runs actual reveal.js 6.0.2 from the pinned local files in
`vendor/reveal/`; it needs no CDN, npm install, analytics, or account. Videos on
slide 11 (OMA-PV.mp4) and slide 13 (the Japanese introduction) are copied from
the two named source MP4 files during packaging.
Playback starts through native controls with audio enabled. Reveal pauses media
on slide departure and lazy loads nearby media. Returning to a distant video may
reload it.

## Viewing modes and controls

Desktop defaults to slides filling the browser viewport, with no header, menus,
buttons, slide counters, arrows or progress indicators. The complete 16:9 slide
image is contained without cropping; other viewport shapes can have empty space.
Arrow keys navigate; Home/End jump to the first/last slide, and swiping navigates
in slide mode. **O** or **Esc** opens the overview, and **F** enters fullscreen
when supported. Native video controls keep their seeking/volume keys and touch
gestures.
Video elements cancel Reveal's slide scale so native controls stay at viewport
pixel size while the picture keeps its original slide bounds. Sizing is refreshed
after initialization, slide changes, resizing and viewing mode changes, including
the sections Reveal recreates when leaving scroll mode. Images and overlays keep
their original slide scaling.

At widths up to 600px, Reveal automatically uses its vertical scroll view with
`scrollLayout: 'compact'` and continuous full-width scrolling without snapping or
a slide progress indicator. Multiple 16:9 slides fit in a continuous page.
Overview is available in slide mode.
`?view=scroll` and `?view=slide` explicitly select a mode at any viewport width.
Reduced motion disables slide transitions.

Direct links use `#/slide-10` (IDs `slide-1` through `slide-30`). Legacy `#slide=10`
links are translated before initialization and on subsequent hash changes;
legacy invalid numbers default to 1 or clamp to the 1–30 range. Reveal owns named
hash navigation and browser back/forward. The actual instance is exposed as
`window.slideDeck` for acceptance checks.
Requested initial links and hash changes use an explicit
vertical index of zero. In compact scroll mode, interior slides receive a 1px
offset into their scroll trigger to avoid rounding onto the previous slide.
Ordinary scrolling and its Reveal-generated hash updates are left to Reveal.

## Refresh rendered slides

Use the same installed Hype version and Tokyo Night theme as the source deck. Run
Hype rendering inside Omabox, following the local Omabox skill (rendering opens a
GUI/Qt surface). With this checkout available in the container, run:

```sh
hype render 'ai-voice-assistant/AI Voice Assistant.md' --width 1920 --output ai-voice-assistant/web/slides
```

Then, from the repository root:

```sh
python3 tools/prepare_manifest.py
```

The conversion reads the Hype `web/slides/slides.json` and source Markdown, removes
source comments, supplies descriptions for visual slides, and writes portable
`web/slides.json`. It also replaces the renderer metadata with portable JSON so no
absolute poster/video paths remain. The latter file is not published. Video
references use `videos/<basename>`; only the two expected video names are accepted.
After conversion, review descriptions against refreshed visuals. Image-only
slides have explicit descriptions in `tools/prepare_manifest.py`.

## Build and preview

```sh
python3 -m unittest discover -s tools -p 'test_*.py'
python3 tools/build_pages.py
node --check ai-voice-assistant/web/app.js
python3 -m http.server 8000 --directory _site
```

Preview `http://localhost:8000/ai-voice-assistant/` using a browser in Omabox.
Preview the generated `_site`, rather than opening the source HTML as `file://`:
the viewer fetches its manifest, and video URLs exist only in the built artifact.
The build contains only an index and the viewer, its manifest, referenced PNGs,
overlays, the two selected videos, and the four explicitly allowlisted Reveal
library/license files. Additional vendor files are excluded. Missing/unsafe references fail the build.
No Markdown, tests, README, PDF/PPTX exports, or validation output is published.
Default output is `_site/`; `--output PATH` selects another build directory.

## GitHub Pages

A coordinator must enable **Settings → Pages → Source: GitHub Actions** for
`komagata/presentations`, then push the reviewed files to `main` or run the
**Deploy presentations to Pages** workflow manually. Actions uses the committed
PNGs and Python stdlib; it does not render with Hype. The public viewer URL is:

https://komagata.github.io/presentations/ai-voice-assistant/

A direct slide link appends `#/slide-10`; old `#slide=10` links still work.
Browser back/forward restores the selected slide. Relative local links support the `/presentations/` Pages subpath. Pages
configuration, publication, and desktop/mobile browser acceptance are separate
coordinator steps, not performed by this implementation worker.

## Upstream reference

- [Reveal media and lazy loading](https://revealjs.com/media/)
- [Scroll view and compact layout](https://revealjs.com/scroll-view/)
- [Overview](https://revealjs.com/overview/)
- [Keyboard](https://revealjs.com/keyboard/)
- [Configuration](https://revealjs.com/config/)

Library provenance is recorded in `vendor/reveal/README.md`.
