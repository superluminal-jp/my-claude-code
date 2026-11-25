// Keyboard paging for the slide format. Without this script the slides still
// scroll and print; it adds keys and keeps the slide number in the URL.
// A classic script, not a module: browsers refuse to load a module from a
// file:// page, and the slides are meant to open without a server.
(() => {
const slides = Array.from(document.querySelectorAll(".slide"));
let current = 0;

const go = (index) => {
  const target = slides[Math.max(0, Math.min(slides.length - 1, index))];
  target?.scrollIntoView({ block: "center" });
};

const observer = new IntersectionObserver(
  (entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      current = slides.indexOf(entry.target);
      history.replaceState(null, "", `#${current + 1}`);
    }
  },
  { threshold: 0.6 },
);
for (const slide of slides) observer.observe(slide);

const keys = {
  ArrowRight: () => go(current + 1),
  ArrowDown: () => go(current + 1),
  PageDown: () => go(current + 1),
  " ": () => go(current + 1),
  ArrowLeft: () => go(current - 1),
  ArrowUp: () => go(current - 1),
  PageUp: () => go(current - 1),
  Home: () => go(0),
  End: () => go(slides.length - 1),
};

document.addEventListener("keydown", (event) => {
  if (event.altKey || event.ctrlKey || event.metaKey) return;
  if (event.target.closest("a, button, input, select, textarea, summary")) return;
  const action = keys[event.key];
  if (!action) return;
  event.preventDefault();
  action();
});

const fromHash = Number.parseInt(location.hash.slice(1), 10);
if (fromHash >= 1) go(fromHash - 1);
})();
