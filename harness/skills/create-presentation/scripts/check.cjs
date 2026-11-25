#!/usr/bin/env node
// Open presentation files in a headless browser and report what a reader
// would see wrong: content cut off at the edge of a slide, a tree diagram
// that has to scroll, a page that scrolls sideways on a phone, a file that
// failed to load, a script error.
//
// Usage: node check.cjs [--screenshots <dir>] <file.html>...
// A file with elements of class "slide" is checked as the slide format, any
// other file as the page format.
// Exit status: 0 no problem, 1 problems found, 2 the check could not run.

const path = require("node:path");
const fs = require("node:fs");
const { pathToFileURL } = require("node:url");

const SLIDE_VIEWPORTS = [
  [1280, 720],
  [1920, 1080],
  [1000, 900],
];
const PAGE_VIEWPORTS = [
  [390, 800],
  [1280, 720],
];
// Sub-pixel rounding at a scaled root font size is not an overflow.
const TOLERANCE = 1;

function parseArgs(argv) {
  const files = [];
  let shots = null;
  for (let i = 0; i < argv.length; i += 1) {
    if (argv[i] === "--screenshots") {
      shots = argv[i + 1];
      i += 1;
    } else {
      files.push(argv[i]);
    }
  }
  return { files, shots };
}

async function open(browser, file, [width, height], problems) {
  const page = await browser.newPage({ viewport: { width, height } });
  const label = `${path.basename(file)} at ${width}x${height}`;
  page.on("pageerror", (error) => problems.push(`${label}: script error: ${error.message}`));
  page.on("requestfailed", (request) => {
    // A font that cannot be fetched offline changes the typeface, not the
    // structure; a local file that is missing breaks the page.
    if (request.url().startsWith("file:")) {
      problems.push(`${label}: could not load ${request.url()}`);
    }
  });
  await page.goto(pathToFileURL(file).href);
  await page.evaluate(() => document.fonts.ready);
  return { page, label };
}

async function checkSlides(browser, file, problems, shots) {
  for (const viewport of SLIDE_VIEWPORTS) {
    const { page, label } = await open(browser, file, viewport, problems);
    const result = await page.evaluate(() => {
      const slides = [...document.querySelectorAll(".slide")];
      return slides.map((slide) => {
        const box = slide.getBoundingClientRect();
        let over = 0;
        for (const element of slide.querySelectorAll("*")) {
          const rect = element.getBoundingClientRect();
          if (rect.width === 0 || rect.height === 0) continue;
          over = Math.max(over, rect.bottom - box.bottom, rect.right - box.right);
        }
        const clipped = [...slide.querySelectorAll(".deck-tree")].some(
          (tree) => tree.scrollWidth > tree.clientWidth + 1 || tree.scrollHeight > tree.clientHeight + 1,
        );
        return { over, clipped };
      });
    });
    result.forEach(({ over, clipped }, index) => {
      if (over > TOLERANCE) {
        problems.push(`${label}: slide ${index + 1} content runs ${Math.round(over)}px past the slide`);
      }
      if (clipped) {
        problems.push(`${label}: slide ${index + 1} has a tree diagram that does not fit and scrolls`);
      }
    });
    if (shots && viewport === SLIDE_VIEWPORTS[0]) {
      const slides = page.locator(".slide");
      for (let i = 0; i < result.length; i += 1) {
        const name = `${path.basename(file, ".html")}-${String(i + 1).padStart(2, "0")}.png`;
        await slides.nth(i).screenshot({ path: path.join(shots, name) });
      }
    }
    await page.close();
  }
}

async function checkPage(browser, file, problems, shots) {
  for (const viewport of PAGE_VIEWPORTS) {
    const { page, label } = await open(browser, file, viewport, problems);
    const sideways = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    if (sideways > TOLERANCE) {
      problems.push(`${label}: the page scrolls sideways by ${Math.round(sideways)}px`);
    }
    if (shots) {
      const name = `${path.basename(file, ".html")}-${viewport[0]}.png`;
      await page.screenshot({ path: path.join(shots, name), fullPage: true });
    }
    await page.close();
  }
}

async function main() {
  const { files, shots } = parseArgs(process.argv.slice(2));
  if (files.length === 0) {
    console.error("Usage: node check.cjs [--screenshots <dir>] <file.html>...");
    return 2;
  }
  for (const file of files) {
    if (!fs.existsSync(file)) {
      console.error(`No such file: ${file}`);
      return 2;
    }
  }
  let chromium;
  try {
    ({ chromium } = require("playwright"));
  } catch {
    console.error("Playwright is not installed, so the check did not run.");
    return 2;
  }
  let browser;
  try {
    browser = await chromium.launch();
  } catch (error) {
    console.error(`The browser did not start, so the check did not run: ${error.message}`);
    return 2;
  }
  if (shots) fs.mkdirSync(shots, { recursive: true });
  const problems = [];
  try {
    for (const file of files) {
      const absolute = path.resolve(file);
      const isSlides = /class="slide"|class="slide /.test(fs.readFileSync(absolute, "utf8"));
      if (isSlides) await checkSlides(browser, absolute, problems, shots);
      else await checkPage(browser, absolute, problems, shots);
    }
  } finally {
    await browser.close();
  }
  for (const problem of problems) console.log(`FAIL ${problem}`);
  if (problems.length > 0) {
    console.log(`${problems.length} problem(s)`);
    return 1;
  }
  console.log(`OK ${files.length} file(s)`);
  return 0;
}

main().then(
  (status) => process.exit(status),
  (error) => {
    console.error(error);
    process.exit(2);
  },
);
