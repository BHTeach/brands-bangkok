import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const venues=JSON.parse(await fs.readFile(path.join(root,'venues.json'),'utf8'));
const themes=JSON.parse(await fs.readFile(path.join(root,'location-themes.json'),'utf8'));
const accessGuide=JSON.parse(await fs.readFile(path.join(root,'access-guide.json'),'utf8'));
const output=path.join(root,'preview');
await fs.mkdir(output,{recursive:true});
const mime={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.json':'application/json','.pdf':'application/pdf'};
const server=http.createServer(async(req,res)=>{
 try{
  const url=new URL(req.url,'http://127.0.0.1');
  let relative=decodeURIComponent(url.pathname).replace(/^\/brands-bangkok\//,'');
  if(!relative||relative.endsWith('/'))relative+='index.html';
  const target=path.resolve(root,relative);
  if(!target.startsWith(root+path.sep))throw Error('Invalid path');
  res.setHeader('Content-Type',mime[path.extname(target)]||'application/octet-stream');
  res.end(await fs.readFile(target));
 }catch(error){res.statusCode=404;res.end('Not found');}
});
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
const base='http://127.0.0.1:'+server.address().port+'/brands-bangkok/';
const browser=await chromium.launch();
const context=await browser.newContext({viewport:{width:1440,height:1100},reducedMotion:'reduce'});
const page=await context.newPage();
const errors=[];
page.on('pageerror',error=>errors.push(error.message));
page.on('response',response=>{if(response.url().startsWith(base)&&response.status()>=400)errors.push(response.status()+' '+response.url());});
const report={widths:[1440,900,375],profiles:[],rentalChecks:[],gateChecks:[],menuChecked:false};
try{
 await page.goto(base+'locations/centralworld.html');
 assert(await page.locator('#access-gate').isVisible());
 assert(await page.locator('#site-content').isHidden());
 await page.getByLabel('Password',{exact:true}).fill('wrong');
 await page.getByRole('button',{name:'Enter Brands Bangkok'}).click();
 assert((await page.locator('#access-error').innerText()).includes("isn't correct"));
 await page.getByLabel('Password',{exact:true}).fill('BHFutureLeaders');
 await page.getByRole('button',{name:'Enter Brands Bangkok'}).click();
 await page.locator('#site-content').waitFor({state:'visible'});
 report.gateChecks.push('direct-link gate','wrong password','correct password');
 for(const width of report.widths){
  await page.setViewportSize({width,height:1100});
  for(const v of venues){
   await page.goto(base+'locations/'+v.slug+'.html');
   await page.locator('.venue-photo-grid img').first().waitFor({state:'visible'});
   await page.locator('.venue-photo-grid img').evaluateAll(images=>Promise.all(images.map(image=>image.decode())));
   assert.equal(await page.locator('.venue-photo-grid img').count(),2);
   const content=await page.locator('#main').innerText();
   for(const key of ['intro','character','neighbourhood','business','beyond'])assert(content.includes(v[key]),v.slug+' '+key);
   const accessText=await page.locator('.access-box').innerText();
   for(const key of ['train','walk','route'])assert(accessText.includes(accessGuide.venues[v.slug][key]),v.slug+' '+key);
   assert(accessText.includes(accessGuide.note));
   if(width===375&&['centralworld','terminal-21-asok'].includes(v.slug))await page.locator('.access-box').screenshot({path:path.join(output,'access-'+v.slug+'-'+width+'.png')});
   assert(!/THB\s*[\d,]+/.test(content),v.slug+' leaked pricing');
   assert((await page.locator('body').getAttribute('class')).includes('theme-'+v.slug));
   const actual=await page.locator('body').evaluate(el=>getComputedStyle(el).getPropertyValue('--venue-accent').trim());
   assert.equal(actual,themes[v.slug].accent);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),v.slug+' overflow at '+width);
   if(width===1440||width===375)await page.screenshot({path:path.join(output,v.slug+'-'+width+'.jpg'),type:'jpeg',quality:78});
   report.profiles.push({slug:v.slug,width,photos:2,copy:true,theme:true,overflow:false});
  }
  for(const relative of ['index.html','locations/index.html','planning.html','about.html','sources.html','rental.html','print-locations.html','print-rental.html']){
   await page.goto(base+relative);
   assert(await page.locator('#site-content').isVisible(),relative+' gate persistence');
   // The printable resource pages deliberately retain their fixed A4 width.
   if(!relative.startsWith('print-'))assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1),relative+' overflow at '+width);
   if(relative==='index.html'||relative==='locations/index.html')assert.equal(await page.locator('.location-card').count(),5);
   if(relative==='locations/index.html'){
    await page.locator('#access-map img').evaluate(image=>image.decode());
    assert.equal(await page.locator('.access-summary li').count(),5);
    assert((await page.locator('#access-map').innerText()).includes(accessGuide.mrt));
    if(width===375)assert(await page.locator('.access-map-scroll').evaluate(el=>el.scrollWidth>el.clientWidth));
    if(width===1440)await page.locator('.access-map-scroll').screenshot({path:path.join(output,'bangkok-access-map.png')});
   }
  }
 }
 await page.goto(base+'locations/centralworld.html');
 await page.getByRole('link',{name:'See the rail access map'}).click();
 assert.equal(new URL(page.url()).hash,'#access-map');
 await page.setViewportSize({width:1440,height:1100});
 await page.goto(base+'rental.html?location=centralworld');
 assert.equal(await page.locator('#rental-location').inputValue(),'centralworld');
 for(const id of ['rental-season','rental-duration','rental-area','rental-setup'])assert.equal(await page.locator('#'+id).inputValue(),'');
 await page.getByRole('button',{name:'View rates'}).click();
 assert(await page.locator('#rental-result').isHidden());
 await page.getByLabel('Season',{exact:true}).selectOption('aug-oct');
 await page.getByLabel('Length of stay',{exact:true}).selectOption('14');
 await page.getByLabel('Space size',{exact:true}).selectOption('40');
 await page.getByLabel('Setup',{exact:true}).selectOption('retail');
 await page.getByRole('button',{name:'View rates'}).click();
 assert.equal(await page.locator('#estimate-total').innerText(),'THB 155,300');
 await page.getByLabel('Currency Converter',{exact:true}).selectOption('JPY');
 assert.equal(await page.locator('#estimate-total').innerText(),'¥734,378');
 await page.getByLabel('Currency Converter',{exact:true}).selectOption('THB');
 assert.equal(await page.locator('#estimate-total').innerText(),'THB 155,300');
 await page.getByLabel('Season',{exact:true}).selectOption('nov-jan');
 assert(await page.locator('#rental-result').isHidden());
 await page.getByRole('button',{name:'View rates'}).click();
 assert.equal(await page.locator('#estimate-total').innerText(),'THB 188,900');
 await page.getByLabel('Season',{exact:true}).selectOption('aug-oct');
 await page.getByLabel('Extra stock storage',{exact:true}).check();
 await page.getByLabel('Printed brand signs',{exact:true}).check();
 await page.getByRole('button',{name:'View rates'}).click();
 assert.equal(await page.locator('#estimate-total').innerText(),'THB 165,500');
 report.rentalChecks=['location preselection','blank required options','validity','THB total and deposit','JPY conversion','currency round trip','changed options hide old estimate','season change','storage and signs'];
 await page.setViewportSize({width:375,height:900});
 await page.getByRole('button',{name:'Menu',exact:true}).click();
 assert.equal(await page.getByRole('button',{name:'Menu',exact:true}).getAttribute('aria-expanded'),'true');
 assert(await page.locator('#navigation').isVisible());
 await page.keyboard.press('Escape');
 assert.equal(await page.getByRole('button',{name:'Menu',exact:true}).getAttribute('aria-expanded'),'false');
 report.menuChecked=true;
 await page.getByRole('button',{name:'Lock site',exact:true}).click();
 assert(await page.locator('#site-content').isHidden());
 assert(await page.locator('#access-gate').isVisible());
 report.gateChecks.push('lock site');
 const noJs=await browser.newContext({javaScriptEnabled:false});
 const locked=await noJs.newPage();await locked.goto(base+'locations/siam-center.html');
 assert(await locked.locator('#site-content').isHidden());
 report.gateChecks.push('JavaScript-disabled gate');
 await noJs.close();
 assert.deepEqual(errors,[]);
 report.accessMapChecked=true;
 report.accessBoxesChecked=5;
 report.browserErrors=errors;
 await fs.writeFile(path.join(output,'website-checks.json'),JSON.stringify(report,null,2)+'\n');
 console.log('Checked five profiles at three widths, both photos, source copy, navigation, password gate and rental/currency interactions.');
}finally{await browser.close();await new Promise(resolve=>server.close(resolve));}
