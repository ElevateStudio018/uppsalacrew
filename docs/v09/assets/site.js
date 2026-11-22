(function () {
  // Meny
  var btn = document.querySelector('.hd__menu'), menu = document.getElementById('menu');
  function close(focus) { menu.hidden = true; btn.setAttribute('aria-expanded', 'false'); if (focus) btn.focus(); }
  if (btn && menu) {
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      if (open) close(false); else { menu.hidden = false; btn.setAttribute('aria-expanded', 'true'); var a = menu.querySelector('a'); if (a) a.focus(); }
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !menu.hidden) close(true); });
  }

  // Klistermärken poppar in
  var st = document.querySelectorAll('.sticker');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) { st.forEach(function (s) { s.classList.add('in'); }); }
  else {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en, i) {
        if (en.isIntersecting) { var s = en.target; setTimeout(function () { s.classList.add('in'); }, (i % 6) * 90); io.unobserve(s); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    st.forEach(function (s) { io.observe(s); });
  }

  // Formulär: öppnar ett färdigskrivet mejl
  document.querySelectorAll('form[data-mail]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!f.reportValidity()) return;
      var lines = [];
      f.querySelectorAll('input:not([type=checkbox]),textarea,select').forEach(function (i) { if (i.value) lines.push(i.dataset.label + ': ' + i.value); });
      window.location.href = 'mailto:' + f.dataset.mail + '?subject=' + encodeURIComponent(f.dataset.subject) + '&body=' + encodeURIComponent(lines.join('\n'));
      var s = f.querySelector('.form-status');
      if (s) s.textContent = 'Ditt e-postprogram öppnas med uppgifterna ifyllda. Skicka mejlet för att slutföra.';
    });
  });
})();
