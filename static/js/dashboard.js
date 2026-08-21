    document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const labels = document.querySelectorAll('.sidebar-label');
    const collapseToggle = document.getElementById('sidebar-collapse-toggle');
    const collapseIcon = document.getElementById('collapse-icon');
    const sidebarLogo = document.getElementById('sidebar-logo');

    function applyCollapsed(collapsed) {
        if (collapsed) {
            sidebar.classList.remove('w-45');
            sidebar.classList.add('w-10');
            labels.forEach(el => el.classList.add('hidden'));
            document.querySelectorAll('[id$="-submenu"]').forEach(el => el.classList.add('hidden'));
            collapseIcon.style.transform = 'rotate(180deg)';
            sidebarLogo.classList.remove('w-11', 'h-11');
            sidebarLogo.classList.add('w-7', 'h-7');
        } else {
            sidebar.classList.remove('w-10');
            sidebar.classList.add('w-45');
            labels.forEach(el => el.classList.remove('hidden'));
            collapseIcon.style.transform = 'rotate(0deg)';
            sidebarLogo.classList.remove('w-7', 'h-7');
            sidebarLogo.classList.add('w-11', 'h-11');
        }
    }

    const savedState = localStorage.getItem('sidebar_collapsed') === 'true';
    applyCollapsed(savedState);

    collapseToggle.addEventListener('click', function () {
        const isCollapsed = sidebar.classList.contains('w-10');
        const next = !isCollapsed;
        applyCollapsed(next);
        localStorage.setItem('sidebar_collapsed', next);
    });

    function bindSubmenuToggle(toggleId, submenuId, chevronId) {
        const toggle = document.getElementById(toggleId);
        const submenu = document.getElementById(submenuId);
        const chevron = document.getElementById(chevronId);
        if (!toggle || !submenu) return;

        toggle.addEventListener('click', function () {
            if (sidebar.classList.contains('w-10')) return;
            submenu.classList.toggle('hidden');
            if (chevron) {
                chevron.style.transform = submenu.classList.contains('hidden') ? 'rotate(-90deg)' : 'rotate(0deg)';
            }
        });
    }

    bindSubmenuToggle('blog-menu-toggle', 'blog-submenu', 'blog-menu-chevron');
    bindSubmenuToggle('users-menu-toggle', 'users-submenu', 'users-menu-chevron');
});