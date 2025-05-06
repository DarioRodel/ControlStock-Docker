document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById('darkModeToggle');
    const currentTheme = localStorage.getItem('theme');

    console.log("El tema actual es:", currentTheme);  // Esto te ayudará a depurar.

    if (currentTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        toggle.checked = true;
    }

    toggle.addEventListener('change', () => {
        if (toggle.checked) {
            document.body.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
        }
    });
});
document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById('darkModeToggle');

    // Sincronizar con localStorage
    const currentTheme = localStorage.getItem('theme') || 'light';

    if (currentTheme === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
        if(toggle) toggle.checked = true;
    }

    if(toggle) {
        toggle.addEventListener('change', () => {
            const theme = toggle.checked ? 'dark' : 'light';
            document.body.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
        });
    }
});