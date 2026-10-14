# AI Voice Assistant web viewer

The viewer uses the 30 committed Hype PNGs to preserve slide typography and order.
Videos on slides 10 and 12 are copied from the two named source MP4 files during
packaging. Playback starts through native controls with audio enabled; leaving a
video slide pauses/unloads it, and returning starts from the beginning. No external
runtime library, analytics, or account is required.

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
overlays, and the two selected videos. Missing/unsafe references fail the build.
No Markdown, tests, README, PDF/PPTX exports, or validation output is published.
Default output is `_site/`; `--output PATH` selects another build directory.

## GitHub Pages

A coordinator must enable **Settings → Pages → Source: GitHub Actions** for
`komagata/presentations`, then push the reviewed files to `main` or run the
**Deploy presentations to Pages** workflow manually. Actions uses the committed
PNGs and Python stdlib; it does not render with Hype. The public viewer URL is:

https://komagata.github.io/presentations/ai-voice-assistant/

A direct slide link appends `#slide=10`. Browser back/forward restores the selected
slide. Relative local links support the `/presentations/` Pages subpath. Pages
configuration, publication, and desktop/mobile browser acceptance are separate
coordinator steps, not performed by this implementation worker.
