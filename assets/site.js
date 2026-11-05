document.documentElement.classList.add('js');
const menu=document.querySelector('.menu'),nav=document.querySelector('.nav');
if(menu&&nav){menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);});document.addEventListener('keydown',e=>{if(e.key==='Escape'){menu.setAttribute('aria-expanded','false');nav.classList.remove('open');}});}
document.querySelectorAll('[data-print]').forEach(button=>button.addEventListener('click',()=>window.print()));