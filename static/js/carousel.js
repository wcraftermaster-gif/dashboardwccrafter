/**
 * Carrusel infinito con GSAP horizontalLoop
 * - Autoplay al cargar
 * - Navegación paso a paso (sin saltos)
 * - Profundidad visual (4 niveles de fade)
 * - Accesible: teclado, aria-live, prefers-reduced-motion
 */

document.addEventListener('DOMContentLoaded', () => {
  if (typeof gsap === 'undefined') return;

  // ---------------------------------------------------------
  // Helper: horizontalLoop de GSAP
  // ---------------------------------------------------------
  function horizontalLoop(items, config) {
    items = gsap.utils.toArray(items);
    config = config || {};
    let tl = gsap.timeline({
        repeat: config.repeat,
        paused: config.paused,
        defaults: { ease: 'none' },
        onReverseComplete: () => tl.totalTime(tl.rawTime() + tl.duration() * 100)
      }),
      length = items.length,
      startX = items[0].offsetLeft,
      times = [],
      widths = [],
      xPercents = [],
      curIndex = 0,
      pixelsPerSecond = (config.speed || 1) * 100,
      snap = config.snap === false ? (v) => v : gsap.utils.snap(config.snap || 1),
      totalWidth, curX, distanceToStart, distanceToLoop, item, i;

    gsap.set(items, {
      xPercent: (i, el) => {
        let w = (widths[i] = parseFloat(gsap.getProperty(el, 'width', 'px')));
        xPercents[i] = snap(
          (parseFloat(gsap.getProperty(el, 'x', 'px')) / w) * 100 +
          gsap.getProperty(el, 'xPercent')
        );
        return xPercents[i];
      }
    });

    gsap.set(items, { x: 0 });

    totalWidth =
      items[length - 1].offsetLeft +
      (xPercents[length - 1] / 100) * widths[length - 1] -
      startX +
      items[length - 1].offsetWidth * gsap.getProperty(items[length - 1], 'scaleX') +
      (parseFloat(config.paddingRight) || 0);

    for (i = 0; i < length; i++) {
      item = items[i];
      curX = (xPercents[i] / 100) * widths[i];
      distanceToStart = item.offsetLeft + curX - startX;
      distanceToLoop = distanceToStart + widths[i] * gsap.getProperty(item, 'scaleX');

      tl.to(item, {
        xPercent: snap(((curX - distanceToLoop) / widths[i]) * 100),
        duration: distanceToLoop / pixelsPerSecond
      }, 0)
      .fromTo(item, {
        xPercent: snap((curX - distanceToLoop + totalWidth) / widths[i] * 100)
      }, {
        xPercent: xPercents[i],
        duration: (curX - distanceToLoop + totalWidth - curX) / pixelsPerSecond,
        immediateRender: false
      }, distanceToLoop / pixelsPerSecond)
      .add('label' + i, distanceToStart / pixelsPerSecond);

      times[i] = distanceToStart / pixelsPerSecond;
    }

    function toIndex(index, vars) {
      vars = vars || {};
      (Math.abs(index - curIndex) > length / 2) &&
        (index += index > curIndex ? -length : length);

      let newIndex = gsap.utils.wrap(0, length, index),
          time = times[newIndex];

      if (time > tl.time() !== index > curIndex) {
        vars.modifiers = { time: gsap.utils.wrap(0, tl.duration()) };
        time += tl.duration() * (index > curIndex ? 1 : -1);
      }

      curIndex = newIndex;
      vars.overwrite = true;
      return tl.tweenTo(time, vars);
    }

    tl.next = (vars) => toIndex(curIndex + 1, vars);
    tl.previous = (vars) => toIndex(curIndex - 1, vars);
    tl.current = () => curIndex;
    tl.toIndex = (index, vars) => toIndex(index, vars);
    tl.times = times;
    tl.progress(1, true).progress(0, true);

    if (config.reversed) {
      tl.vars.onReverseComplete();
      tl.reverse();
    }
    return tl;
  }

  // ---------------------------------------------------------
  // Inicialización
  // ---------------------------------------------------------
  document.querySelectorAll('[data-carousel]').forEach((root) => {
    const track   = root.querySelector('[data-carousel-track]');
    const prevBtn = root.querySelector('[data-carousel-prev]');
    const nextBtn = root.querySelector('[data-carousel-next]');

    if (!track || !prevBtn || !nextBtn) return;

    const items = [...track.querySelectorAll('[data-carousel-item]')];
    if (items.length < 2) return;

    items.forEach((item) => item.classList.add('carousel-item'));

    // --- aria-live para lectores de pantalla ---
    let liveRegion = root.querySelector('[data-carousel-live]');
    if (!liveRegion) {
      liveRegion = document.createElement('div');
      liveRegion.setAttribute('data-carousel-live', '');
      liveRegion.setAttribute('aria-live', 'polite');
      liveRegion.setAttribute('aria-atomic', 'true');
      liveRegion.className = 'sr-only';
      root.appendChild(liveRegion);
    }

    // --- Inicializar loop ---
    const loop = horizontalLoop(items, {
      paused: true,
      repeat: -1,
      speed: 0.4,              // ← velocidad que pediste
      paddingRight: 16
    });

    // ---------------------------------------------------------
    // Profundidad: detectar índice activo desde la línea de tiempo
    // ---------------------------------------------------------
    function getActiveIndex() {
      const total = loop.duration();
      if (!total) return 0;
      const t = loop.time() % total;
      let idx = 0;
      for (let i = 0; i < loop.times.length; i++) {
        if (t >= loop.times[i]) idx = i;
      }
      return idx;
    }

    let lastIdx = -1;
    function updateDepth() {
      const idx = getActiveIndex();
      if (idx === lastIdx) return;
      lastIdx = idx;

      const total = items.length;
      items.forEach((item, i) => {
        let dist = Math.abs(i - idx);
        dist = Math.min(dist, total - dist);

        item.classList.remove('is-active', 'is-adjacent', 'is-distant', 'is-far');
        if (dist === 0)      item.classList.add('is-active');
        else if (dist === 1) item.classList.add('is-adjacent');
        else if (dist === 2) item.classList.add('is-distant');
        else                 item.classList.add('is-far');
      });

      liveRegion.textContent = `Proyecto ${idx + 1} de ${total}`;
    }

    // Conectamos al timeline para que se actualice en vivo (autoplay incluido)
    loop.eventCallback('onUpdate', updateDepth);
    updateDepth();

    // ---------------------------------------------------------
    // Navegación paso a paso (bloquea clics rápidos)
    // ---------------------------------------------------------
    const NAV = { duration: 0.25, ease: 'power2.inOut' };
    let isAnimating = false;
    let animationTimeout;

    function navigate(direction) {
    if (isAnimating) return;

    isAnimating = true;

    // Identificar la tarjeta que está actualmente destacada
    const outgoingItem = items[loop.current()];

    // Siguiente: sale hacia la izquierda.
    // Anterior: sale hacia la derecha.
    const directionX = direction === 'next' ? -100 : 100;
    const directionRotation = direction === 'next' ? -7 : 7;

    // Efecto de lanzamiento y desaparición
    gsap.to(outgoingItem, {
        x: directionX,
        y: -152,
        rotation: directionRotation,
        scale: 0.94,
        opacity: 0,
        duration: 0.14,
        ease: 'power3.in',
        overwrite: 'auto'
    });

    // Desplazar el carrusel y recolocar las tarjetas
    const tween = direction === 'next'
        ? loop.next(NAV)
        : loop.previous(NAV);

    // Al finalizar, la tarjeta ya está recolocada en el circuito.
    const finishNavigation = () => {
        gsap.set(outgoingItem, {
            x: 0,
            y: 0,
            rotation: 0,
            scale: 1,
            clearProps: 'opacity'
        });

        isAnimating = false;
        clearTimeout(animationTimeout);
    };

    if (tween && tween.eventCallback) {
        tween.eventCallback('onComplete', finishNavigation);
    }

    // Protección por si la animación no notifica su finalización
    clearTimeout(animationTimeout);

    animationTimeout = setTimeout(() => {
        finishNavigation();
    }, 1000);
}

    nextBtn.addEventListener('click', () => navigate('next'));
    prevBtn.addEventListener('click', () => navigate('previous'));

    // ---------------------------------------------------------
    // Teclado
    // ---------------------------------------------------------
    track.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') { e.preventDefault(); navigate('next'); }
      if (e.key === 'ArrowLeft')  { e.preventDefault(); navigate('previous'); }
    });

    // ---------------------------------------------------------
    // Autoplay (arranca al cargar, sin necesitar hover)
    // ---------------------------------------------------------
    const AUTOPLAY_DELAY = 2200;
    let autoplayTimer = null;

    function startAutoplay() {
      stopAutoplay();
      autoplayTimer = setInterval(() => {
        if (!isAnimating) navigate('next');
      }, AUTOPLAY_DELAY);
    }
    function stopAutoplay() {
      if (autoplayTimer) clearInterval(autoplayTimer);
      autoplayTimer = null;
    }

    // Solo iniciar autoplay si el usuario no pidió reducir movimiento
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!reduceMotion) {
      startAutoplay();

      // Pausa en hover / focus dentro
      root.addEventListener('mouseenter', stopAutoplay);
      root.addEventListener('mouseleave', startAutoplay);
      root.addEventListener('focusin', stopAutoplay);
      root.addEventListener('focusout', startAutoplay);
    }

    // Reinicia el contador al hacer clic manual (evita doble avance)
    nextBtn.addEventListener('click', () => { if (!reduceMotion) startAutoplay(); });
    prevBtn.addEventListener('click', () => { if (!reduceMotion) startAutoplay(); });
  });
});