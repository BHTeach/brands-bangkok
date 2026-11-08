import fs from 'node:fs/promises';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const venues=JSON.parse(await fs.readFile(path.join(root,'venues.json'),'utf8'));
const accessGuide=JSON.parse(await fs.readFile(path.join(root,'access-guide.json'),'utf8'));
const rate=JSON.parse(await fs.readFile(path.join(root,'exchange-rate.json'),'utf8'));
const context={module:{exports:{}}};
vm.runInNewContext(await fs.readFile(path.join(root,'assets/rental.js'),'utf8'),context);
const {estimate,seasons,setups}=context.module.exports;
const areas=[20,40,60], days=[7,14,28], seasonKeys=Object.keys(seasons);
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const fmt=n=>n.toLocaleString('en-US');
const paras=[
 ['The retail character','character'],['Around the address','neighbourhood'],
 ['Getting here','access'],['A fashion business perspective','business'],['Beyond fashion','beyond']
];
const services=[
 ['Short-term retail','A space for a new collection, a product display or a first visit to the city. Rental options are available at all five locations, with a choice of dates, space sizes and setup.'],
 ['Brand launches and events','A launch can bring your products and brand story to a new audience. Displays, signs and event space can be arranged to match the location and the collection.'],
 ['Store setup','From clothing rails and a sales counter to display lights and fitting areas, setup can be simple or more complete. Extra storage and printed signs are also available.'],
 ['A longer-term home','For permanent stores, space size, design and lease length are agreed separately. Each of our location profiles gives a view of the shopping offer and the surrounding area.'],
 ['Local arrangements','Delivery access, opening times and the exact space are confirmed with the final offer. Staff, stock and payment equipment are arranged separately.']
];
const terms=[
 'Rent covers the full stay shown in the table. Setup is charged once. Extra stock storage is charged for the full stay. Printed brand signs are charged once.',
 'The refundable deposit is paid before opening. It is returned after the space is checked, if there is no damage or unpaid charge.',
 'Staff, stock, payment equipment, electricity and taxes are not included.',
 'An estimate does not reserve a space. Exact dates and the position of the space are confirmed before booking.'
];
const model={rate,accessGuide,services,terms,sections:paras,seasons:seasonKeys.map(k=>({key:k,label:seasons[k].label})),setups:Object.entries(setups).map(([key,s])=>({key,label:s.label,includes:s.includes})),venues:venues.map(v=>{
 const ref={referenceArea:v.size,referenceRent:v.rent,referenceSetup:v.setup,referenceDeposit:v.deposit};
 return {...v,
  rents:areas.flatMap(area=>days.map(day=>({area,days:day,values:seasonKeys.map(season=>estimate(ref,{season,days:day,area,setup:'space'}).rent)}))),
  charges:areas.map(area=>{const q=setup=>estimate(ref,{season:'aug-oct',days:14,area,setup});return {area,space:q('space').setup,retail:q('retail').setup,brand:q('brand').setup,deposit:q('space').deposit};})
 };
})};
await fs.mkdir(path.join(root,'print'),{recursive:true});
await fs.writeFile(path.join(root,'print','print-data.json'),JSON.stringify(model,null,2)+'\n');
const foot=(label,n)=>'<footer><span>Brands Bangkok · '+label+'</span><span>'+n+' / '+(label==='Location guide'?7:6)+'</span></footer>';
const brand='<div class="print-brand"><b>B.</b><span>Brands Bangkok<small>Fashion. Retail. Possibility.</small></span></div>';
const page=(body,label,n,id)=>'<section class="paper" id="'+id+'">'+brand+body+foot(label,n)+'</section>';
const websiteQr='<a class="print-qr" href="https://bhteach.github.io/brands-bangkok/"><img src="assets/website-qr.svg" alt="QR code for the Brands Bangkok website"><span>Website version</span></a>';
const h=(eyebrow,title,lead='')=>'<p class="kicker">'+eyebrow+'</p><h1>'+title+'</h1>'+(lead?'<p class="intro">'+lead+'</p>':'');
const table=(headers,rows,cls='')=>'<table class="'+cls+'"><thead><tr>'+headers.map(s=>'<th scope="col">'+s+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map((s,i)=>i===0?'<th scope="row">'+s+'</th>':'<td>'+s+'</td>').join('')+'</tr>').join('')+'</tbody></table>';
const rateNote='<p class="rate"><strong>Currency conversion:</strong> 1 THB = ¥'+rate.rate+' · '+rate.displayDate+' · <a href="'+rate.sourceUrl+'">'+rate.sourceName+'</a><br>Thai baht × '+rate.rate+' = Japanese yen. Round to the nearest yen.</p>';
let locations=page(h('The location collection','Your brand. Bangkok’s next chapter.','Bring your business to Bangkok. Discover five shopping destinations for international fashion and retail brands.')+
 '<p>Brands Bangkok brings the city closer to overseas fashion and retail businesses. Our guide introduces five centres, from local fashion and Thai design to international and luxury brands.</p>'+
 table(['Location','Retail setting','Rail access'],venues.map(v=>[esc(v.name),esc(v.type),esc(v.rail)]),'directory')+
 '<h2>Business services</h2>'+services.map(([a,b])=>'<h3>'+a+'</h3><p>'+b+'</p>').join('')+
 '<p class="small">Short-term rates are available in the separate <em>Retail spaces &amp; rates</em> booklet.</p>','Location guide',1,'location-guide');
locations+=page(h('Connected addresses',esc(accessGuide.title),'Station links and short walks to five shopping destinations.')+
 '<img src="assets/bangkok-access-map.svg" alt="Rail connections for the five shopping locations. Diagram not to scale.">'+
 '<p><strong>BTS Skytrain</strong><br>'+esc(accessGuide.bts)+'</p><p><strong>MRT</strong><br>'+esc(accessGuide.mrt)+'</p>'+
 '<h2>From the station exit</h2><p>'+esc(accessGuide.note)+'</p>'+
 table(['Location','Approximate walk'],venues.map(v=>[esc(v.name),esc(accessGuide.venues[v.slug].mapWalk)])),
 'Location guide',2,'location-access-map');

for(const [i,v] of venues.entries()){
 locations+=page(h(esc(v.area)+' · Bangkok',esc(v.name),esc(v.intro))+
 '<p class="tagline">'+esc(v.line)+'</p><div class="facts"><p><strong>Retail setting</strong><br>'+esc(v.type)+'</p><p><strong>Rail access</strong><br>'+esc(v.rail)+'</p></div>'+
 '<img class="profile-photo" src="assets/'+v.slug+'.jpg" alt="'+esc(v.name)+' in Bangkok">'+
 '<p class="credit">Photo: <a href="'+esc(v.photoPage)+'">'+esc(v.photoAuthor)+'</a> · <a href="'+v.licenseUrl+'">'+esc(v.photoLicense)+'</a> · Resized and cropped. Original: Wikimedia Commons.</p>'+
 paras.map(([title,key])=>'<h2>'+title+'</h2><p>'+esc(v[key])+'</p>').join(''),'Location guide',i+3,v.slug);
}

// The print view uses the PDF's vector pages, with a semantic text version for accessibility.
const locationSections=locations.match(/<section class="paper"[\s\S]*?<\/section>/g);
locations=locationSections.map((section,i)=>{
 const readable=section.replace(/^<section[^>]*>/,'').replace(/<\/section>$/,'').replace(/<div class="print-brand">[\s\S]*?<\/div>/,'').replace(/<footer>[\s\S]*?<\/footer>/,'').replace(/<img[^>]*>/g,'').replace(/<p class="credit">[\s\S]*?<\/p>/,'');
 return '<section class="paper premium"><img class="premium-page" src="print/location-pages/page-'+(i+1)+'.svg?v=20261108-qr" alt=""><div class="print-transcript">'+readable+'</div></section>';
}).join('');

let rental=page(websiteQr+h('Business services','Retail spaces &amp; rates.','Space for your next collection. Rental options at five Bangkok shopping centres.')+
 '<p>Rates vary by location, season, length of stay and space size. Each location has its own rate page.</p>'+
 '<h2>Space and stay options</h2>'+table(['Option','Choices'],[['Space size','Compact · 20 m² / Standard · 40 m² / Large · 60 m²'],['Length of stay','1 week · 7 days / 2 weeks · 14 days / 4 weeks · 28 days'],['Season','Feb – Apr / May – Jul / Aug – Oct / Nov – Jan']])+
 '<p class="small">Any listed space size can be combined with any listed stay and season.</p>'+
 '<h2>Setup options</h2>'+table(['Setup','What is included'],model.setups.map(s=>[s.label,s.includes]))+
 '<h2>Optional extras</h2>'+table(['Service','Price'],[['Extra stock storage','THB 300 per day · 7 days: 2,100 · 14 days: 4,200 · 28 days: 8,400'],['Printed brand signs','THB 6,000 · One-time charge']])+
 '<h2>Your total before opening</h2><p>Space rental + setup + optional extras + refundable deposit.</p>'+
 '<div class="terms">'+terms.map(t=>'<p>'+t+'</p>').join('')+'</div>'+rateNote,'Retail spaces & rates',1,'rental-guide');
for(const[i,v]of model.venues.entries()){
 rental+=page(h(esc(v.area)+' · Retail space',esc(v.name),'Short-term retail · All table prices are in Thai baht (THB).')+
 '<h2>Space rental for the full stay</h2><p>Rental prices below cover the full stay. Other charges are added separately.</p>'+
 table(['Space','Stay','Feb – Apr','May – Jul','Aug – Oct','Nov – Jan'],v.rents.map(r=>[r.area+' m²',r.days+' days',...r.values.map(fmt)]),'rents')+
 '<h2>Setup and refundable deposit</h2><p>Choose one setup. Setup is charged once. The refundable deposit is separate.</p>'+
 table(['Space','Space only','Retail setup','Brand display','Refundable<br>deposit'],v.charges.map(r=>[r.area+' m²',fmt(r.space),fmt(r.retail),fmt(r.brand),fmt(r.deposit)]),'charges')+
 '<p class="small">Setup descriptions and full rental terms are on page 1.</p>'+
 '<h2>Optional extras</h2><p>Stock storage: THB 300 per day. Printed brand signs: THB 6,000 once.</p>'+
 '<div class="total-rule"><strong>Total before opening = rent + setup + extras + deposit.</strong></div>'+
 '<p class="small">The deposit is returned if there is no damage or unpaid charge. Staff, stock, payment equipment, electricity and taxes are not included. Exact dates and position are confirmed before booking. All rental terms are on page 1.</p>'+rateNote,
 'Retail spaces & rates',i+2,'rates-'+v.slug);
}
const index=await fs.readFile(path.join(root,'index.html'),'utf8');
const prefix=index.split('<div id="site-content">')[0]
 .replace(/<title>.*?<\/title>/,'<title>Printed booklets | Brands Bangkok</title>')
 .replace('</head>','<link rel="stylesheet" href="assets/print.css?v=20261108-qr"></head>');
function output(body,kind){return prefix+'<div id="site-content"><div class="print-toolbar"><strong>Brands Bangkok · Printed booklets</strong><nav><a href="print-locations.html">Location guide</a><a href="print-rental.html">Retail spaces &amp; rates</a><a href="print/brands-bangkok-locations.pdf?v=20261108-qr">Location guide PDF</a><a href="print/brands-bangkok-rental-rates.pdf?v=20261108-qr">Rental booklet PDF</a></nav><button data-print>Print '+kind+'</button><button data-lock>Lock site</button></div><main>'+body+'</main></div></body></html>';}
await fs.writeFile(path.join(root,'print-pack.html'),output(locations+rental,'both booklets'));
await fs.writeFile(path.join(root,'print-locations.html'),output(locations,'location guide'));
await fs.writeFile(path.join(root,'print-rental.html'),output(rental,'rental booklet'));
console.log('Built 7-page location guide and 6-page rental booklet. Prices use assets/rental.js directly.');
