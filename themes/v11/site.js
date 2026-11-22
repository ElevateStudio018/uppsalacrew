(function(){
  document.documentElement.classList.remove('no-js');
  var nav=document.querySelector('.mainnav'),btn=document.querySelector('.menu-btn');
  if(btn&&nav){
    btn.addEventListener('click',function(){
      var o=btn.getAttribute('aria-expanded')!=='true';
      btn.setAttribute('aria-expanded',o);nav.setAttribute('data-open',o);
      btn.querySelector('span').textContent=o?'Stäng':'Meny';
      document.body.classList.toggle('menu-open',o);
    });
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&btn.getAttribute('aria-expanded')==='true'){btn.click();btn.focus();}});
  }
  document.querySelectorAll('.has-drop>button').forEach(function(b){
    b.addEventListener('click',function(){
      var li=b.parentElement,o=li.getAttribute('data-open')!=='true';
      document.querySelectorAll('.has-drop[data-open="true"]').forEach(function(x){if(x!==li){x.setAttribute('data-open','false');x.firstElementChild.setAttribute('aria-expanded','false');}});
      li.setAttribute('data-open',o);b.setAttribute('aria-expanded',o);
    });
  });
  document.addEventListener('click',function(e){document.querySelectorAll('.has-drop[data-open="true"]').forEach(function(li){if(!li.contains(e.target)){li.setAttribute('data-open','false');li.firstElementChild.setAttribute('aria-expanded','false');}});});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'){document.querySelectorAll('.has-drop[data-open="true"]').forEach(function(li){li.setAttribute('data-open','false');li.firstElementChild.setAttribute('aria-expanded','false');li.firstElementChild.focus();});}});
  var els=document.querySelectorAll('.rv');
  if('IntersectionObserver' in window&&!matchMedia('(prefers-reduced-motion: reduce)').matches){
    var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target);}});},{rootMargin:'0px 0px -6% 0px'});
    els.forEach(function(el,i){el.style.transitionDelay=(Math.min(i%3,2)*80)+'ms';io.observe(el);});
  }else{els.forEach(function(el){el.classList.add('in');});}
  document.querySelectorAll('form[data-mail]').forEach(function(f){
    f.addEventListener('submit',function(e){
      e.preventDefault();if(!f.reportValidity())return;
      var l=[];f.querySelectorAll('input:not([type=checkbox]),select,textarea').forEach(function(i){if(i.value)l.push(i.dataset.label+': '+i.value);});
      location.href='mailto:'+f.dataset.mail+'?subject='+encodeURIComponent(f.dataset.subject)+'&body='+encodeURIComponent(l.join('\n'));
      var s=f.querySelector('.status');if(s)s.textContent='Ditt e-postprogram öppnas med uppgifterna ifyllda. Skicka mejlet för att slutföra.';
    });
  });
})();
