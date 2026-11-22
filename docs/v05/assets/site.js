document.documentElement.classList.add('js');
(function(){
 var btn=document.querySelector('.hd__btn'),menu=document.getElementById('meny');
 function close(f){menu.hidden=true;btn.setAttribute('aria-expanded','false');document.body.style.overflow='';if(f)btn.focus();}
 if(btn){btn.addEventListener('click',function(){var o=btn.getAttribute('aria-expanded')==='true';if(o){close();}else{menu.hidden=false;btn.setAttribute('aria-expanded','true');document.body.style.overflow='hidden';var a=menu.querySelector('a');if(a)a.focus();}});
 document.addEventListener('keydown',function(e){if(e.key==='Escape'&&btn.getAttribute('aria-expanded')==='true')close(true);});}
 var rm=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 var els=[].slice.call(document.querySelectorAll('.rv'));
 if(rm||!('IntersectionObserver' in window)){els.forEach(function(el){el.classList.add('in')});}
 else{var io=new IntersectionObserver(function(en){var n=0;en.forEach(function(x){if(x.isIntersecting){x.target.style.setProperty('--d',(n++*90)+'ms');x.target.classList.add('in');io.unobserve(x.target);}});},{rootMargin:'0px 0px -8% 0px'});
 els.forEach(function(el){io.observe(el)});}
 document.querySelectorAll('form[data-mail]').forEach(function(f){f.addEventListener('submit',function(ev){ev.preventDefault();
  if(!f.reportValidity())return;var lines=[];[].forEach.call(f.elements,function(el){if(el.name&&el.name!=='samtycke'&&el.value)lines.push(el.name+': '+el.value);});
  lines.push('','Jag godkänner behandling av mina uppgifter enligt integritetspolicyn.');
  location.href='mailto:'+f.dataset.mail+'?subject='+encodeURIComponent(f.dataset.subject)+'&body='+encodeURIComponent(lines.join('\n'));
  var s=f.querySelector('.form-status');if(s)s.textContent='Ditt e-postprogram öppnas med ett förifyllt mejl. Skicka det för att slutföra.';});});
})();
