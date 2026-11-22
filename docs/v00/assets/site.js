(function () {
  document.documentElement.classList.remove('no-js');

  // Mobilmeny
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('nav');
  if (btn && nav) {
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') !== 'true';
      btn.setAttribute('aria-expanded', open);
      btn.textContent = open ? 'Stäng' : 'Meny';
      nav.setAttribute('data-open', open);
      document.body.classList.toggle('menu-open', open);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && btn.getAttribute('aria-expanded') === 'true') { btn.click(); btn.focus(); }
    });
  }

  // Rullgardin
  document.querySelectorAll('.has-drop > button').forEach(function (b) {
    b.addEventListener('click', function () {
      var li = b.parentElement, open = li.getAttribute('data-open') !== 'true';
      li.setAttribute('data-open', open);
      b.setAttribute('aria-expanded', open);
    });
  });
  document.addEventListener('click', function (e) {
    document.querySelectorAll('.has-drop[data-open="true"]').forEach(function (li) {
      if (!li.contains(e.target)) { li.setAttribute('data-open', 'false'); li.firstElementChild.setAttribute('aria-expanded', 'false'); }
    });
  });

  // Inträde, en gång per element
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('in'); }); }

  // Formulär: öppnar ett färdigskrivet mejl till föreningen
  document.querySelectorAll('form[data-mail]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!f.reportValidity()) return;
      var lines = [];
      f.querySelectorAll('input:not([type=checkbox]),textarea,select').forEach(function (i) {
        if (i.value) lines.push(i.dataset.label + ': ' + i.value);
      });
      var href = 'mailto:' + f.dataset.mail + '?subject=' + encodeURIComponent(f.dataset.subject) +
        '&body=' + encodeURIComponent(lines.join('\n'));
      window.location.href = href;
      var s = f.querySelector('.form-status');
      if (s) s.textContent = 'Ditt e-postprogram öppnas med uppgifterna ifyllda. Skicka mejlet för att slutföra.';
    });
  });
})();
