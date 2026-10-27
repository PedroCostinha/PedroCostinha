// SPDX-License-Identifier: MIT
// Copyright (c) 2026 PedroCostinha
// Requires Playwright in NODE_PATH or installed outside the production generators.
const fs=require('node:fs/promises'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..');
async function main(){
 const readme=await fs.readFile(path.join(root,'README.md'),'utf8');
 const pictures=[...readme.matchAll(/<picture>[\s\S]*?<\/picture>/g)].map(m=>m[0]).filter(p=>p.includes('assets/arcade/')||p.includes('assets/code-snake/'));
 assert.equal(pictures.length,2);
 const baseStyle='<meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#0d0d0f;color:#eee8e5;margin:0;font:14px Consolas,monospace}main{max-width:1100px;margin:30px auto;padding:16px}img{display:block;width:100%;height:auto}table{width:100%;table-layout:fixed;border-collapse:collapse}td,th{width:50%;padding:8px;vertical-align:top}th{text-align:left;color:#ed8893}p{color:#aaa0af;line-height:1.7}a{color:#ed8893}.single{max-width:1080px;margin:auto}h1{font-size:26px;letter-spacing:2px}@media(max-width:600px){main{padding:8px}td,th{padding:3px;font-size:10px}}</style>';
 const showcase=baseStyle+'<main><h1>ARCADE COLLECTION</h1><p>Duas demos em movimento. Arte original e contribuições reais.</p><h2>Barrel Quest</h2>'+pictures[0]+'<p><a href="https://pedrocostinha.github.io/arcade-collection/">Jogar Barrel Quest · 1.1.0</a></p><h2>Code Snake · em desenvolvimento</h2>'+pictures[1]+'<p>Protótipo demonstrativo. As demos usam o mesmo snapshot. O jogo tem pontuação própria da partida.</p></main>';
 const server=http.createServer(async(req,res)=>{
  try{
   const url=new URL(req.url,'http://localhost');
   if(url.pathname==='/'){res.setHeader('content-type','text/html; charset=utf-8');return res.end(showcase);}
   if(url.pathname==='/demo'){res.setHeader('content-type','text/html; charset=utf-8');return res.end(baseStyle+'<div class="single">'+pictures[1]+'</div>');}
   if(url.pathname==='/inspect'){res.setHeader('content-type','text/html; charset=utf-8');return res.end(await fs.readFile(path.join(root,'assets/code-snake/code-snake.svg')));}
   const file=path.resolve(root,'.'+decodeURIComponent(url.pathname));
   if(!file.startsWith(root+path.sep)||!file.endsWith('.svg')){res.writeHead(404);return res.end();}
   res.setHeader('content-type','image/svg+xml');res.end(await fs.readFile(file));
  }catch{res.writeHead(404);res.end();}
 });
 await new Promise(ok=>server.listen(process.argv.includes('--serve')?4176:0,'127.0.0.1',ok));
 const base=`http://127.0.0.1:${server.address().port}`;
 if(process.argv.includes('--serve')){console.log('Profile preview: '+base+'; /demo');return;}
 const {chromium,firefox}=require('playwright');const engine=process.env.ARCADE_BROWSER??'chrome';
 const browser=engine==='firefox'?await firefox.launch({headless:true}):await chromium.launch({channel:'chrome',headless:true});
 const output=path.resolve(process.env.SNAKE_EVIDENCE_DIR??path.join(root,'docs/code-snake',engine));await fs.mkdir(output,{recursive:true});
 const checks=[],errors=[];
 try{
  const page=await browser.newPage({viewport:{width:1200,height:800},reducedMotion:'no-preference'});page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(base+'/demo');await page.locator('img').evaluate(img=>img.decode());
  const a=await page.locator('img').screenshot();await page.waitForTimeout(850);const b=await page.locator('img').screenshot();assert(!a.equals(b),'SVG animates when embedded as img');
  await page.waitForTimeout(2000);await page.screenshot({path:path.join(output,'01-demo-desktop.png'),fullPage:true});
  await page.goto(base+'/');await page.waitForTimeout(2000);await page.screenshot({path:path.join(output,'02-showcase-desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:850});await page.goto(base+'/demo');
  assert.match(await page.locator('img').evaluate(img=>img.currentSrc),/code-snake-mobile.svg$/);
  await page.waitForTimeout(2200);await page.screenshot({path:path.join(output,'03-demo-mobile.png'),fullPage:true});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.goto(base+'/');await page.screenshot({path:path.join(output,'04-showcase-mobile.png'),fullPage:true});
  await page.goto(base+'/demo');await page.emulateMedia({reducedMotion:'reduce'});
  await page.locator('img').evaluate(img=>img.decode());assert.match(await page.locator('img').evaluate(img=>img.currentSrc),/code-snake-static-mobile.svg$/);
  const still=await page.locator('img').screenshot();await page.waitForTimeout(600);assert(still.equals(await page.locator('img').screenshot()),'Static fallback stays pixel-identical');
  await page.screenshot({path:path.join(output,'05-mobile-static.png'),fullPage:true});
  checks.push('SVG animates inside img; desktop/mobile sources, reduced-motion static source and stable pixels; contained 390px preview');
  await page.emulateMedia({reducedMotion:'no-preference'});await page.goto(base+'/inspect');
  const loop=await page.evaluate(()=>{
   for(const a of document.getAnimations()){a.pause();a.currentTime=17999;}
   const end=Number(getComputedStyle(document.querySelector('.curtain')).opacity);
   for(const a of document.getAnimations())a.currentTime=18001;
   const begin=Number(getComputedStyle(document.querySelector('.curtain')).opacity);
   return {end,begin,days:document.querySelectorAll('[data-date]').length};
  });assert(loop.end<.01&&loop.begin<.01);assert(loop.days>=364);
  await page.emulateMedia({reducedMotion:'reduce'});assert.equal(await page.locator('.moving').first().evaluate(e=>getComputedStyle(e).display),'none');
  checks.push('Loop reset hidden at 18s boundary; all annual dates retained; SVG internal reduced-motion disables moving layers');
  await page.emulateMedia({reducedMotion:'no-preference'});await page.goto(base+'/assets/code-snake/code-snake-mobile.svg');
  const mobileSpacing=await page.evaluate(()=>{
   for(const a of document.getAnimations()){a.pause();a.currentTime=16000;}
   const completion=document.querySelector('.complete text').getBoundingClientRect();
   const calendar=[...document.querySelectorAll('text')].find(e=>e.textContent==='ANO COMPLETO / CONTRIBUIÇÕES REAIS').getBoundingClientRect();
   return {gap:calendar.top-completion.bottom,viewport:innerWidth};
  });assert(mobileSpacing.gap>=4,'Mobile completion and annual-calendar labels have a readable gap');
  checks.push('390px completion and annual-calendar labels separated by at least four screen pixels');
  assert.equal(errors.length,0);
  await fs.writeFile(path.join(output,'results.json'),JSON.stringify({engine,version:browser.version(),checks,loop,mobileSpacing,errors},null,2));console.log(JSON.stringify({engine,checks}));
 }finally{await browser.close();server.closeAllConnections();await new Promise(ok=>server.close(ok));}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
