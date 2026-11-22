(function () {
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var root = document.documentElement;

  // Meny: helskärm, Escape stänger, fokus stannar i menyn
  var btn = document.querySelector('.menu-btn'), menu = document.getElementById('menu');
  function setMenu(open) {
    btn.setAttribute('aria-expanded', open);
    btn.querySelector('.menu-btn__t').textContent = open ? 'Stäng' : 'Meny';
    if (open) { menu.hidden = false; requestAnimationFrame(function () { menu.classList.add('open'); }); }
    else { menu.classList.remove('open'); menu.hidden = true; }
    document.body.classList.toggle('lock', open);
    if (open) { var a = menu.querySelector('a'); if (a) a.focus(); }
  }
  if (btn && menu) {
    btn.addEventListener('click', function () { setMenu(btn.getAttribute('aria-expanded') !== 'true'); });
    document.addEventListener('keydown', function (e) {
      if (btn.getAttribute('aria-expanded') !== 'true') return;
      if (e.key === 'Escape') { setMenu(false); btn.focus(); }
      if (e.key === 'Tab') {
        var f = [btn].concat([].slice.call(menu.querySelectorAll('a')));
        var i = f.indexOf(document.activeElement);
        if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); }
        else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); }
      }
    });
  }

  // Rubriker: gruppera ord till rader och ge varje rad en fördröjning
  function lines() {
    document.querySelectorAll('.split').forEach(function (h) {
      var top = null, line = -1;
      h.querySelectorAll('.w').forEach(function (w) {
        var t = w.offsetTop;
        if (top === null || Math.abs(t - top) > 4) { line++; top = t; }
        w.style.setProperty('--l', line);
      });
    });
  }
  lines();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(lines);
  var rt; addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(lines, 150); });

  // Inträden
  var els = document.querySelectorAll('.h, .rv, .zoom');
  if (!reduce && 'IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('is-in'); io.unobserve(x.target); } });
    }, { rootMargin: '0px 0px -10% 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else { root.classList.add('still'); els.forEach(function (el) { el.classList.add('is-in'); }); }

  // Scrollprogress
  var bar = document.querySelector('.progress span'), top = document.querySelector('.top');
  function onScroll() {
    var h = document.documentElement.scrollHeight - innerHeight;
    if (bar) bar.style.transform = 'scaleX(' + (h > 0 ? scrollY / h : 0) + ')';
    if (top) top.classList.toggle('top--solid', scrollY > 40);
  }
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  // Formulär: förifyllt mejl
  document.querySelectorAll('form[data-mail]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!f.reportValidity()) return;
      var lines = [];
      f.querySelectorAll('input:not([type=checkbox]),textarea,select').forEach(function (i) {
        if (i.value) lines.push(i.dataset.label + ': ' + i.value);
      });
      window.location.href = 'mailto:' + f.dataset.mail + '?subject=' + encodeURIComponent(f.dataset.subject) +
        '&body=' + encodeURIComponent(lines.join('\n'));
      var s = f.querySelector('.form-status');
      if (s) s.textContent = 'Ditt e-postprogram öppnas med uppgifterna ifyllda. Skicka mejlet för att slutföra.';
    });
  });
})();
