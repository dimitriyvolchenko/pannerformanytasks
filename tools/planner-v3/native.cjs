'use strict';
const fs=require('node:fs'),http=require('node:http'),assert=require('node:assert/strict'),vm=require('node:vm');
const {chromium,webkit,devices}=require('playwright');
let html=fs.readFileSync('fixed.html','utf8');
for(const [i,m] of [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].entries())new vm.Script(m[1],{filename:'inline-'+i+'.js'});
let i=html.lastIndexOf('})();');assert(i>0);
html=html.slice(0,i)+`window.__test={state:()=>state,spaces:()=>spaces,config:ghConf,saveConfig:ghSave,push:ghPush,pull:ghPull,
core:ghCore,snapshot:ghSnapshot,refresh:refreshAll,render:render,persist:persist,zoom:setLocalZoom,load:loadProgressText,
editing:ghEditing,cycle:ghCycle,roll:plRoll,
setup:function(name){Object.assign(ghConf(),{repo:'test/planner',path:'progress.json',branch:'main',token:'TEST_ONLY',device:name,auto:false});ghSave();ghStart(false);},
auto:function(on){ghConf().auto=on;ghSave();},status:()=>document.getElementById('syState').textContent};\n`+html.slice(i);
let remote=null,sha=0,puts=0;const errors=[],browsers=[];
const app=http.createServer((req,res)=>{res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(html);});
async function main(){
 await new Promise(r=>app.listen(0,'127.0.0.1',r));const base='http://127.0.0.1:'+app.address().port;
 const desktop=await chromium.launch({headless:true}),phone=await webkit.launch({headless:true});browsers.push(desktop,phone);
 async function make(browser,options,name,existing){
  const ctx=existing||await browser.newContext(options);
  if(!existing){
   await ctx.route('**/*',r=>r.request().url().startsWith(base)?r.continue():r.abort());
   await ctx.route('https://api.github.com/**',async r=>{
    const q=r.request();assert(q.url().startsWith('https://api.github.com/repos/test/planner/'));
    if(!q.url().includes('/contents/progress.json'))return r.fulfill({status:404,body:'{}'});
    if(q.method()==='PUT'){
     const d=q.postDataJSON();if(d.sha!==(remote?String(sha):undefined))return r.fulfill({status:409,body:'{}'});
     remote=JSON.parse(Buffer.from(d.content,'base64').toString('utf8'));sha++;puts++;
     return r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({content:{sha:String(sha)}})});
    }
    return r.fulfill({status:remote?200:404,contentType:'application/json',body:remote?JSON.stringify({sha:String(sha),encoding:'base64',content:Buffer.from(JSON.stringify(remote)).toString('base64')}):'{}'});
   });
  }
  const p=await ctx.newPage();p.setDefaultTimeout(12000);p.on('pageerror',e=>errors.push(name+': '+e.message));
  await p.goto(base,{waitUntil:'load'});await p.waitForFunction(()=>!!window.__test);await p.evaluate(n=>__test.setup(n),name);return p;
 }
 const a=await make(desktop,{viewport:{width:1600,height:1000}},'Desktop');
 const b=await make(phone,devices['iPhone 13'],'iPhone');
 assert(await a.evaluate(()=>__test.push(false)));assert(await b.evaluate(()=>__test.pull(false)));
 for(const p of [a,b]){assert.equal(await p.locator('#totalBox #stepsInp').count(),1);assert.equal(await p.locator('#hzVal').innerText(),'100%');}
 console.log('PASS Chromium and iPhone WebKit: complete app loads at 100%, Steps present');
 await a.evaluate(()=>__test.auto(true));await a.locator('#tasksInp').fill('NATIVE desktop');await a.locator('#tasksInp').press('Enter');
 await a.waitForFunction(()=>!__test.config().dirty);assert.equal(await a.evaluate(()=>document.activeElement.id),'tasksInp');
 assert(remote.spaces.states[remote.spaces.active].tasks.some(x=>x.t==='NATIVE desktop'));
 assert(await b.evaluate(()=>__test.pull(false)));assert(await b.evaluate(()=>__test.state().tasks.some(x=>x.t==='NATIVE desktop')));
 console.log('PASS Desktop Enter autosaves while its empty input retains focus; phone receives it');
 await a.evaluate(()=>__test.auto(false));await b.locator('#stepsInp').fill('NATIVE phone');await b.locator('#stepsInp').press('Enter');
 assert(await b.evaluate(()=>__test.push(false)));assert(await a.evaluate(()=>__test.pull(false)));
 assert(await a.evaluate(()=>__test.state().steps.some(x=>x.t==='NATIVE phone')));
 console.log('PASS Phone save reaches desktop in the opposite direction');
 await a.evaluate(()=>__test.zoom(1.2));const n=puts;assert(await a.evaluate(()=>__test.push(false)));assert.equal(puts,n);
 assert(await b.evaluate(()=>__test.pull(false)));assert.equal(await b.locator('#hzVal').innerText(),'100%');
 await a.reload({waitUntil:'load'});await a.evaluate(()=>__test.setup('Desktop'));assert.equal(await a.locator('#hzVal').innerText(),'120%');
 await a.evaluate(()=>__test.zoom(1));console.log('PASS Device zoom stays local, survives real reload and creates no cloud commit');
 // Two real browser tabs share native localStorage; no emulated storage for this check.
 const c=await make(desktop,{},'Second desktop tab',a.context());
 await a.locator('#stepsInp').fill('NATIVE tab A');await a.locator('#stepsInp').press('Enter');
 await c.locator('#stepsInp').fill('NATIVE tab B');await c.locator('#stepsInp').press('Enter');
 for(const p of [a,c])await p.waitForFunction(()=>['NATIVE tab A','NATIVE tab B'].every(t=>__test.state().steps.some(x=>x.t===t)));
 await c.close();console.log('PASS Real storage events preserve edits across two browser tabs');
 const line=a.locator('#tasksList [data-tdtext]').filter({hasText:'NATIVE desktop'}).first();await line.click({button:'right'});
 await a.locator('#plMenu [data-plb="b"]').click();await a.locator('#plMenu [data-ple="🔥"]').click();
 assert(await a.evaluate(()=>__test.state().tasks.some(x=>x.t==='🔥 NATIVE desktop'&&x.b)));
 await a.keyboard.press('Escape');console.log('PASS Desktop right-click applies bold and emoji');
 await a.locator('#tasksBox [data-spot="tasks"]').click();await a.locator('#totalBox [data-spot="done"]').click();await a.locator('#btnMega').click();
 await a.waitForFunction(()=>document.body.classList.contains('megaon'));await a.waitForTimeout(1100);
 await line.click({button:'right'});await a.locator('#plMenu [data-plb="i"]').click();await a.keyboard.press('Escape');
 assert(await a.evaluate(()=>document.body.classList.contains('megaon')));
 await a.evaluate(()=>__test.refresh());assert.equal(await a.locator('#stepsBox').count(),1);
 await a.locator('#megaOut').click();await a.waitForFunction(()=>!document.body.classList.contains('megaon'));await a.waitForTimeout(1000);
 assert.equal(await a.locator('#hero #totalBox #stepsBox').count(),1);
 console.log('PASS Mega Focus menu, Escape, rebuild and returning to the normal layout');
 for(const p of [a,b]){await p.evaluate(()=>document.activeElement.blur());assert(await p.evaluate(()=>__test.push(false)));}
 assert.deepEqual(errors,[]);console.log('PASS No runtime JavaScript errors in Chromium or mobile WebKit');
 console.log('All native integration tests passed; no real GitHub progress file was read or written.');
}
main().catch(e=>{console.error(e.stack);process.exitCode=1;}).finally(async()=>{for(const b of browsers)await b.close();app.close();});
