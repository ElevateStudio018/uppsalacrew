(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var btn = document.querySelector('.hd__menu'), menu = document.getElementById('menu');
  var qn = document.getElementById('qn');
  function closeMenu(focus) { menu.hidden = true; btn.setAttribute('aria-expanded', 'false'); if (focus) btn.focus(); }
  btn.addEventListener('click', function () {
    if (btn.getAttribute('aria-expanded') === 'true') closeMenu(false);
    else { menu.hidden = false; btn.setAttribute('aria-expanded', 'true'); menu.querySelector('a').focus(); }
  });

  // Snabbnavigering
  var f = document.getElementById('qn-f'), items = qn ? qn.querySelectorAll('li') : [];
  function openQn() { if (!qn.open) { qn.showModal(); f.value = ''; filter(); f.focus(); } }
  function filter() {
    var q = f.value.trim().toLowerCase();
    items.forEach(function (li) { li.hidden = q && li.textContent.toLowerCase().indexOf(q) < 0; });
  }
  if (qn) {
    f.addEventListener('input', filter);
    f.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') { var a = qn.querySelector('li:not([hidden]) a'); if (a) { e.preventDefault(); a.click(); } }
    });
    qn.querySelector('.qn__x').addEventListener('click', function () { qn.close(); });
  }

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !menu.hidden) { closeMenu(true); return; }
    if (e.ctrlKey || e.metaKey || e.altKey || e.defaultPrevented) return;
    var t = e.target, tag = t.tagName;
    if (t.isContentEditable || tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || (qn && qn.open)) return;
    if (e.key === '/') { e.preventDefault(); openQn(); }
    else if (e.key === 'm' || e.key === 'M') { window.location.href = '/uppsalacrew/v10/bli-medlem/'; }
  });

  // Typewriter för rubriker, bara första besöket per sida
  var key = 'uc10-typed:' + location.pathname, seen = false;
  try { seen = sessionStorage.getItem(key) === '1'; sessionStorage.setItem(key, '1'); } catch (e) {}
  var h1 = document.querySelector('main h1');
  if (h1) {
    if (reduce || seen) h1.classList.add('typed-done');
    else {
      var full = h1.textContent, i = 0;
      h1.setAttribute('aria-label', full);
      h1.style.minHeight = h1.offsetHeight + 'px';
      h1.textContent = ''; h1.classList.add('cursor');
      var step = Math.max(14, Math.min(45, 900 / full.length));
      (function tick() {
        i++; h1.textContent = full.slice(0, i);
        if (i < full.length) setTimeout(tick, step);
        else { h1.classList.remove('cursor'); h1.classList.add('typed-done'); h1.removeAttribute('aria-label'); h1.style.minHeight = ''; }
      })();
    }
  }

  // Listor rad för rad
  var lists = document.querySelectorAll('.pl, .roles, .steps, .checks, .tl, .facts, .comps, .lst--big, .tbl tbody');
  lists.forEach(function (l) {
    l.classList.add('seq');
    Array.prototype.forEach.call(l.children, function (c, n) { c.style.transitionDelay = (n * 70) + 'ms'; });
  });
  if (reduce || !('IntersectionObserver' in window)) lists.forEach(function (l) { l.classList.add('in'); });
  else {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -5% 0px' });
    lists.forEach(function (l) { io.observe(l); });
  }

  document.querySelectorAll('form[data-mail]').forEach(function (fm) {
    fm.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!fm.reportValidity()) return;
      var lines = [];
      fm.querySelectorAll('input:not([type=checkbox]),textarea,select').forEach(function (i) { if (i.value) lines.push(i.dataset.label + ': ' + i.value); });
      window.location.href = 'mailto:' + fm.dataset.mail + '?subject=' + encodeURIComponent(fm.dataset.subject) + '&body=' + encodeURIComponent(lines.join('\n'));
      var s = fm.querySelector('.form-status');
      if (s) s.textContent = 'Ditt e-postprogram öppnas med uppgifterna ifyllda. Skicka mejlet för att slutföra.';
    });
  });
})();
