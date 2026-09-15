/*
 * Slide extractor: reads a laid-out deck in the browser and returns the
 * intermediate representation the PowerPoint builder consumes.
 *
 * It runs inside the page, so every number it reports is a measured layout
 * value rather than a guess about how CSS would resolve. Geometry stays in CSS
 * pixels; the builder converts with the exact factors 1px = 0.75pt = 9525 EMU.
 *
 * Classification is automatic. `data-pptx` on an element overrides it:
 *   text | shape | image | table | raster | notes | ignore
 *
 * Contract: defines window.__extractDeck(options) -> deck IR.
 */

(() => {
  const MEDIA_TAGS = new Set(['IMG', 'SVG', 'CANVAS', 'VIDEO', 'IFRAME', 'OBJECT', 'PICTURE']);
  const TRANSPARENT = /^rgba\(0,\s*0,\s*0,\s*0\)$|^transparent$/;

  const isTransparent = (color) => !color || TRANSPARENT.test(color.replace(/\s+/g, ' '));

  function parseColor(value) {
    if (isTransparent(value)) return null;
    const m = value.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const parts = m[1].split(',').map((p) => parseFloat(p));
    const [r, g, b] = parts;
    const a = parts.length > 3 ? parts[3] : 1;
    if (a === 0) return null;
    const hex = [r, g, b]
      .map((c) => Math.round(Math.max(0, Math.min(255, c))).toString(16).padStart(2, '0'))
      .join('');
    return { hex: hex.toUpperCase(), alpha: a, rgb: [r, g, b] };
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

  function effectiveBackground(el) {
    let node = el;
    while (node && node.nodeType === 1) {
      const color = parseColor(getComputedStyle(node).backgroundColor);
      if (color && color.alpha >= 0.95) return color.rgb;
      node = node.parentElement;
    }
    return [255, 255, 255];
  }

  const rectOf = (el, origin) => {
    const r = el.getBoundingClientRect();
    return { x: r.left - origin.left, y: r.top - origin.top, w: r.width, h: r.height };
  };

  /* The content box: what a PowerPoint text frame with zero insets must cover. */
  function contentRect(el, origin) {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    const l = parseFloat(cs.borderLeftWidth) + parseFloat(cs.paddingLeft);
    const t = parseFloat(cs.borderTopWidth) + parseFloat(cs.paddingTop);
    const rr = parseFloat(cs.borderRightWidth) + parseFloat(cs.paddingRight);
    const bb = parseFloat(cs.borderBottomWidth) + parseFloat(cs.paddingBottom);
    return {
      x: r.left - origin.left + l,
      y: r.top - origin.top + t,
      w: Math.max(0, r.width - l - rr),
      h: Math.max(0, r.height - t - bb),
    };
  }

  /* Horizontal padding box, vertical content box: a list keeps room for its
     markers (which live in the padding) without gaining a vertical offset. */
  function listFrameRect(el, origin) {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    const content = contentRect(el, origin);
    const l = parseFloat(cs.borderLeftWidth);
    const rr = parseFloat(cs.borderRightWidth);
    return {
      x: r.left - origin.left + l,
      y: content.y,
      w: Math.max(0, r.width - l - rr),
      h: content.h,
    };
  }

  const isListContainer = (el) =>
    (el.tagName === 'UL' || el.tagName === 'OL') && el.querySelector(':scope > li') !== null;

  const isRendered = (el) => {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) return false;
    const r = el.getBoundingClientRect();
    return r.width > 0.5 && r.height > 0.5;
  };

  const hasText = (el) => (el.textContent || '').trim().length > 0;

  const override = (el) => el.getAttribute('data-pptx');

  /* A child element that generates a block-level box in normal flow. */
  function blockKids(el) {
    return Array.from(el.children).filter((kid) => {
      if (!isRendered(kid)) return false;
      const d = getComputedStyle(kid).display;
      return !d.startsWith('inline') || d === 'inline-block';
    });
  }

  const borderSides = (cs) => ['Top', 'Right', 'Bottom', 'Left'].map((side) => ({
    side: side.toLowerCase(),
    width: parseFloat(cs[`border${side}Width`]) || 0,
    style: cs[`border${side}Style`],
    color: parseColor(cs[`border${side}Color`]),
  }));

  function decoration(el) {
    const cs = getComputedStyle(el);
    const fill = parseColor(cs.backgroundColor);
    const borders = borderSides(cs).filter((b) => b.width > 0 && b.style !== 'none' && b.color);
    if (!fill && borders.length === 0) return null;
    return {
      fill: fill ? fill.hex : null,
      borders,
      radius: parseFloat(cs.borderTopLeftRadius) || 0,
    };
  }

  const hasMedia = (el) =>
    MEDIA_TAGS.has(el.tagName) || el.querySelector('img, svg, canvas, video, iframe, object, table') !== null;

  const hasOverrideInside = (el) => el.querySelector('[data-pptx]') !== null;

  /*
   * Flex and grid gaps are not margins, so PowerPoint cannot reproduce them
   * inside one text frame. Such a container is decomposed into one frame per
   * child, each placed at its measured rectangle, instead of being grouped.
   */
  function groupable(el) {
    const cs = getComputedStyle(el);
    if (/flex|grid/.test(cs.display) && blockKids(el).length > 1) return false;
    return true;
  }

  function canBeOneTextFrame(el) {
    if (!hasText(el) || hasMedia(el) || hasOverrideInside(el)) return false;
    if (!groupable(el)) return false;
    const kids = blockKids(el);
    if (kids.length === 0) return true;
    return kids.every((kid) => !decoration(kid) && canBeOneTextFrame(kid));
  }

  /* Inline runs, each carrying the character formatting actually applied. */
  function runsOf(el) {
    const runs = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let node = walker.nextNode();
    while (node) {
      const text = node.nodeValue.replace(/\s+/g, ' ');
      if (text.trim().length > 0) {
        const parent = node.parentElement;
        const cs = getComputedStyle(parent);
        const color = parseColor(cs.color);
        runs.push({
          text,
          size_px: parseFloat(cs.fontSize),
          bold: parseInt(cs.fontWeight, 10) >= 600,
          italic: cs.fontStyle === 'italic',
          underline: cs.textDecorationLine.includes('underline'),
          strike: cs.textDecorationLine.includes('line-through'),
          color: color ? color.hex : '000000',
          font: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(),
          letter_spacing_px: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing) || 0,
        });
      }
      node = walker.nextNode();
    }
    /* Merge adjacent runs that carry identical formatting. */
    return runs.reduce((acc, run) => {
      const prev = acc[acc.length - 1];
      const same =
        prev &&
        ['size_px', 'bold', 'italic', 'underline', 'strike', 'color', 'font', 'letter_spacing_px'].every(
          (k) => prev[k] === run[k],
        );
      if (same) prev.text += run.text;
      else acc.push(run);
      return acc;
    }, []);
  }

  function lineCount(el, cs) {
    const line = lineHeightPx(cs);
    if (!(line > 0)) return 1;
    const r = el.getBoundingClientRect();
    const inner =
      r.height -
      (parseFloat(cs.paddingTop) || 0) -
      (parseFloat(cs.paddingBottom) || 0) -
      (parseFloat(cs.borderTopWidth) || 0) -
      (parseFloat(cs.borderBottomWidth) || 0);
    return Math.max(1, Math.round(inner / line));
  }

  function lineHeightPx(cs) {
    const lh = parseFloat(cs.lineHeight);
    if (Number.isFinite(lh)) return lh;
    return parseFloat(cs.fontSize) * 1.2;
  }

  /* Where the text of a list item actually starts, so the hanging indent and
     the marker gap survive conversion instead of being approximated. */
  function textStartLeft(el) {
    const range = document.createRange();
    range.selectNodeContents(el);
    const r = range.getBoundingClientRect();
    range.detach?.();
    return r.width > 0 ? r.left : el.getBoundingClientRect().left;
  }

  function markerOf(el) {
    const parent = el.parentElement;
    if (!parent) return null;
    const tag = parent.tagName;
    if (tag !== 'UL' && tag !== 'OL') return null;
    if (tag === 'OL') return { kind: 'number' };
    const style = getComputedStyle(parent).listStyleType;
    if (style === 'none') return { kind: 'none' };
    const chars = { disc: '•', circle: '◦', square: '▪' };
    return { kind: 'char', char: chars[style] || '•' };
  }

  /* One paragraph per text-leaf block, in document order. */
  function paragraphsOf(el, frameLeft) {
    const kids = blockKids(el);
    if (kids.length === 0) {
      const cs = getComputedStyle(el);
      const runs = runsOf(el);
      if (runs.length === 0) return [];
      const marker = markerOf(el);
      const bulleted = marker !== null && marker.kind !== 'none';
      return [
        {
          runs,
          align: cs.textAlign,
          line_px: lineHeightPx(cs),
          space_before_px: parseFloat(cs.paddingTop) || 0,
          space_after_px: parseFloat(cs.paddingBottom) || 0,
          lines: lineCount(el, cs),
          marker,
          indent_px: textStartLeft(el) - frameLeft,
          /* A bullet hangs at the left edge of the frame, which for a list is
             the padding box — the strip the browser draws its marker in. */
          box_left_px: bulleted ? 0 : el.getBoundingClientRect().left - frameLeft,
        },
      ];
    }
    const out = [];
    kids.forEach((kid, i) => {
      const cs = getComputedStyle(kid);
      const nested = paragraphsOf(kid, frameLeft);
      if (nested.length === 0) return;
      nested[0].space_before_px += i === 0 ? 0 : parseFloat(cs.marginTop) || 0;
      nested[nested.length - 1].space_after_px += parseFloat(cs.marginBottom) || 0;
      out.push(...nested);
    });
    return out;
  }

  function anchorOf(el) {
    const cs = getComputedStyle(el);
    if (/flex/.test(cs.display) && cs.flexDirection.startsWith('column')) {
      if (cs.justifyContent === 'center') return 'middle';
      if (/end/.test(cs.justifyContent)) return 'bottom';
    }
    return 'top';
  }

  function tableOf(el, origin) {
    const rows = Array.from(el.querySelectorAll('tr')).filter(isRendered);
    if (rows.length === 0) return null;
    const grid = rows.map((tr) => {
      const cells = Array.from(tr.children).filter((c) => /^(TD|TH)$/.test(c.tagName));
      return cells.map((cell) => {
        const cs = getComputedStyle(cell);
        const fill = parseColor(cs.backgroundColor);
        const borders = borderSides(cs).filter((b) => b.width > 0 && b.style !== 'none' && b.color);
        return {
          text: (cell.textContent || '').trim(),
          runs: runsOf(cell),
          lines: lineCount(cell, cs),
          header: cell.tagName === 'TH',
          colspan: cell.colSpan || 1,
          rowspan: cell.rowSpan || 1,
          align: cs.textAlign,
          fill: fill && fill.alpha >= 0.95 ? fill.hex : null,
          borders,
          pad: {
            l: parseFloat(cs.paddingLeft) || 0,
            r: parseFloat(cs.paddingRight) || 0,
            t: parseFloat(cs.paddingTop) || 0,
            b: parseFloat(cs.paddingBottom) || 0,
          },
        };
      });
    });
    const widest = rows.reduce((best, tr) => {
      const n = Array.from(tr.children).reduce((sum, c) => sum + (c.colSpan || 1), 0);
      return n > best.n ? { n, tr } : best;
    }, { n: 0, tr: rows[0] });
    const colWidths = [];
    Array.from(widest.tr.children).forEach((cell) => {
      const w = cell.getBoundingClientRect().width;
      const span = cell.colSpan || 1;
      for (let i = 0; i < span; i += 1) colWidths.push(w / span);
    });
    return {
      rect: rectOf(el, origin),
      rows: grid,
      col_widths_px: colWidths,
      row_heights_px: rows.map((tr) => tr.getBoundingClientRect().height),
    };
  }

  function altTextOf(el) {
    if (el.tagName === 'IMG') return el.getAttribute('alt');
    const labelled = el.getAttribute('aria-label');
    if (labelled) return labelled;
    const by = el.getAttribute('aria-labelledby');
    if (by) {
      const target = document.getElementById(by);
      if (target) return (target.textContent || '').trim();
    }
    const title = el.querySelector(':scope > title');
    return title ? (title.textContent || '').trim() : null;
  }

  function extractSlide(slideEl, index, options, findings) {
    const origin = slideEl.getBoundingClientRect();
    const shapes = [];
    let rasterSeq = 0;

    const notesEl = slideEl.querySelector('[data-pptx="notes"], .sld-notes');
    const notes = notesEl
      ? (notesEl.textContent || '').trim()
      : (slideEl.getAttribute('data-notes') || '').trim();

    const report = (level, code, message, el) => {
      findings.push({
        slide: index + 1,
        level,
        code,
        message,
        element: el ? `${el.tagName.toLowerCase()}${el.className ? `.${String(el.className).trim().split(/\s+/).join('.')}` : ''}` : null,
        text: el ? (el.textContent || '').trim().slice(0, 60) : null,
      });
    };

    const checkBounds = (el, rect) => {
      const eps = 0.5;
      if (rect.x < -eps || rect.y < -eps || rect.x + rect.w > origin.width + eps || rect.y + rect.h > origin.height + eps) {
        report('error', 'off-slide', 'Content extends past the slide edge and will be cut off.', el);
      } else if (
        rect.x < options.safe_area_px - eps ||
        rect.y < options.safe_area_px - eps ||
        rect.x + rect.w > origin.width - options.safe_area_px + eps ||
        rect.y + rect.h > origin.height - options.safe_area_px + eps
      ) {
        report('warn', 'safe-area', `Content sits within ${options.safe_area_px}px of the slide edge.`, el);
      }
    };

    const checkText = (el, paragraphs) => {
      if (el.scrollHeight > el.clientHeight + 1 || el.scrollWidth > el.clientWidth + 1) {
        report('error', 'clipped', 'Text does not fit its box and is clipped.', el);
      }
      const bg = effectiveBackground(el);
      /* Secondary content — footers, captions, eyebrows, tile labels — is
         allowed the dense type scale. Body copy is not. */
      const secondary = el.closest(options.secondary_selector) !== null;
      paragraphs.forEach((p) => {
        p.runs.forEach((run) => {
          if (run.size_px < options.min_font_px) {
            report('error', 'font-too-small', `${run.size_px}px is below the ${options.min_font_px}px floor.`, el);
          } else if (!secondary && run.size_px < options.body_font_px) {
            report('warn', 'font-small', `${run.size_px}px is hard to read when projected.`, el);
          }
          const fg = [
            parseInt(run.color.slice(0, 2), 16),
            parseInt(run.color.slice(2, 4), 16),
            parseInt(run.color.slice(4, 6), 16),
          ];
          const large = run.size_px >= 24 || (run.size_px >= 18.66 && run.bold);
          const required = large ? 3 : 4.5;
          const ratio = contrastRatio(fg, bg);
          if (ratio < required) {
            report('error', 'contrast', `Contrast ${ratio.toFixed(2)}:1 is below the required ${required}:1.`, el);
          }
        });
      });
    };

    /* ::before and ::after have no DOM node and no measurable box, so anything
       they paint is invisible to the converter. Say so rather than dropping it. */
    const checkPseudoDecoration = (el) => {
      ['::before', '::after'].forEach((pseudo) => {
        const cs = getComputedStyle(el, pseudo);
        if (!cs || cs.content === 'none' || cs.content === 'normal') return;
        const paints =
          !isTransparent(cs.backgroundColor) ||
          borderSides(cs).some((b) => b.width > 0 && b.style !== 'none') ||
          /^["']/.test(cs.content) ||
          cs.content.includes('url(');
        if (paints) {
          report('warn', 'pseudo-decoration', `${pseudo} paints content that cannot be converted; use a real element.`, el);
        }
      });
    };

    const emitRaster = (el) => {
      rasterSeq += 1;
      const id = `s${index + 1}r${rasterSeq}`;
      el.setAttribute('data-pptx-id', id);
      const rect = rectOf(el, origin);
      const alt = altTextOf(el);
      if (!alt) {
        report('warn', 'no-alt', 'Rasterized content has no text alternative (alt, aria-label or <title>).', el);
      }
      checkBounds(el, rect);
      shapes.push({ kind: 'raster', id, rect, alt: alt || '' });
    };

    const walk = (el) => {
      Array.from(el.children).forEach((kid) => {
        if (kid === notesEl) return;
        const mode = override(kid);
        if (mode === 'ignore' || mode === 'notes') return;
        if (!isRendered(kid)) return;

        if (mode === 'raster' || (!mode && (kid.tagName === 'SVG' || kid.tagName === 'CANVAS' || kid.tagName === 'VIDEO'))) {
          emitRaster(kid);
          return;
        }

        if (mode === 'image' || (!mode && kid.tagName === 'IMG')) {
          const rect = rectOf(kid, origin);
          const alt = altTextOf(kid);
          if (alt === null || alt === undefined) {
            report('error', 'no-alt', 'Image has no alt attribute.', kid);
          }
          checkBounds(kid, rect);
          shapes.push({ kind: 'image', rect, src: kid.currentSrc || kid.src, alt: alt || '', id: null });
          return;
        }

        if (mode === 'table' || (!mode && kid.tagName === 'TABLE')) {
          const table = tableOf(kid, origin);
          if (table) {
            checkBounds(kid, table.rect);
            shapes.push({ kind: 'table', ...table });
          }
          return;
        }

        checkPseudoDecoration(kid);

        const deco = decoration(kid);
        if (deco) {
          const rect = rectOf(kid, origin);
          checkBounds(kid, rect);
          shapes.push({ kind: 'shape', rect, ...deco });
        }

        if (mode === 'text' || (!mode && canBeOneTextFrame(kid))) {
          const rect = isListContainer(kid) ? listFrameRect(kid, origin) : contentRect(kid, origin);
          const frameLeft = origin.left + rect.x;
          const paragraphs = paragraphsOf(kid, frameLeft);
          if (paragraphs.length > 0) {
            checkText(kid, paragraphs);
            shapes.push({
              kind: 'text',
              rect,
              anchor: anchorOf(kid),
              /* Every paragraph fit on one line here; re-wrapping it in
                 PowerPoint under different font metrics would be wrong. */
              wrap: paragraphs.some((p) => p.lines > 1),
              paragraphs,
            });
          }
          return;
        }

        if (hasText(kid) || kid.children.length > 0) walk(kid);
        else if (!deco) {
          report('warn', 'dropped', 'Element produced no convertible content.', kid);
        }
      });
    };

    walk(slideEl);

    const messageEl = slideEl.querySelector('[data-role="message"], .sld-message, h1, h2');
    if (!messageEl || !hasText(messageEl)) {
      report('warn', 'no-message', 'Slide states no governing message (.sld-message, h1 or h2).', slideEl);
    }

    const listItems = slideEl.querySelectorAll('li').length;
    if (listItems > options.max_list_items) {
      report('warn', 'dense', `${listItems} list items exceeds the ${options.max_list_items}-item limit for one slide.`, slideEl);
    }

    const slideBg = parseColor(getComputedStyle(slideEl).backgroundColor);
    return {
      index: index + 1,
      layout: slideEl.getAttribute('data-layout') || 'custom',
      title: messageEl ? (messageEl.textContent || '').trim() : '',
      background: slideBg ? slideBg.hex : 'FFFFFF',
      notes,
      shapes,
    };
  }

  window.__extractDeck = (options) => {
    const opts = Object.assign(
      {
        safe_area_px: 32,
        min_font_px: 14,
        body_font_px: 18,
        max_list_items: 7,
        slide_selector: '.sld-slide, [data-slide]',
        secondary_selector:
          'footer, figcaption, caption, small, [data-role="meta"], .sld-eyebrow, .sld-card__label, .sld-kpi__label, .sld-steps__index',
      },
      options || {},
    );
    const slideEls = Array.from(document.querySelectorAll(opts.slide_selector));
    const findings = [];
    if (slideEls.length === 0) {
      return { deck: null, slides: [], findings: [{ slide: 0, level: 'error', code: 'no-slides', message: `No element matched ${opts.slide_selector}.`, element: null, text: null }] };
    }
    const first = slideEls[0].getBoundingClientRect();
    slideEls.forEach((el, i) => {
      const r = el.getBoundingClientRect();
      if (Math.abs(r.width - first.width) > 1 || Math.abs(r.height - first.height) > 1) {
        findings.push({
          slide: i + 1,
          level: 'error',
          code: 'size-mismatch',
          message: `Slide is ${Math.round(r.width)}x${Math.round(r.height)}px but slide 1 is ${Math.round(first.width)}x${Math.round(first.height)}px.`,
          element: null,
          text: null,
        });
      }
    });
    const slides = slideEls.map((el, i) => extractSlide(el, i, opts, findings));
    return {
      deck: {
        width_px: first.width,
        height_px: first.height,
        title: document.title || '',
        lang: document.documentElement.lang || '',
      },
      slides,
      findings,
    };
  };
})();
