// AgriFarma Theme JS
// Purpose: Minor interactive enhancements (dark mode toggle, active nav detection, future chart hooks)

(function(){
  const navLinks = document.querySelectorAll('.navbar .nav-link');
  const current = window.location.pathname;
  navLinks.forEach(l => {
    if (l.getAttribute('href') === current) {
      l.classList.add('active');
    }
  });

  // Dark mode toggle (optional)
  const toggle = document.getElementById('af-dark-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const root = document.documentElement;
      const isDark = root.getAttribute('data-theme') === 'dark';
      root.setAttribute('data-theme', isDark ? 'light' : 'dark');
      localStorage.setItem('af-theme', isDark ? 'light' : 'dark');
    });
    const saved = localStorage.getItem('af-theme');
    if (saved) document.documentElement.setAttribute('data-theme', saved);
  }

  // Placeholder: chart initialization hook
  window.afInitCharts = function(){
    // Integrate Chart.js later
  };
})();
