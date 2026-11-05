/* A light access gate for a static GitHub Pages site. Not secure authentication. */
(function(){
  'use strict';
  var key='brands-bangkok-access-v1';
  function allowed(){try{return sessionStorage.getItem(key)==='granted';}catch(e){return false;}}
  function unlock(){document.documentElement.classList.remove('access-locked');}
  if(allowed())unlock();
  document.addEventListener('DOMContentLoaded',function(){
    var form=document.getElementById('access-form');
    var input=document.getElementById('access-password');
    var error=document.getElementById('access-error');
    if(form)form.addEventListener('submit',function(event){
      event.preventDefault();
      if(input.value==='BHFutureLeaders'){
        try{sessionStorage.setItem(key,'granted');}catch(e){}
        input.value='';
        error.textContent='';
        unlock();
        var heading=document.querySelector('#site-content h1');
        if(heading){heading.setAttribute('tabindex','-1');heading.focus({preventScroll:true});}
      }else{
        error.textContent="That password isn't correct. Please try again.";
        input.setAttribute('aria-invalid','true');
        input.focus();
        input.select();
      }
    });
    if(input)input.addEventListener('input',function(){error.textContent='';input.removeAttribute('aria-invalid');});
    document.querySelectorAll('[data-lock]').forEach(function(button){
      button.addEventListener('click',function(){
        try{sessionStorage.removeItem(key);}catch(e){}
        document.documentElement.classList.add('access-locked');
        if(input)input.focus();
        window.scrollTo(0,0);
      });
    });
  });
})();