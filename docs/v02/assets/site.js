(function () {
  var btn = document.querySelector('.menubtn'), panel = document.getElementById('meny');
  function setOpen(o) {
    btn.setAttribute('aria-expanded', o ? 'true' : 'false');
    panel.hidden = !o;
    document.body.classList.toggle('menu-open', o);
    if (o) { var f = panel.querySelector('a'); if (f) f.focus(); }
  }
  if (btn && panel) {
    btn.addEventListener('click', function () { setOpen(panel.hidden); });
    document.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' && !panel.hidden) { setOpen(false); btn.focus(); }
      if (ev.key === 'Tab' && !panel.hidden) {
        var els = [btn].concat([].slice.call(panel.querySelectorAll('a,button')));
        var first = els[0], last = els[els.length - 1];
        if (ev.shiftKey && document.activeElement === first) { ev.preventDefault(); last.focus(); }
        else if (!ev.shiftKey && document.activeElement === last) { ev.preventDefault(); first.focus(); }
      }
    });
  }
  var items = document.querySelectorAll('.pop');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) {
    items.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    items.forEach(function (el) { io.observe(el); });
  }
  document.querySelectorAll('form[data-mail]').forEach(function (form) {
    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      if (!form.reportValidity()) return;
      var lines = [];
      form.querySelectorAll('[data-label]').forEach(function (f) { if (f.value) lines.push(f.getAttribute('data-label') + ': ' + f.value); });
      lines.push('', 'Jag godkänner att föreningen behandlar mina uppgifter enligt integritetspolicyn.');
      var href = 'mailto:' + form.getAttribute('data-mail') + '?subject=' + encodeURIComponent(form.getAttribute('data-subject')) + '&body=' + encodeURIComponent(lines.join('\n'));
      var st = form.querySelector('[role="status"]');
      if (st) st.textContent = 'Ditt e-postprogram öppnas med ett förifyllt mejl. Skicka det för att slutföra.';
      window.location.href = href;
    });
  });
})();
