// Sidebar toggle logic for AgriFarma
(function(){
  const body = document.body;
  const sidebar = document.getElementById('af-sidebar');
  const page = document.getElementById('af-page');
  const toggleBtn = document.getElementById('mobile-menu-toggle');
  const STORAGE_KEY = 'af-sidebar-state';
  const menuOverlay = document.getElementById('af-menu-overlay');
  const menuCloseBtn = document.getElementById('af-menu-overlay-close');

  function setAria(expanded){
    if (toggleBtn) toggleBtn.setAttribute('aria-expanded', String(expanded));
    if (menuOverlay) menuOverlay.setAttribute('aria-hidden', String(!expanded));
    if (sidebar) sidebar.setAttribute('aria-hidden', String(!expanded));
  }

  function isMobile(){
    return window.matchMedia('(max-width: 768px)').matches;
  }

  function openSidebar(){
    body.classList.add('af-sidebar-open');
    body.classList.remove('af-sidebar-closed');
    setAria(true);
    if (!isMobile()) {
      localStorage.setItem(STORAGE_KEY, 'open');
    }
  }

  function closeSidebar(){
    body.classList.add('af-sidebar-closed');
    body.classList.remove('af-sidebar-open');
    setAria(false);
    if (!isMobile()) {
      localStorage.setItem(STORAGE_KEY, 'closed');
    }
  }

  // Overlay handlers
  function openMenuOverlay(){
    if (!menuOverlay) return toggle(); // fallback to sidebar if overlay missing
    body.classList.add('af-menu-open');
    setAria(true);
    // focus first link if available
    const firstLink = menuOverlay.querySelector('.af-menu-link');
    if (firstLink) setTimeout(() => firstLink.focus({preventScroll:true}), 0);
  }

  function closeMenuOverlay(){
    if (!menuOverlay) return closeSidebar();
    body.classList.remove('af-menu-open');
    setAria(false);
    if (toggleBtn) toggleBtn.focus();
  }

  function toggleMenuOverlay(){
    if (body.classList.contains('af-menu-open')) closeMenuOverlay();
    else openMenuOverlay();
  }

  if (toggleBtn){
    toggleBtn.addEventListener('click', (e) => {
      e.preventDefault();
      toggleMenuOverlay();
    });
  }

  // Close overlay via close button
  if (menuCloseBtn){
    menuCloseBtn.addEventListener('click', closeMenuOverlay);
  }

  // Click on backdrop closes overlay
  if (menuOverlay){
    menuOverlay.addEventListener('click', (e) => {
      if (e.target.classList && e.target.classList.contains('af-menu-backdrop')){
        closeMenuOverlay();
      }
    });
  }

  // Click outside to close on mobile
  document.addEventListener('click', (e) => {
    if (!isMobile()) return;
    if (!sidebar) return;
    const isClickInsideSidebar = sidebar.contains(e.target);
    const isToggle = toggleBtn && toggleBtn.contains(e.target);
    if (!isClickInsideSidebar && !isToggle && body.classList.contains('af-sidebar-open')){
      closeSidebar();
    }
  });

  // Escape key closes overlay (and mobile sidebar)
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (body.classList.contains('af-menu-open')) return closeMenuOverlay();
      if (isMobile() && body.classList.contains('af-sidebar-open')) return closeSidebar();
    }
  });

  // Initialize state: restore from localStorage on desktop, closed on mobile
  function init(){
    // Start with overlay closed
    if (body.classList.contains('af-menu-open')) body.classList.remove('af-menu-open');
    setAria(false);
    // Maintain previous sidebar persistence on desktop in case other controls toggle it
    if (!isMobile()){
      const savedState = localStorage.getItem(STORAGE_KEY);
      if (savedState === 'closed') closeSidebar(); else openSidebar();
    } else {
      closeSidebar();
    }
  }

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      // On mobile, always start closed
      if (isMobile() && !body.classList.contains('af-sidebar-closed')){
        closeSidebar();
      }
      // On desktop, restore saved state
      if (!isMobile()) {
        const savedState = localStorage.getItem(STORAGE_KEY);
        if (savedState === 'closed' && !body.classList.contains('af-sidebar-closed')) {
          closeSidebar();
        } else if (savedState !== 'closed' && body.classList.contains('af-sidebar-closed')) {
          openSidebar();
        }
      }
    }, 150);
  });

  init();
})();
