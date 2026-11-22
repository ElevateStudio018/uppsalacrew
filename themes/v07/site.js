(function () {
  var d = document, rm = matchMedia('(prefers-reduced-motion: reduce)').matches;
  d.documentElement.classList.add('js');

  // Meny
  var btn = d.querySelector('.menubtn'), menu = d.getElementById('menu');
  function setMenu(open) {
    btn.setAttribute('aria-expanded', open);
    btn.querySelector('.menubtn__t').textContent = open ? 'Stäng' : 'Meny';
    menu.hidden = !open;
    d.body.classList.toggle('menu-open', open);
    if (open) { var a = menu.querySelector('a'); if (a) a.focus(); }
  }
  if (btn && menu) {
    btn.addEventListener('click', function () { setMenu(btn.getAttribute('aria-expanded') !== 'true'); });
    d.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && btn.getAttribute('aria-expanded') === 'true') { setMenu(false); btn.focus(); }
    });
  }

  // Kort som poppar in
  var els = d.querySelectorAll('.pop');
  if (!rm && 'IntersectionObserver' in window) {
    d.documentElement.classList.add('anim');
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } });
    }, { rootMargin: '0px 0px -6% 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('in'); }); }

  // Formulär -> förifyllt mejl
  d.querySelectorAll('form[data-mail]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!f.reportValidity()) return;
      var lines = [];
      f.querySelectorAll('input:not([type=checkbox]),textarea,select').forEach(function (i) {
        if (i.value) lines.push(i.dataset.label + ': ' + i.value);
      });
      window.location.href = 'mailto:' + f.dataset.mail + '?subject=' + encodeURIComponent(f.dataset.subject) +
        '&body=' + encodeURIComponent(lines.join('\n'));
      var s = f.querySelector('[role=status]');
      if (s) s.textContent = 'Ditt e-postprogram öppnas med uppgifterna ifyllda. Skicka mejlet för att slutföra.';
    });
  });
})();
