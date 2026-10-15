# Omarchy Meetup Tokyo Night — Opening web viewer

Seven 1920×1080 slides follow the source Hype Markdown, in order: opening video,
meetup introduction, Tokyo Night title, ANDPAD beer sponsor, OPTiM venue and meal
sponsor, pixel-art welcome, and schedule. Slides 2–7 are the exact Hype renders.
The first image is a real first-frame video poster, not Hype's missing-media
placeholder. No transparent overlay is needed.

Slide 1 uses the original `videos/omarchy-meetup.mp4` with native controls,
`span`, `loop`, `muted`, and `autoplay` all true. Reveal owns playback: the visible
video starts muted, pauses on departure, and can play again when revisited.
The shared AI viewer keeps its two videos audible and manually started.

## Shared viewer and preview

This deck declares `data-slide-count="7"` and reuses the pinned Reveal library,
CSS, and JavaScript at the deployed sibling `../ai-voice-assistant/`. Do not
publish this source directory alone or open its HTML directly from disk.

From the repository root:

```sh
python3 -m unittest discover -s tools -p 'test_*.py'
python3 tools/build_pages.py
python3 -m http.server 8000 --directory _site
```

Preview `http://localhost:8000/omarchy-meetup3-opening/` in an Omabox browser.
The Pages URL is `https://komagata.github.io/presentations/omarchy-meetup3-opening/`.
The catalog links directly to this deck. The source Markdown, PDF, raw renderer
metadata, and unused images are excluded from the built site.

The shared viewer supports arrows, swipes, overview (**O** / **Esc**), fullscreen
(**F**), mobile scroll mode, `?view=scroll`, `?view=slide`, native controls, and
named links `#/slide-1` through `#/slide-7`. Legacy `#slide=7` links also work.
See [AI viewer controls](../../ai-voice-assistant/web/README.md) for details.

## Regenerate the committed assets

Use the installed Hype and Tokyo Night theme. Follow the Omabox skill and run
these Hype commands **inside Omabox**, with this checkout available. Rendering
opens a Qt surface. The source uses 16:9 slides, producing 1920×1080 PNGs:

```sh
hype check omarchy-meetup3-opening/omarchy-meetup3-opening-talk.md
hype render omarchy-meetup3-opening/omarchy-meetup3-opening-talk.md --width 1920 --output /tmp/opening-render
```

Check that Hype reports seven slides and no errors. It resolves bare image
filenames within the deck's image directory; the source paths need no repair.
Render into a temporary directory so absolute-path renderer metadata never
enters the repository. From the repository root, copy only slides 2–7:

```sh
python3 - <<'PY'
from pathlib import Path
import shutil
source = Path('/tmp/opening-render')
target = Path('omarchy-meetup3-opening/web/slides')
for number in range(2, 8):
    name = f'slide-{number:03}.png'
    shutil.copyfile(source / name, target / name)
PY
```

Recreate the video poster from the original MP4's first frame; Hype's rendered
`slide-001.png` is a missing-poster placeholder. This ffmpeg step is headless:

```sh
ffmpeg -y -i omarchy-meetup3-opening/videos/omarchy-meetup.mp4 -frames:v 1 -vf scale=1920:1080 omarchy-meetup3-opening/web/slides/slide-001.png
```

The committed `web/slides.json` is the portable manifest. Retain its title and
seven descriptions, reviewing them against the refreshed images. Every image
must be `slides/slide-NNN.png` in source order. Only the first slide has a video,
with `video: "videos/omarchy-meetup.mp4"` and `span`, `loop`, `muted`, `autoplay`
set to JSON `true`. Other slides contain only `image` and `description`. Do not
copy the renderer's `slides.json`, absolute video paths, warnings, poster field,
or entirely transparent `overlay-1.png`. No conversion of renderer metadata is
needed when using the committed portable manifest.

Run the tests and build above after regeneration. CI only packages these
committed assets offline; it never invokes Hype or ffmpeg. Browser acceptance
and publication are coordinator steps.
