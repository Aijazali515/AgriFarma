// Theme toggle for AgriFarma
(function(){
  const STORAGE_KEY = 'af-theme';
  const root = document.documentElement;
  const toggleBtn = document.getElementById('af-theme-toggle');
  if (!toggleBtn) return;

  function applyTheme(mode){
    if (mode === 'dark') {
      root.setAttribute('data-theme','dark');
      toggleBtn.setAttribute('aria-pressed','true');
      toggleBtn.innerHTML = '<i class="bi bi-sun" aria-hidden="true"></i><span class="visually-hidden">Switch to light</span>';
    } else {
      root.removeAttribute('data-theme');
      toggleBtn.setAttribute('aria-pressed','false');
      toggleBtn.innerHTML = '<i class="bi bi-moon-stars" aria-hidden="true"></i><span class="visually-hidden">Switch to dark</span>';
    }
  }

  function getPreferred(){
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    // system preference fallback
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function toggle(){
    const current = root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
  }

  toggleBtn.addEventListener('click', toggle);
  applyTheme(getPreferred());
})();