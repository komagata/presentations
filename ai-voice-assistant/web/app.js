'use strict';

(async () => {
  const viewer = document.getElementById('viewer');
  const stage = document.getElementById('stage');
  const previous = document.getElementById('previous');
  const next = document.getElementById('next');
  const selector = document.getElementById('slide-select');
  const counter = document.getElementById('counter');
  const fullscreen = document.getElementById('fullscreen');
  const message = document.getElementById('message');
  const description = document.getElementById('description');
  let slides;
  let current = -1;
  let activeVideo = null;
  let nextImage = null;

  function readHash() {
    const value = new URLSearchParams(location.hash.slice(1)).get('slide');
    const number = value && /^-?\d+$/.test(value) ? Number(value) : 1;
    return Math.max(1, Math.min(slides.length, number)) - 1;
  }

  function render(index) {
    if (index === current) return;
    if (activeVideo) {
      activeVideo.pause();
      activeVideo.removeAttribute('src');
      activeVideo.load();
      activeVideo = null;
    }
    current = index;
    stage.replaceChildren();
    stage.setAttribute('aria-busy', 'true');
    message.textContent = '';
    const slide = slides[index];
    description.textContent = slide.description;
    stage.setAttribute('aria-label', `Slide ${index + 1} of ${slides.length}`);
    if (slide.video) {
      const video = document.createElement('video');
      video.controls = true;
      video.playsInline = true;
      video.preload = 'metadata';
      video.poster = slide.image;
      video.muted = false;
      video.loop = Boolean(slide.loop);
      video.classList.toggle('span', Boolean(slide.span));
      video.setAttribute('aria-label', slide.description);
      video.append(document.createTextNode('Your browser cannot play this video.'));
      video.addEventListener('loadedmetadata', () => {
        if (activeVideo === video) stage.setAttribute('aria-busy', 'false');
      });
      video.addEventListener('error', () => {
        if (activeVideo !== video) return;
        stage.setAttribute('aria-busy', 'false');
        message.replaceChildren(document.createTextNode('Video could not be loaded. '));
        const link = document.createElement('a');
        link.href = slide.video;
        link.textContent = 'Open video directly';
        message.append(link);
      });
      activeVideo = video;
      video.src = slide.video;
      stage.append(video);
      if (slide.overlay_image) {
        const overlay = document.createElement('img');
        overlay.src = slide.overlay_image;
        overlay.alt = '';
        overlay.className = 'overlay';
        overlay.setAttribute('aria-hidden', 'true');
        stage.append(overlay);
      }
      message.textContent = 'Press Play in the video controls. Audio is enabled.';
    } else {
      const image = document.createElement('img');
      image.alt = slide.description;
      image.addEventListener('load', () => {
        if (current === index) stage.setAttribute('aria-busy', 'false');
      });
      image.addEventListener('error', () => {
        if (current !== index) return;
        stage.setAttribute('aria-busy', 'false');
        message.textContent = 'Slide image could not be loaded. Please reload or select another slide.';
      });
      image.src = slide.image;
      stage.append(image);
    }
    previous.disabled = index === 0;
    next.disabled = index === slides.length - 1;
    selector.value = String(index + 1);
    counter.textContent = `${index + 1} / ${slides.length}`;
    // Only the next slide image is prefetched; video sources are attached on selection.
    nextImage = null;
    if (slides[index + 1]) {
      nextImage = new Image();
      nextImage.src = slides[index + 1].image;
    }
  }

  function navigate(index) {
    index = Math.max(0, Math.min(slides.length - 1, index));
    if (index === current) return;
    location.hash = `slide=${index + 1}`;
  }

  function syncHash() {
    const index = readHash();
    const canonical = `#slide=${index + 1}`;
    if (location.hash !== canonical) history.replaceState(null, '', canonical);
    render(index);
  }

  try {
    const response = await fetch('slides.json');
    if (!response.ok) throw new Error(`Manifest request failed (${response.status})`);
    const data = await response.json();
    if (!Array.isArray(data.slides) || data.slides.length !== 30) throw new Error('Invalid slide manifest');
    slides = data.slides;
    document.title = `${data.title} · komagata`;
    selector.replaceChildren(...slides.map((slide, index) => {
      const option = document.createElement('option');
      option.value = String(index + 1);
      option.textContent = `${index + 1}. ${slide.description}`;
      return option;
    }));
    selector.disabled = false;
    previous.addEventListener('click', () => navigate(current - 1));
    next.addEventListener('click', () => navigate(current + 1));
    selector.addEventListener('change', () => navigate(Number(selector.value) - 1));
    window.addEventListener('hashchange', syncHash);
    document.addEventListener('keydown', (event) => {
      if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
      // Video shadow controls target the video host; preserve native seeking/volume keys.
      if (event.composedPath().some(node => node instanceof Element && node.matches('input, select, textarea, video, [contenteditable]'))) return;
      const destinations = { ArrowLeft: current - 1, ArrowRight: current + 1, Home: 0, End: slides.length - 1 };
      if (Object.hasOwn(destinations, event.key)) {
        event.preventDefault();
        navigate(destinations[event.key]);
      }
    });
    if (document.fullscreenEnabled && viewer.requestFullscreen) {
      fullscreen.hidden = false;
      fullscreen.addEventListener('click', async () => {
        try {
          if (document.fullscreenElement) await document.exitFullscreen();
          else await viewer.requestFullscreen();
        } catch (_) {
          message.textContent = 'Fullscreen is unavailable. You can continue using the viewer here.';
        }
      });
      document.addEventListener('fullscreenchange', () => {
        const label = document.fullscreenElement ? 'Exit fullscreen' : 'Enter fullscreen';
        fullscreen.textContent = label;
        fullscreen.setAttribute('aria-label', label);
      });
    }
    syncHash();
  } catch (_) {
    stage.setAttribute('aria-busy', 'false');
    counter.textContent = 'Presentation unavailable';
    message.textContent = 'The presentation could not be loaded. Please reload the page. For a local preview, serve the generated _site folder over HTTP.';
  }
})();
