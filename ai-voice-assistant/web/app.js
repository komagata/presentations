'use strict';

(async () => {
  const viewer = document.getElementById('viewer');
  const revealElement = viewer.querySelector('.reveal');
  const slideContainer = revealElement.querySelector('.slides');
  const overview = document.getElementById('overview');
  const mode = document.getElementById('view-mode');
  const fullscreen = document.getElementById('fullscreen');
  const message = document.getElementById('message');
  const resources = document.getElementById('resources');

  // Convert legacy links before reveal reads the URL. Named hashes stay native.
  function translateLegacyHash(count) {
    if (!location.hash.startsWith('#slide=')) return null;
    const value = new URLSearchParams(location.hash.slice(1)).get('slide');
    const number = /^-?\d+$/.test(value || '') ? Number(value) : 1;
    const index = Math.max(1, Math.min(count, number)) - 1;
    history.replaceState(null, '', `#/slide-${index + 1}`);
    return index;
  }

  function namedHashIndex(count) {
    const match = location.hash.match(/^#\/slide-(\d+)(?:\/-?\d+)?$/);
    const index = match ? Number(match[1]) - 1 : -1;
    return index >= 0 && index < count ? index : null;
  }

  function createSlide(slide, index) {
    const section = document.createElement('section');
    section.id = `slide-${index + 1}`;
    section.className = 'hype-slide';
    section.setAttribute('aria-label', `Slide ${index + 1}: ${slide.description}`);
    const media = document.createElement(slide.video ? 'video' : 'img');
    media.className = 'slide-media';
    media.setAttribute('data-src', slide.video || slide.image);
    if (slide.video) {
      media.controls = true;
      media.playsInline = true;
      media.preload = 'metadata';
      media.poster = slide.image;
      media.muted = false;
      media.loop = Boolean(slide.loop);
      media.classList.toggle('span', Boolean(slide.span));
      media.setAttribute('aria-label', slide.description);
      media.setAttribute('data-prevent-swipe', '');
      media.append(document.createTextNode('Your browser cannot play this video. '));
      const fallback = document.createElement('a');
      fallback.href = slide.video;
      fallback.textContent = 'Open video directly';
      media.append(fallback);
    } else {
      media.alt = slide.description;
    }
    section.append(media);
    if (slide.overlay_image) {
      const overlay = document.createElement('img');
      overlay.className = 'slide-media overlay';
      overlay.setAttribute('data-src', slide.overlay_image);
      overlay.alt = '';
      overlay.setAttribute('aria-hidden', 'true');
      section.append(overlay);
    }
    const error = document.createElement('p');
    error.className = 'media-error';
    error.hidden = true;
    error.setAttribute('role', 'status');
    error.append(document.createTextNode(slide.video ? 'Video could not be loaded. ' : 'Slide image could not be loaded. '));
    const link = document.createElement('a');
    link.href = slide.video || slide.image;
    link.textContent = slide.video ? 'Open video directly' : 'Open image directly';
    error.append(link);
    section.append(error);
    return section;
  }

  try {
    if (typeof Reveal !== 'function') throw new Error('Presentation library unavailable');
    const response = await fetch('slides.json');
    if (!response.ok) throw new Error(`Manifest request failed (${response.status})`);
    const data = await response.json();
    if (!Array.isArray(data.slides) || data.slides.length !== 30) throw new Error('Invalid slide manifest');
    document.title = `${data.title} · komagata`;
    slideContainer.replaceChildren(...data.slides.map(createSlide));
    const initialIndex = translateLegacyHash(data.slides.length) ?? namedHashIndex(data.slides.length);

    // Capture on the persistent wrapper: scroll view recreates sections on exit.
    revealElement.addEventListener('error', event => {
      const error = event.target.closest('section')?.querySelector('.media-error');
      if (error) error.hidden = false;
    }, true);
    const explicitView = new URLSearchParams(location.search).get('view');
    const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const deck = new Reveal(revealElement, {
      embedded: true,
      width: 1920,
      height: 1080,
      margin: 0,
      minScale: 0.05,
      maxScale: 2,
      center: false,
      touch: true,
      controls: true,
      progress: true,
      slideNumber: 'c/t',
      hash: true,
      history: true,
      overview: true,
      autoPlayMedia: false,
      viewDistance: 1,
      mobileViewDistance: 1,
      view: explicitView === 'scroll' ? 'scroll' : null,
      scrollActivationWidth: ['scroll', 'slide'].includes(explicitView) ? null : 600,
      scrollLayout: 'compact',
      scrollSnap: false,
      scrollProgress: true,
      transition: reducedMotion ? 'none' : 'fade',
      backgroundTransition: 'none',
      keyboardCondition: event => !resources.open && !event.composedPath().some(node =>
        node instanceof Element && (node.matches('video, audio, input, select, textarea, [contenteditable]') ||
          ([' ', 'Enter'].includes(event.key) && node.matches('button, a, summary'))))
    });
    window.slideDeck = deck;

    function updateVideoSizing() {
      revealElement.querySelectorAll('section.hype-slide > video').forEach(video => {
        const { width, height } = video.parentElement.getBoundingClientRect();
        if (width <= 0 || height <= 0 || getComputedStyle(video).visibility === 'hidden') return;
        const scale = width / 1920;
        // Cancel Reveal's scale for native controls, keeping the picture bounds.
        video.style.width = `${1920 * scale}px`;
        video.style.height = `${1080 * scale}px`;
        video.style.transform = `scale(${1 / scale})`;
      });
    }

    let sizingFrame;
    function scheduleVideoSizing() {
      cancelAnimationFrame(sizingFrame);
      sizingFrame = requestAnimationFrame(updateVideoSizing);
    }

    function updateMode() {
      const scrolling = deck.isScrollView();
      mode.textContent = scrolling ? 'Slides' : 'Read';
      mode.setAttribute('aria-label', scrolling ? 'Switch to slide mode' : 'Switch to reading mode');
      overview.hidden = scrolling;
    }

    function alignSlide(index) {
      deck.slide(index, 0);
      if (deck.isScrollView() && index > 0 && index < data.slides.length - 1) {
        // Compact scroll targets a trigger boundary; rounding can select its predecessor.
        viewer.scrollTop += 1;
      }
    }

    function setMode(scrolling) {
      // Pin a manual choice so automatic mobile activation cannot undo it.
      const index = deck.getIndices().h;
      revealElement.querySelectorAll('video').forEach(video => video.pause());
      deck.toggleOverview(false);
      deck.configure({ scrollActivationWidth: null, view: scrolling ? 'scroll' : null });
      deck.toggleScrollView(scrolling);
      alignSlide(index);
      updateMode();
      scheduleVideoSizing();
    }

    deck.on('slidechanged', updateMode);
    deck.on('slidechanged', scheduleVideoSizing);
    deck.on('ready', scheduleVideoSizing);
    deck.on('resize', scheduleVideoSizing);
    // Automatic activation is a viewport class change, including on resize.
    new MutationObserver(() => {
      updateMode();
      scheduleVideoSizing();
    }).observe(viewer, { attributes: true, attributeFilter: ['class'] });
    await deck.initialize();
    // Run after Reveal's native hash listener so it cannot reset the offset.
    window.addEventListener('hashchange', () => {
      const legacyIndex = translateLegacyHash(data.slides.length);
      const index = legacyIndex ?? namedHashIndex(data.slides.length);
      // Reveal also writes hashes during ordinary scrolling: leave those alone.
      if (index !== null && (legacyIndex !== null || index !== deck.getIndices().h)) alignSlide(index);
    });
    if (initialIndex !== null) alignSlide(initialIndex);
    overview.disabled = false;
    mode.disabled = false;
    overview.addEventListener('click', () => deck.toggleOverview());
    mode.addEventListener('click', () => setMode(!deck.isScrollView()));
    updateMode();
    viewer.setAttribute('aria-busy', 'false');
    message.textContent = '';

    if (document.fullscreenEnabled && document.documentElement.requestFullscreen) {
      fullscreen.hidden = false;
      fullscreen.addEventListener('click', async () => {
        resources.open = false;
        try {
          if (document.fullscreenElement) await document.exitFullscreen();
          else await document.documentElement.requestFullscreen();
        } catch (_) {
          message.textContent = 'Fullscreen is unavailable. You can continue using the viewer here.';
        }
      });
      document.addEventListener('fullscreenchange', () => {
        fullscreen.textContent = document.fullscreenElement ? 'Exit fullscreen' : 'Fullscreen';
      });
    }
    document.addEventListener('click', event => {
      if (!resources.contains(event.target)) resources.open = false;
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && resources.open) {
        resources.open = false;
        resources.querySelector('summary').focus();
      }
    });
  } catch (_) {
    viewer.setAttribute('aria-busy', 'false');
    message.textContent = 'The presentation could not be loaded. Please reload the page.';
  }
})();
