document.addEventListener('DOMContentLoaded', () => {
  const SPEED = 40; // píxeles por segundo; sube el número para ir más rápido
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  document.querySelectorAll('[data-marquee]').forEach((root) => {
    const track = root.querySelector('[data-marquee-track]');
    const group = root.querySelector('[data-marquee-group]');
    const controls = root.querySelector('[data-marquee-controls]');
    const toggle = root.querySelector('[data-marquee-toggle]');
    if (!track || !group) return;

    let clones = [];

    function clearClones() {
      clones.forEach((c) => c.remove());
      clones = [];
    }

    function start() {
      clearClones();

      const groupWidth = group.getBoundingClientRect().width;
      if (!groupWidth) return;

      // Copias suficientes para que nunca se vea un hueco, ni en pantallas muy anchas
      const needed = Math.max(1, Math.ceil(root.clientWidth / groupWidth));
      for (let i = 0; i < needed; i++) {
        const clone = group.cloneNode(true);
        clone.removeAttribute('data-marquee-group');
        clone.setAttribute('aria-hidden', 'true');
        clone.setAttribute('inert', '');
        track.appendChild(clone);
        clones.push(clone);
      }

      track.style.setProperty('--marquee-shift', `-${groupWidth}px`);
      track.style.setProperty('--marquee-duration', `${groupWidth / SPEED}s`);
      root.classList.add('is-running');
      if (controls) controls.hidden = false;
    }

    function stop() {
      clearClones();
      root.classList.remove('is-running', 'is-paused');
      if (controls) controls.hidden = true;
      if (toggle) toggle.textContent = 'Pausar animación';
    }

    if (toggle) {
      toggle.addEventListener('click', () => {
        const paused = root.classList.toggle('is-paused');
        toggle.textContent = paused ? 'Reanudar animación' : 'Pausar animación';
      });
    }

    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        if (!reduceMotion.matches) start();
      }, 150);
    });

    reduceMotion.addEventListener('change', (e) => (e.matches ? stop() : start()));
    if (!reduceMotion.matches) start();
  });
});