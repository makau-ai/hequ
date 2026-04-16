// Shared background starfield for hequ.ai/discovery sub-pages.
// Sparse, slow, no distraction. Installs a fixed canvas behind
// all content and paints twinkling stars plus two distant slow-
// drifting constellations.
(function () {
  const canvas = document.getElementById('starfield');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, DPR;
  let stars = [];
  let rings = [];
  let t = 0;

  function resize() {
    DPR = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth;
    H = window.innerHeight;
    canvas.width = W * DPR;
    canvas.height = H * DPR;
    canvas.style.width = W + 'px';
    canvas.style.height = H + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    // Rebuild stars relative to new viewport.
    stars = Array.from({length: 220}, () => ({
      x: Math.random() * W,
      y: Math.random() * H,
      r: Math.random() * 1.1 + 0.2,
      base: Math.random() * 0.5 + 0.2,
      tw: Math.random() * Math.PI * 2,
      sp: 0.0004 + Math.random() * 0.0012,
      hue: Math.random() < 0.15 ? 'gold' : 'cool'
    }));
    rings = [
      { cx: W * 0.82, cy: H * 0.18, r: Math.min(W, H) * 0.22, a: 0.05 },
      { cx: W * 0.14, cy: H * 0.74, r: Math.min(W, H) * 0.28, a: 0.04 }
    ];
  }

  function frame(now) {
    t = now * 0.001;
    ctx.clearRect(0, 0, W, H);

    // Faint distant orbits
    ctx.strokeStyle = 'rgba(212, 168, 83, 0.08)';
    ctx.lineWidth = 1;
    for (const r of rings) {
      ctx.beginPath();
      ctx.arc(r.cx, r.cy, r.r, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(r.cx, r.cy, r.r * 0.62, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Stars
    for (const s of stars) {
      s.tw += s.sp;
      const alpha = s.base + Math.sin(s.tw) * 0.28;
      const color = s.hue === 'gold'
        ? `rgba(240, 224, 184, ${Math.max(0, alpha)})`
        : `rgba(200, 210, 240, ${Math.max(0, alpha * 0.82)})`;
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(frame);
  }

  window.addEventListener('resize', resize);
  resize();
  requestAnimationFrame(frame);
})();
