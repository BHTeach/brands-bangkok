(function(){
'use strict';
var seasons={'feb-apr':{label:'Feb – Apr',multiplier:1.1},'may-jul':{label:'May – Jul',multiplier:0.9},'aug-oct':{label:'Aug – Oct',multiplier:1},'nov-jan':{label:'Nov – Jan',multiplier:1.3}};
var setups={
space:{label:'Space only',multiplier:0,includes:'Empty space, ready for your own equipment and displays.'},
retail:{label:'Retail setup',multiplier:1,includes:'Clothing rails, a sales counter and a mirror.'},
brand:{label:'Brand display',multiplier:1.5,includes:'Clothing rails, a sales counter, a mirror, display lights, branded panels and a small fitting area.'}
};
function round(value){return Math.round(value/100)*100;}
function estimate(venue,options){
if(!venue||!seasons[options.season]||![7,14,28].includes(options.days)||![20,40,60].includes(options.area)||!setups[options.setup])throw new Error('Choose a location, season, length of stay, size and setup.');
var scale=options.area/venue.referenceArea;
var rent=round(venue.referenceRent*scale*(options.days/14)*seasons[options.season].multiplier);
var setup=round(venue.referenceSetup*scale*setups[options.setup].multiplier);
var storage=options.storage?options.days*300:0;
var signs=options.signs?6000:0;
var deposit=round(venue.referenceDeposit*scale);
return {rent:rent,setup:setup,storage:storage,signs:signs,deposit:deposit,subtotal:rent+setup+storage+signs,total:rent+setup+storage+signs+deposit};
}
function convertedAmount(amount,currency,rate){
return currency==='JPY'?Math.round(amount*rate):amount;
}
function formatMoney(amount,currency,rate){
var value=convertedAmount(amount,currency,rate);
return (currency==='JPY'?'¥':'THB ')+value.toLocaleString('en-US');
}
if(typeof module!=='undefined'&&module.exports)module.exports={estimate:estimate,seasons:seasons,setups:setups,convertedAmount:convertedAmount,formatMoney:formatMoney};
if(typeof document==='undefined')return;
var form=document.getElementById('rental-form');
if(!form)return;
var venues=JSON.parse(document.getElementById('rental-data').textContent);
var locationField=document.getElementById('rental-location');
var requested=new URLSearchParams(window.location.search).get('location');
if(venues.some(function(v){return v.slug===requested;}))locationField.value=requested;
var result=document.getElementById('rental-result');
var intro=document.getElementById('rental-intro');
var status=document.getElementById('rental-status');
var hasEstimate=false;
var converter=document.getElementById('estimate-currency');
var exchangeRate=JSON.parse(document.getElementById('exchange-rate-data').textContent);
function money(n){return formatMoney(n,converter.value,exchangeRate.rate);}
function renderCurrency(){
result.querySelectorAll('[data-thb]').forEach(function(element){
element.textContent=money(Number(element.dataset.thb));
});
document.getElementById('estimate-currency-note').textContent=converter.value==='JPY'?'Includes the refundable deposit. Amounts shown in Japanese yen (JPY).':'Includes the refundable deposit. All prices are in Thai baht (THB).';
document.getElementById('conversion-rounding').hidden=converter.value!=='JPY';
}
converter.addEventListener('change',function(){
renderCurrency();
status.textContent=converter.value==='JPY'?'Estimate shown in Japanese yen.':'Estimate shown in Thai baht.';
});
function addRow(label,value,extraClass){
var row=document.createElement('div');
if(extraClass)row.className=extraClass;
var dt=document.createElement('dt');dt.textContent=label;
var dd=document.createElement('dd');dd.dataset.thb=String(value);dd.textContent=money(value);
row.appendChild(dt);row.appendChild(dd);
document.getElementById('estimate-breakdown').appendChild(row);
}
form.addEventListener('change',function(){
var selectedSetup=document.getElementById('rental-setup').value;
document.getElementById('rental-setup-info').textContent=setups[selectedSetup]?setups[selectedSetup].includes:'Equipment and fitting areas depend on the setup.';
if(!hasEstimate)return;
result.hidden=true;intro.hidden=false;status.textContent='Options changed. View rates for the new estimate.';hasEstimate=false;
});
form.addEventListener('submit',function(event){
event.preventDefault();
if(!form.reportValidity())return;
var venue=venues.find(function(v){return v.slug===locationField.value;});
var options={season:document.getElementById('rental-season').value,days:Number(document.getElementById('rental-duration').value),area:Number(document.getElementById('rental-area').value),setup:document.getElementById('rental-setup').value,storage:document.getElementById('rental-storage').checked,signs:document.getElementById('rental-signs').checked};
var quote;
try{quote=estimate(venue,options);}catch(error){status.textContent=error.message;return;}
document.getElementById('estimate-heading').textContent=venue.name;
document.getElementById('estimate-summary').textContent=seasons[options.season].label+' · '+options.days+' days · '+options.area+' m² · '+setups[options.setup].label;
document.getElementById('estimate-breakdown').replaceChildren();
addRow('Space rental',quote.rent);
addRow('Setup',quote.setup);
if(options.storage)addRow('Extra stock storage',quote.storage);
if(options.signs)addRow('Printed brand signs',quote.signs);
addRow('Rent, setup & extras',quote.subtotal,'estimate-subtotal');
addRow('Refundable deposit',quote.deposit);
document.getElementById('estimate-total').dataset.thb=String(quote.total);
renderCurrency();
document.getElementById('estimate-inclusions').textContent=setups[options.setup].includes+(options.storage?' Extra stock storage is included.':'')+(options.signs?' Printed brand signs are included.':'');
intro.hidden=true;result.hidden=false;hasEstimate=true;
status.textContent='Estimate ready for '+venue.name+'.';
document.getElementById('estimate-heading').focus();
});
})();