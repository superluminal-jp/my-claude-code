/*
 * Deck checker: reads a laid-out HTML deck in the browser and returns what
 * breaks the deck's structure, the document's accessibility, or a slide's
 * legibility.
 *
 * It runs inside the page, so every number it reports is a measured layout
 * value rather than a guess about how CSS would resolve.
 *
 * Contract: defines window.__checkDeck(options) -> { deck, slides, findings }.
 * A finding is { slide, level: "error" | "warn", code, message, element, text };
 * slide 0 means the finding is about the whole document.
 */

(() => {
  const TRANSPARENT = /^rgba\(0,\s*0,\s*0,\s*0\)$|^transparent$/;

  const isTransparent = (color) => !color || TRANSPARENT.test(color.replace(/\s+/g, ' '));

  /* HTML elements report an upper-case tagName; SVG elements report their
     qualified name verbatim ('svg', 'text', 'rect'). Compare through this. */
  const tagOf = (el) => (el.tagName || '').toUpperCase();

  /* SVG's className is an SVGAnimatedString, which stringifies to
     "[object SVGAnimatedString]" in a finding. */
  const classOf = (el) =>
    typeof el.className === 'string' ? el.className : el.getAttribute('class') || '';

  const SENTINEL = '#1b2c3d';
  let swatch = null;

  /*
   * rgb()/rgba() is the fast path. Anything else — oklch(), color-mix(),
   * color(srgb …) — is handed to the canvas, which converts whatever CSS the
   * browser accepted. Returning null for an unreadable colour matters: the
   * caller must report it rather than check a value nobody wrote.
   */
  function parseColor(value) {
    if (isTransparent(value)) return null;
    const m = String(value).match(/rgba?\(([^)]+)\)/);
    if (m) {
      const parts = m[1].split(/[,\s/]+/).filter(Boolean).map(parseFloat);
      const a = parts.length > 3 ? parts[3] : 1;
      if (a === 0) return null;
      return { alpha: a, rgb: parts.slice(0, 3) };
    }
    if (!swatch) {
      swatch = document.createElement('canvas').getContext('2d', { willReadFrequently: true });
    }
    swatch.fillStyle = SENTINEL;
    swatch.fillStyle = value;
    if (swatch.fillStyle === SENTINEL && String(value).trim().toLowerCase() !== SENTINEL) return null;
    swatch.globalCompositeOperation = 'copy';
    swatch.fillRect(0, 0, 1, 1);
    const [r, g, b, a255] = swatch.getImageData(0, 0, 1, 1).data;
    const alpha = a255 / 255;
    if (alpha === 0) return null;
    return { alpha, rgb: [r, g, b] };
  }

  const relativeLuminance = ([r, g, b]) => {
    const f = (c) => {
      const s = c / 255;
      return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
    };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };

  const contrastRatio = (a, b) => {
    const [l1, l2] = [relativeLuminance(a), relativeLuminance(b)].sort((x, y) => y - x);
    return (l1 + 0.05) / (l2 + 0.05);
  };

  const composite = (fg, bg, alpha) => fg.map((c, i) => c * alpha + bg[i] * (1 - alpha));

  /*
   * Resolve what a pixel of background actually is. A translucent layer has to
   * be composited, not skipped — skipping one reports the colour behind it and
   * silently passes text that is unreadable. Under a gradient or an image there
   * is no single answer, so return null and let the caller report that.
   */
  function effectiveBackground(el) {
    const stack = [];
    let node = el;
    while (node && node.nodeType === 1) {
      const cs = getComputedStyle(node);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
      const color = parseColor(cs.backgroundColor);
      if (color) {
        if (color.alpha >= 0.999) {
          return stack.reduceRight((bg, layer) => composite(layer.rgb, bg, layer.alpha), color.rgb);
        }
        stack.push(color);
      }
      node = node.parentElement;
    }
    return stack.reduceRight((bg, layer) => composite(layer.rgb, bg, layer.alpha), [255, 255, 255]);
  }

  const rectOf = (el, origin) => {
    const r = el.getBoundingClientRect();
    return { x: r.left - origin.left, y: r.top - origin.top, w: r.width, h: r.height };
  };

  /* Anything inside a display:none subtree has an empty box, so this also
     skips speaker notes and everything else that is not rendered. */
  const isRendered = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0.5 && r.height > 0.5;
  };

  const hasText = (el) => (el.textContent || '').trim().length > 0;

  /* Text the element itself paints, as opposed to text its children paint. */
  const ownsText = (el) =>
    Array.from(el.childNodes).some((node) => node.nodeType === 3 && node.nodeValue.trim().length > 0);

  const borderSides = (cs) => ['Top', 'Right', 'Bottom', 'Left'].map((side) => ({
    side: side.toLowerCase(),
    width: parseFloat(cs[`border${side}Width`]) || 0,
    style: cs[`border${side}Style`],
    color: parseColor(cs[`border${side}Color`]),
  }));

  const visibleBorders = (cs) => borderSides(cs).filter((b) => b.width > 0 && b.style !== 'none' && b.color);

  const isDecorated = (cs) => parseColor(cs.backgroundColor) !== null || visibleBorders(cs).length > 0;

  function accessibleName(el) {
    if (tagOf(el) === 'IMG') return el.getAttribute('alt');
    const labelled = el.getAttribute('aria-label');
    if (labelled) return labelled;
    const by = el.getAttribute('aria-labelledby');
    if (by) {
      const text = by
        .split(/\s+/)
        .map((id) => document.getElementById(id))
        .filter(Boolean)
        .map((target) => (target.textContent || '').trim())
        .join(' ')
        .trim();
      if (text) return text;
    }
    const title = el.querySelector(':scope > title');
    return title ? (title.textContent || '').trim() : null;
  }

  const describe = (el) =>
    el ? `${tagOf(el).toLowerCase()}${classOf(el) ? `.${classOf(el).trim().split(/\s+/).join('.')}` : ''}` : null;

  function checkDocument(opts, report) {
    const lang = (document.documentElement.getAttribute('lang') || '').trim();
    if (!lang) {
      report(0, 'error', 'no-lang', 'The <html> element declares no lang, so assistive technology cannot pick a voice.', null);
    }
    if (!(document.title || '').trim()) {
      report(0, 'error', 'no-title', 'The document has no <title>; it should state the deck\'s subject, as its h1 does.', null);
    }

    /* The design system's heading guidance: the h1 is the page's subject, and
       a heading level is never skipped. */
    const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).filter(
      (h) => isRendered(h) && hasText(h),
    );
    const h1s = headings.filter((h) => tagOf(h) === 'H1');
    if (h1s.length !== 1) {
      report(0, 'error', 'h1-count', `The document has ${h1s.length} h1 elements; it needs exactly one, on the cover.`, null);
    }
    let previous = 0;
    headings.forEach((h) => {
      const level = Number(tagOf(h).slice(1));
      if (level > previous + 1) {
        const slide = h.closest(opts.slide_selector);
        report(
          slide ? slideNumber.get(slide) || 0 : 0,
          'error',
          'heading-skip',
          `An h${level} follows ${previous ? `an h${previous}` : 'no heading'}; heading levels must not be skipped.`,
          h,
        );
      }
      previous = level;
    });
  }

  const slideNumber = new Map();

  function checkStructure(slides, opts, report) {
    const roles = slides.map((s) => s.layout);
    const main = roles.filter((role) => role !== 'appendix');
    if (opts.max_slides && main.length > opts.max_slides) {
      report(
        0,
        'warn',
        'deck-long',
        `The main deck has ${main.length} slides, above the ${opts.max_slides}-slide limit set for this occasion. Cut a branch of the tree or move it to the appendix.`,
        null,
      );
    }
    const answerAt = roles.indexOf('answer') + 1;
    if (answerAt === 0 || answerAt > 3) {
      report(
        answerAt || 0,
        'warn',
        'late-answer',
        answerAt === 0
          ? 'No slide has data-layout="answer"; the conclusion must come by slide 3.'
          : `The answer is on slide ${answerAt}; it must come by slide 3, after the cover and the premises.`,
        null,
      );
    }
    let appendixSeen = false;
    roles.forEach((role, i) => {
      if (role === 'appendix') appendixSeen = true;
      else if (appendixSeen) {
        report(i + 1, 'warn', 'appendix-order', 'A main slide follows an appendix slide; the appendix goes after the main deck.', null);
      }
    });
  }

  /*
   * The tracker lists the main deck's parts after the cover and marks the
   * slide's own part. A slide with data-continues carries on the part of the
   * slide before it, so a point that runs over several slides is one part. A tracker that marks the wrong part tells the audience they are
   * somewhere they are not, so it is an error; a slide that drops a tracker
   * the rest of the deck carries is a lapse in consistency.
   */
  function checkTrackers(slideEls, slides, report) {
    if (!slideEls.some((el) => el.querySelector('.sld-tracker'))) return;
    const tracked = slides.filter((s) => s.layout !== 'title' && s.layout !== 'appendix');
    const position = new Map();
    let parts = 0;
    tracked.forEach((s) => {
      if (!(s.continues && parts > 0)) parts += 1;
      position.set(s.index, parts - 1);
    });
    slideEls.forEach((el, i) => {
      const n = i + 1;
      if (!position.has(n)) return;
      const tracker = el.querySelector('.sld-tracker');
      if (!tracker) {
        report(n, 'warn', 'tracker-missing', 'The other main slides show where they sit in the deck; this one does not.', el);
        return;
      }
      const items = Array.from(tracker.querySelectorAll(':scope > li'));
      const marked = items
        .map((li, k) => (li.hasAttribute('aria-current') && li.getAttribute('aria-current') !== 'false' ? k : -1))
        .filter((k) => k >= 0);
      if (items.length !== parts) {
        report(n, 'error', 'tracker', `The tracker lists ${items.length} parts, but the main deck after the cover has ${parts}.`, tracker);
      } else if (marked.length !== 1 || marked[0] !== position.get(n)) {
        const said = marked.length === 1 ? `part ${marked[0] + 1}` : `${marked.length} parts`;
        report(n, 'error', 'tracker', `The tracker marks ${said} as current, but this slide is part ${position.get(n) + 1}.`, tracker);
      }
    });
  }

  /*
   * The classification marking states how the information must be handled.
   * A page without it, or with a different one, can be handled wrongly once
   * printed or forwarded on its own, so every slide carries the same marking
   * at its top right. The level's meaning is the organisation's policy, not
   * this checker's; only its form is checked.
   */
  const LEVELS = ['1', '2', '3'];
  const FULL_WIDTH = { 1: '１', 2: '２', 3: '３' };

  function checkMarkings(slideEls, report) {
    const marks = slideEls.map((el) =>
      Array.from(el.querySelectorAll('.sld-marking')).find((m) => isRendered(m)) || null,
    );
    if (marks.every((m) => m === null)) {
      report(0, 'error', 'marking-missing', 'No slide carries a classification marking (機密性 and 公開範囲).', null);
      return;
    }
    const normalise = (m) => (m.textContent || '').replace(/\s+/g, ' ').trim();
    const first = marks.find((m) => m !== null);
    marks.forEach((m, i) => {
      const n = i + 1;
      const slideEl = slideEls[i];
      if (m === null) {
        report(n, 'error', 'marking-missing', 'This slide carries no classification marking; every slide must.', slideEl);
        return;
      }
      const level = m.getAttribute('data-level') || '';
      const levelText = ((m.querySelector('.sld-marking__level') || {}).textContent || '').trim();
      const scope = m.querySelector('.sld-marking__scope');
      const origin = slideEl.getBoundingClientRect();
      const box = m.getBoundingClientRect();
      let problem = null;
      if (!LEVELS.includes(level)) {
        problem = `data-level="${level}" is not 1, 2 or 3.`;
      } else if (!levelText.includes(level) && !levelText.includes(FULL_WIDTH[level])) {
        problem = `The marking reads "${levelText}" but data-level is ${level}.`;
      } else if (!scope || !hasText(scope)) {
        problem = 'The marking states no 公開範囲.';
      } else if (normalise(m) !== normalise(first) || level !== first.getAttribute('data-level')) {
        problem = `The marking differs from the first slide's ("${normalise(first)}"); one deck carries one classification.`;
      } else if (box.left - origin.left < origin.width / 2 || box.top - origin.top > 64) {
        problem = 'The marking is not at the top right of the slide.';
      }
      if (problem) report(n, 'error', 'marking', problem, m);
    });
  }

  function checkSlide(slideEl, n, opts, report) {
    const origin = slideEl.getBoundingClientRect();
    const at = (level, code, message, el) => report(n, level, code, message, el);

    const heading = Array.from(slideEl.querySelectorAll('h1, h2')).find((h) => isRendered(h) && hasText(h));
    if (!heading) {
      at('error', 'no-heading', 'The slide has no h1 or h2, so it states no assertion and has no place in the outline.', slideEl);
    }

    const checkBounds = (el) => {
      const rect = rectOf(el, origin);
      const eps = 0.5;
      if (rect.x < -eps || rect.y < -eps || rect.x + rect.w > origin.width + eps || rect.y + rect.h > origin.height + eps) {
        at('error', 'off-slide', 'Content extends past the slide edge and is cut off.', el);
      } else if (
        rect.x < opts.safe_area_px - eps ||
        rect.y < opts.safe_area_px - eps ||
        rect.x + rect.w > origin.width - opts.safe_area_px + eps ||
        rect.y + rect.h > origin.height - opts.safe_area_px + eps
      ) {
        at('warn', 'safe-area', `Content sits within ${opts.safe_area_px}px of the slide edge.`, el);
      }
    };

    /*
     * The Digital Agency's colour foundation removes WCAG's large-text
     * relaxation: every piece of text clears 4.5:1 against its background
     * whatever its size.
     */
    const checkText = (el, size, color) => {
      const secondary = el.closest(opts.secondary_selector) !== null;
      if (size < opts.min_font_px) {
        at('error', 'font-too-small', `${size.toFixed(1)}px is below the ${opts.min_font_px}px floor.`, el);
      } else if (!secondary && size < opts.body_font_px) {
        at('warn', 'font-small', `${size.toFixed(1)}px is hard to read when projected.`, el);
      }
      const bg = effectiveBackground(el);
      if (bg === null || color === null) {
        at('warn', 'contrast-unknown', 'Contrast cannot be computed: the text sits on a gradient or image, or its colour did not resolve.', el);
        return;
      }
      const ratio = contrastRatio(color.rgb, bg);
      if (ratio < opts.text_contrast) {
        at('error', 'contrast', `Contrast ${ratio.toFixed(2)}:1 is below the required ${opts.text_contrast}:1.`, el);
      }
    };

    /* Text inside an inline SVG is drawn at the SVG's scale, on whatever shape
       is painted under it, so check it at that size and against that fill. */
    const checkSvgText = (svg) => {
      const box = svg.getBoundingClientRect();
      const view = svg.viewBox && svg.viewBox.baseVal;
      const scale = view && view.width > 0 ? box.width / view.width : 1;
      const painted = Array.from(svg.querySelectorAll('rect, circle, ellipse, path, polygon'));
      Array.from(svg.querySelectorAll('text')).forEach((node) => {
        if (!hasText(node)) return;
        const cs = getComputedStyle(node);
        const size = (parseFloat(cs.fontSize) || 0) * scale;
        if (size > 0 && size < opts.min_font_px) {
          at('error', 'font-too-small', `${size.toFixed(1)}px of figure text is below the ${opts.min_font_px}px floor.`, svg);
        }
        const fg = parseColor(cs.fill);
        if (!fg) return;
        const rect = node.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        let behind = null;
        painted.forEach((shape) => {
          const r = shape.getBoundingClientRect();
          if (cx >= r.left && cx <= r.right && cy >= r.top && cy <= r.bottom) {
            const fill = parseColor(getComputedStyle(shape).fill);
            if (fill && fill.alpha >= 0.999) behind = fill.rgb;
          }
        });
        const bg = behind || effectiveBackground(svg) || [255, 255, 255];
        const ratio = contrastRatio(fg.rgb, bg);
        if (ratio < opts.text_contrast) {
          at('error', 'contrast', `Figure label "${node.textContent.trim().slice(0, 14)}" is ${ratio.toFixed(2)}:1, below ${opts.text_contrast}:1.`, svg);
        }
      });
    };

    Array.from(slideEl.querySelectorAll('*')).forEach((el) => {
      if (el.ownerSVGElement) return; /* handled through its root <svg> */
      if (!isRendered(el)) return;
      const tag = tagOf(el);
      const cs = getComputedStyle(el);

      if (tag === 'IMG') {
        if (accessibleName(el) === null) at('error', 'no-alt', 'Image has no alt attribute. A decorative image takes alt="".', el);
        checkBounds(el);
        return;
      }
      if (tag === 'SVG') {
        if (el.getAttribute('aria-hidden') !== 'true') {
          if (!accessibleName(el)) {
            at('error', 'no-alt', 'SVG has no accessible name (aria-label, aria-labelledby or <title>), and is not aria-hidden.', el);
          }
          checkSvgText(el);
        }
        checkBounds(el);
        return;
      }
      if (tag === 'TABLE') {
        if (!el.querySelector('th')) {
          at('error', 'table-no-header', 'Table has no <th>, so no cell is announced with its column or row.', el);
        }
        checkBounds(el);
      }

      const text = ownsText(el);
      const decorated = isDecorated(cs);
      /* An inline box is as tall as its font's ascent and descent, which can
         exceed the line it sits on; the block that lays out its line is the
         box that has to fit, so that is the one measured. */
      if (cs.display !== 'inline' && (hasText(el) || decorated)) checkBounds(el);
      if (text) checkText(el, parseFloat(cs.fontSize), parseColor(cs.color));

      /* Only an element that actually clips can clip. A padded inline
         highlight legitimately overflows its line box and clips nothing. */
      const clips = cs.overflow !== 'visible' || cs.overflowX !== 'visible' || cs.overflowY !== 'visible';
      if (clips && hasText(el) && (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1)) {
        at('error', 'clipped', 'Text does not fit its box and is clipped.', el);
      }

      /*
       * A border or rule that separates content needs 3:1 against what
       * surrounds it (WCAG 1.4.11). A table's own grid is the official
       * component's business, so it is left alone.
       */
      if (decorated && !el.closest('table')) {
        const bg = effectiveBackground(el.parentElement || el);
        if (bg !== null) {
          const weak = visibleBorders(cs)
            .map((border) => ({ side: border.side, ratio: contrastRatio(border.color.rgb, bg) }))
            .filter((border) => border.ratio < opts.nontext_contrast);
          if (weak.length > 0) {
            const sides = weak.map((border) => `${border.side} ${border.ratio.toFixed(2)}:1`).join(', ');
            at('warn', 'nontext-contrast', `Border below ${opts.nontext_contrast}:1 against its background (${sides}).`, el);
          }
        }
      }
    });

    /* Two groups of five can be compared; one list of ten cannot. So the
       per-list limit and the pooled per-slide limit are separate checks. The
       tracker states position, not content to hold in mind, so it is not
       counted. */
    const content = (el) => isRendered(el) && !el.closest('.sld-tracker');
    slideEl.querySelectorAll('ul, ol').forEach((list) => {
      if (!content(list)) return;
      const own = Array.from(list.children).filter((kid) => tagOf(kid) === 'LI').length;
      if (own > opts.max_list_items) {
        at('warn', 'dense', `${own} items in one list exceeds the ${opts.max_list_items}-item limit.`, list);
      }
    });
    const listItems = Array.from(slideEl.querySelectorAll('li')).filter(content).length;
    if (listItems > opts.max_slide_items) {
      at('warn', 'dense', `${listItems} list items on one slide exceeds the ${opts.max_slide_items}-item limit.`, slideEl);
    }

    return {
      index: n,
      layout: slideEl.getAttribute('data-layout') || 'custom',
      continues: slideEl.hasAttribute('data-continues'),
      title: heading ? (heading.textContent || '').trim().replace(/\s+/g, ' ') : '',
    };
  }

  window.__checkDeck = (options) => {
    const opts = Object.assign(
      {
        safe_area_px: 32,
        min_font_px: 14,
        body_font_px: 18,
        max_list_items: 5,
        max_slide_items: 10,
        max_slides: null,
        text_contrast: 4.5,
        nontext_contrast: 3,
        slide_selector: '.sld-slide',
        secondary_selector:
          'footer, figcaption, caption, small, .dads-heading__shoulder, .dads-chip-label, .sld-kpi__label, .sld-steps__index, .sld-tracker, .sld-marking',
      },
      options || {},
    );
    const findings = [];
    const report = (slide, level, code, message, el) => {
      findings.push({ slide, level, code, message, element: describe(el), text: el ? (el.textContent || '').trim().slice(0, 60) : null });
    };

    const slideEls = Array.from(document.querySelectorAll(opts.slide_selector));
    slideEls.forEach((el, i) => slideNumber.set(el, i + 1));
    checkDocument(opts, report);
    if (slideEls.length === 0) {
      report(0, 'error', 'no-slides', `No element matched ${opts.slide_selector}.`, null);
      return { deck: null, slides: [], findings };
    }

    const first = slideEls[0].getBoundingClientRect();
    slideEls.forEach((el, i) => {
      const r = el.getBoundingClientRect();
      if (Math.abs(r.width - first.width) > 1 || Math.abs(r.height - first.height) > 1) {
        report(
          i + 1,
          'error',
          'size-mismatch',
          `Slide is ${Math.round(r.width)}x${Math.round(r.height)}px but slide 1 is ${Math.round(first.width)}x${Math.round(first.height)}px.`,
          null,
        );
      }
    });
    const slides = slideEls.map((el, i) => checkSlide(el, i + 1, opts, report));
    checkStructure(slides, opts, report);
    checkTrackers(slideEls, slides, report);
    checkMarkings(slideEls, report);
    findings.sort((a, b) => a.slide - b.slide);

    return {
      deck: {
        width_px: first.width,
        height_px: first.height,
        title: document.title || '',
        lang: document.documentElement.getAttribute('lang') || '',
      },
      slides,
      findings,
    };
  };
})();
