document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const logoFull = document.getElementById('logo-full');
    const logoSmall = document.getElementById('logo-small');
    const labels = document.querySelectorAll('.sidebar-label');
    const collapseToggle = document.getElementById('sidebar-collapse-toggle');
    const collapseIcon = document.getElementById('collapse-icon');
    const blogSubmenu = document.getElementById('blog-submenu');
    const blogMenuToggle = document.getElementById('blog-menu-toggle');
    const blogChevron = document.getElementById('blog-menu-chevron');

    function applyCollapsed(collapsed) {
        if (collapsed) {
            sidebar.classList.remove('w-64');
            sidebar.classList.add('w-20');
            labels.forEach(el => el.classList.add('hidden'));
            logoFull.classList.add('hidden');
            logoSmall.classList.remove('hidden');
            blogSubmenu.classList.add('hidden');
            collapseIcon.style.transform = 'rotate(180deg)';
        } else {
            sidebar.classList.remove('w-20');
            sidebar.classList.add('w-64');
            labels.forEach(el => el.classList.remove('hidden'));
            logoFull.classList.remove('hidden');
            logoSmall.classList.add('hidden');
            collapseIcon.style.transform = 'rotate(0deg)';
        }
    }

    const savedState = localStorage.getItem('sidebar_collapsed') === 'true';
    applyCollapsed(savedState);

    collapseToggle.addEventListener('click', function () {
        const isCollapsed = sidebar.classList.contains('w-20');
        const next = !isCollapsed;
        applyCollapsed(next);
        localStorage.setItem('sidebar_collapsed', next);
    });

    blogMenuToggle.addEventListener('click', function () {
        if (sidebar.classList.contains('w-20')) return; // no abrir submenu si esta colapsado
        blogSubmenu.classList.toggle('hidden');
        blogChevron.style.transform = blogSubmenu.classList.contains('hidden') ? 'rotate(-90deg)' : 'rotate(0deg)';
    });
});