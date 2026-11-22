(function(){
 var btn=document.querySelector('.hd__btn'),menu=document.getElementById('meny');
 function close(f){menu.hidden=true;btn.setAttribute('aria-expanded','false');if(f)btn.focus();}
 if(btn){btn.addEventListener('click',function(){if(btn.getAttribute('aria-expanded')==='true'){close();}else{menu.hidden=false;btn.setAttribute('aria-expanded','true');var a=menu.querySelector('a');if(a)a.focus();}});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&btn.getAttribute('aria-expanded')==='true')close(true);});
  document.addEventListener('click',function(e){if(!menu.hidden&&!menu.contains(e.target)&&!btn.contains(e.target))close();});}
 var rm=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 var els=[].slice.call(document.querySelectorAll('.rv'));
 if(rm||!('IntersectionObserver' in window)){els.forEach(function(el){el.classList.add('in')});}
 else{var io=new IntersectionObserver(function(en){var n=0;en.forEach(function(x){if(x.isIntersecting){x.target.style.setProperty('--d',(n++*80)+'ms');x.target.classList.add('in');io.unobserve(x.target);}});},{rootMargin:'0px 0px -6% 0px'});
  els.forEach(function(el){io.observe(el)});}
 // segmenterad flikväxlare
 var tabs=[].slice.call(document.querySelectorAll('.seg__b'));
 function sel(t,focus){tabs.forEach(function(o){var on=o===t;o.setAttribute('aria-selected',on);o.tabIndex=on?0:-1;var p=document.getElementById(o.getAttribute('aria-controls'));p.hidden=!on;
   if(on){p.querySelectorAll('.rv').forEach(function(c){c.classList.add('in')});if(!rm){p.classList.remove('swap');void p.offsetWidth;p.classList.add('swap');}}});if(focus)t.focus();}
 tabs.forEach(function(t,i){t.addEventListener('click',function(){sel(t)});t.addEventListener('keydown',function(e){var d=e.key==='ArrowRight'?1:e.key==='ArrowLeft'?-1:0;if(d){e.preventDefault();sel(tabs[(i+d+tabs.length)%tabs.length],true);}});});
 // toast: en gång per besök
 var toast=document.getElementById('toast'),KEY='uc-v06-toast';
 function seen(){try{return sessionStorage.getItem(KEY)==='1'}catch(e){return false}}
 function mark(){try{sessionStorage.setItem(KEY,'1')}catch(e){}}
 if(toast&&!seen()&&!/\/bli-medlem\//.test(location.pathname)){
  var onScroll=function(){if(window.scrollY>window.innerHeight*0.9){window.removeEventListener('scroll',onScroll);toast.hidden=false;toast.classList.add('show');mark();}};
  window.addEventListener('scroll',onScroll,{passive:true});
  toast.querySelector('.toast__x').addEventListener('click',function(){toast.hidden=true;});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!toast.hidden&&(!btn||btn.getAttribute('aria-expanded')!=='true'))toast.hidden=true;});
 }
 document.querySelectorAll('form[data-mail]').forEach(function(f){f.addEventListener('submit',function(ev){ev.preventDefault();
  if(!f.reportValidity())return;var lines=[];[].forEach.call(f.elements,function(el){if(el.name&&el.name!=='samtycke'&&el.value)lines.push(el.name+': '+el.value);});
  lines.push('','Jag godkänner behandling av mina uppgifter enligt integritetspolicyn.');
  location.href='mailto:'+f.dataset.mail+'?subject='+encodeURIComponent(f.dataset.subject)+'&body='+encodeURIComponent(lines.join('\n'));
  var s=f.querySelector('.form-status');if(s)s.textContent='Ditt e-postprogram öppnas med ett förifyllt mejl. Skicka det för att slutföra.';});});
})();
