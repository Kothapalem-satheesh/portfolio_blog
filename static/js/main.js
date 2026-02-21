/* ─────────────────────────────────────────────────────────────
   MAIN.JS — scroll progress · back-to-top · active nav ·
             scroll reveals · skill bars · KPI counters · hamburger
   ───────────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── Hamburger ──────────────────────────────────── */
  const toggle = document.getElementById("nav-toggle");
  const links  = document.getElementById("nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", () => {
      links.classList.toggle("open");
      toggle.classList.toggle("open");
    });
    // Close mobile menu when a link is tapped
    links.querySelectorAll("a").forEach(a => {
      a.addEventListener("click", () => links.classList.remove("open"));
    });
  }

  /* ── Active nav link ─────────────────────────────── */
  const path = window.location.pathname;
  document.querySelectorAll(".nav-links a[data-path]").forEach(a => {
    const p = a.dataset.path;
    // Exact match for home, prefix match for others
    const active = p === "/" ? path === "/" : path.startsWith(p);
    if (active) a.classList.add("nav-active");
  });

  /* ── Scroll progress bar ─────────────────────────── */
  const progressBar = document.getElementById("scroll-progress");
  if (progressBar) {
    const updateProgress = () => {
      const scrollTop    = window.scrollY;
      const docHeight    = document.documentElement.scrollHeight - window.innerHeight;
      const pct          = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      progressBar.style.width = pct + "%";
    };
    window.addEventListener("scroll", updateProgress, { passive: true });
    updateProgress();
  }

  /* ── Back to top button ──────────────────────────── */
  const backBtn = document.getElementById("back-to-top");
  if (backBtn) {
    window.addEventListener("scroll", () => {
      backBtn.classList.toggle("visible", window.scrollY > 400);
    }, { passive: true });
    backBtn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* ── Scroll reveal ──────────────────────────────── */
  const revealEls = document.querySelectorAll(".reveal, .card, .post-row, .timeline-item, .home-post-card");
  if (!reduced) {
    const revealObs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e, i) => {
          if (e.isIntersecting) {
            setTimeout(() => e.target.classList.add("visible"), i * 60);
            revealObs.unobserve(e.target);
          }
        });
      },
      { threshold: 0.06 }
    );
    revealEls.forEach((el) => {
      el.classList.add("reveal");
      revealObs.observe(el);
    });
  } else {
    revealEls.forEach((el) => el.classList.add("visible"));
  }

  /* ── Animated skill bars ────────────────────────── */
  const bars = document.querySelectorAll(".skill-bar-fill");
  if (!reduced && bars.length) {
    const barObs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.style.width = e.target.dataset.level + "%";
            barObs.unobserve(e.target);
          }
        });
      },
      { threshold: 0.3 }
    );
    bars.forEach((b) => barObs.observe(b));
  } else {
    bars.forEach((b) => (b.style.width = b.dataset.level + "%"));
  }

  /* ── KPI counter animation ──────────────────────── */
  const counters = document.querySelectorAll(".kpi-number[data-count]");
  if (!reduced && counters.length) {
    const cntObs = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            const target = parseInt(e.target.dataset.count, 10);
            const suffix = e.target.dataset.suffix !== undefined ? e.target.dataset.suffix : "+";
            let current = 0;
            const step = Math.ceil(target / 30);
            const timer = setInterval(() => {
              current = Math.min(current + step, target);
              e.target.textContent = current + suffix;
              if (current >= target) clearInterval(timer);
            }, 40);
            cntObs.unobserve(e.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    counters.forEach((c) => cntObs.observe(c));
  } else {
    counters.forEach((c) => {
      const suffix = c.dataset.suffix !== undefined ? c.dataset.suffix : "+";
      c.textContent = c.dataset.count + suffix;
    });
  }

  /* ── Typing headline effect ─────────────────────── */
  const subEl = document.getElementById("hero-sub");
  if (subEl && !reduced) {
    const titles = [
      "AI Engineer & Full-Stack Developer",
      "Machine Learning Practitioner",
      "Django Backend Engineer",
      "Python Automation Expert",
    ];
    const original = subEl.textContent.trim() || titles[0];
    titles[0] = original;
    let ti = 0, ci = 0, deleting = false;
    subEl.textContent = "";
    subEl.classList.add("typing-cursor");

    function type() {
      const word = titles[ti % titles.length];
      if (!deleting) {
        subEl.textContent = word.slice(0, ++ci);
        if (ci === word.length) {
          deleting = true;
          return setTimeout(type, 2200);
        }
      } else {
        subEl.textContent = word.slice(0, --ci);
        if (ci === 0) {
          deleting = false;
          ti++;
          return setTimeout(type, 400);
        }
      }
      setTimeout(type, deleting ? 45 : 75);
    }
    setTimeout(type, 800);
  }

  /* ── Hamburger animated bars (X transform) ───────── */
  if (toggle) {
    toggle.addEventListener("click", () => {
      const spans = toggle.querySelectorAll("span");
      const isOpen = links.classList.contains("open");
      spans[0].style.transform = isOpen ? "" : "translateY(7px) rotate(45deg)";
      spans[1].style.opacity   = isOpen ? "" : "0";
      spans[2].style.transform = isOpen ? "" : "translateY(-7px) rotate(-45deg)";
    });
  }
});
