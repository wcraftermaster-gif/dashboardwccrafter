document.addEventListener('DOMContentLoaded', function () {
    const heroSection = document.getElementById('inicio');
    if (!heroSection) return;

    const staticContainer = heroSection.querySelector('.dots-static');
    const interactiveContainer = heroSection.querySelector('.dots-interactive');
    if (!staticContainer || !interactiveContainer) return;

    const width = heroSection.offsetWidth;
    const height = heroSection.offsetHeight;

    // 80 puntos estáticos dispersos por todo el hero
    const NUM_STATIC = 80;
    for (let i = 0; i < NUM_STATIC; i++) {
        const dot = document.createElement('div');
        const sizeClass = i % 5 === 0 ? 'large' : (i % 3 === 0 ? 'small' : '');
        dot.className = 'dot ' + sizeClass;
        dot.style.left = Math.random() * width + 'px';
        dot.style.top = Math.random() * height + 'px';
        staticContainer.appendChild(dot);
    }

    // 30 puntos interactivos (reducido de 60)
    const NUM_INTERACTIVE = 30;
    const dots = [];

    for (let i = 0; i < NUM_INTERACTIVE; i++) {
        const dot = document.createElement('div');
        const sizeClass = i % 4 === 0 ? 'large' : (i % 2 === 0 ? 'small' : '');
        dot.className = 'dot ' + sizeClass;
        interactiveContainer.appendChild(dot);

        dots.push({
            element: dot,
            x: Math.random() * width,
            y: Math.random() * height,
            vx: 0,
            vy: 0,
            angle: Math.random() * Math.PI * 2,
            orbitRadius: 20 + Math.random() * 80,
            orbitSpeed: 0.02 + Math.random() * 0.03,
            scatterX: Math.random() * width,
            scatterY: Math.random() * height,
            isScattering: false
        });
    }

    let mouseX = width / 2;
    let mouseY = height / 2;
    let mouseInside = false;

    heroSection.addEventListener('mousemove', function (e) {
        const rect = heroSection.getBoundingClientRect();
        mouseX = e.clientX - rect.left;
        mouseY = e.clientY - rect.top;
        mouseInside = true;
    });

    heroSection.addEventListener('mouseleave', function () {
        mouseInside = false;
        dots.forEach(function (dot) {
            dot.scatterX = Math.random() * width;
            dot.scatterY = Math.random() * height;
            dot.isScattering = true;
        });
    });

    window.addEventListener('resize', function () {
        const newWidth = heroSection.offsetWidth;
        const newHeight = heroSection.offsetHeight;
        dots.forEach(function (dot) {
            dot.x = Math.min(dot.x, newWidth);
            dot.y = Math.min(dot.y, newHeight);
        });
    });

    function animateDots() {
        dots.forEach(function (dot) {
            if (mouseInside) {
                dot.angle += dot.orbitSpeed;
                const targetOrbitX = mouseX + Math.cos(dot.angle) * dot.orbitRadius;
                const targetOrbitY = mouseY + Math.sin(dot.angle) * dot.orbitRadius;

                const dx = targetOrbitX - dot.x;
                const dy = targetOrbitY - dot.y;

                dot.vx += dx * 0.08;
                dot.vy += dy * 0.08;
                dot.isScattering = false;

            } else if (dot.isScattering) {
                const dx = dot.scatterX - dot.x;
                const dy = dot.scatterY - dot.y;

                dot.vx += dx * 0.03;
                dot.vy += dy * 0.03;

                const distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < 10) {
                    dot.isScattering = false;
                }
            } else {
                dot.vx += (Math.random() - 0.5) * 0.3;
                dot.vy += (Math.random() - 0.5) * 0.3;

                const margin = 50;
                if (dot.x < margin) dot.vx += 0.3;
                if (dot.x > width - margin) dot.vx -= 0.3;
                if (dot.y < margin) dot.vy += 0.3;
                if (dot.y > height - margin) dot.vy -= 0.3;
            }

            const friction = mouseInside ? 0.85 : 0.90;
            dot.vx *= friction;
            dot.vy *= friction;

            const maxSpeed = mouseInside ? 15 : 12;
            const speed = Math.sqrt(dot.vx * dot.vx + dot.vy * dot.vy);
            if (speed > maxSpeed) {
                dot.vx = (dot.vx / speed) * maxSpeed;
                dot.vy = (dot.vy / speed) * maxSpeed;
            }

            dot.x += dot.vx;
            dot.y += dot.vy;

            dot.x = Math.max(0, Math.min(width, dot.x));
            dot.y = Math.max(0, Math.min(height, dot.y));

            dot.element.style.left = dot.x + 'px';
            dot.element.style.top = dot.y + 'px';
        });

        requestAnimationFrame(animateDots);
    }

    animateDots();
});