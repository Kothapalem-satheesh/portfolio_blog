/* ─────────────────────────────────────────────────────────────
   ANIMATIONS.JS
   • 3-D card tilt on hover
   • Magnetic button effect
   • Floating section particles
   • Shimmer trail on cursor
   • Animated section orbs
   ───────────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ── 3-D Tilt on cards ──────────────────────────────────── */
  if (!reduced) {
    const TILT_CARDS = document.querySelectorAll(
      ".proj-card, .blog-card, .home-post-card, .card.focus-card, .card.kpi, .achievement-card, .timeline-card"
    );
    TILT_CARDS.forEach(card => {
      card.addEventListener("mousemove", e => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width  - 0.5;
        const y = (e.clientY - r.top)  / r.height - 0.5;
        card.style.transform = `
          perspective(700px)
          rotateX(${-y * 7}deg)
          rotateY(${x * 7}deg)
          translateY(-4px)
          scale(1.015)
        `;
        card.style.transition = "transform 0.08s ease";
      });
      card.addEventListener("mouseleave", () => {
        card.style.transform = "";
        card.style.transition = "transform 0.45s ease";
      });
    });
  }

  /* ── Magnetic buttons ────────────────────────────────────── */
  if (!reduced) {
    document.querySelectorAll(".btn, .cta-banner .btn").forEach(btn => {
      btn.addEventListener("mousemove", e => {
        const r = btn.getBoundingClientRect();
        const x = (e.clientX - r.left - r.width  / 2) * 0.25;
        const y = (e.clientY - r.top  - r.height / 2) * 0.25;
        btn.style.transform = `translate(${x}px, ${y}px) translateY(-2px)`;
        btn.style.transition = "transform 0.1s ease";
      });
      btn.addEventListener("mouseleave", () => {
        btn.style.transform = "";
        btn.style.transition = "transform 0.4s ease";
      });
    });
  }

  /* ── Floating section particles ─────────────────────────── */
  function spawnSectionParticles(section, count = 18) {
    for (let i = 0; i < count; i++) {
      const dot = document.createElement("span");
      dot.className = "section-particle";
      dot.style.cssText = `
        left:  ${Math.random() * 100}%;
        top:   ${Math.random() * 100}%;
        width: ${1 + Math.random() * 2.5}px;
        height: ${1 + Math.random() * 2.5}px;
        animation-delay:    ${Math.random() * 8}s;
        animation-duration: ${6 + Math.random() * 8}s;
        opacity: ${0.1 + Math.random() * 0.3};
      `;
      section.appendChild(dot);
    }
  }

  if (!reduced) {
    document.querySelectorAll(".section").forEach(s => {
      s.style.position = "relative";
      s.style.overflow = "hidden";
      spawnSectionParticles(s, 16);
    });
  }

  /* ── Glowing cursor trail (desktop only) ────────────────── */
  if (!reduced && window.innerWidth > 768) {
    const trail = document.getElementById("cursor-trail");
    if (trail) {
      let tx = 0, ty = 0, cx = 0, cy = 0;
      document.addEventListener("mousemove", e => { tx = e.clientX; ty = e.clientY; });
      (function move() {
        cx += (tx - cx) * 0.14;
        cy += (ty - cy) * 0.14;
        trail.style.transform = `translate(${cx - 10}px, ${cy - 10}px)`;
        requestAnimationFrame(move);
      })();
    }
  }

  /* ── Staggered children animate-in ─────────────────────── */
  if (!reduced) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => {
        if (!e.isIntersecting) return;
        const children = e.target.querySelectorAll(
          ".proj-card, .blog-card, .card, .home-post-card, .achievement-card, .timeline-item, .tech-cloud-badge"
        );
        children.forEach((c, i) => {
          c.style.transitionDelay = `${i * 55}ms`;
          c.classList.add("visible");
        });
        io.unobserve(e.target);
      });
    }, { threshold: 0.05 });

    document.querySelectorAll(".proj-grid, .blog-grid, .cards, .home-posts-grid, .achievements-grid, .tech-cloud, .kpi-grid")
      .forEach(el => io.observe(el));
  }

  /* ── Number ticker on KPI numbers (already in main.js,    ─ */
  /* ── this adds a color-shift glow when it hits target)    ─ */
  document.querySelectorAll(".kpi-number").forEach(el => {
    const obs = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) {
        setTimeout(() => el.classList.add("kpi-done"), 1400);
        obs.disconnect();
      }
    }, { threshold: 0.8 });
    obs.observe(el);
  });

  /* ── Hero photo pulse ring ───────────────────────────────── */
  const ring = document.querySelector(".hero-photo-ring");
  if (ring && !reduced) {
    ring.classList.add("hero-ring-anim");
  }

  /* ── Lottie-style inline SVG animations activate ────────── */
  document.querySelectorAll(".lottie-inline").forEach(el => {
    el.classList.add("lottie-play");
  });
});
