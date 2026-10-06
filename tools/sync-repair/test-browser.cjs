'use strict';
const fs=require('node:fs'),http=require('node:http'),vm=require('node:vm'),assert=require('node:assert/strict');
const {chromium,webkit,devices}=require('playwright');
let html=fs.readFileSync('index.html','utf8');
const scripts=[...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)];
for(let i=0;i<scripts.length;i++)new vm.Script(scripts[i][1],{filename:'inline-'+i+'.js'});
console.log('PASS Full inline JavaScript parses');
const end=html.lastIndexOf('})();');assert(end>=0);
html=html.slice(0,end)+`
window.__syncTest={
  setup:function(name){var c=ghConf();Object.assign(c,{repo:'test/planner',path:'progress.json',branch:'main',token:'TEST_ONLY',device:name,auto:false});ghSave();ghStart(false);},
  push:ghPush,pull:ghPull,cycle:ghCycle,
  config:ghConf,saveConfig:ghSave,
  state:function(){return state;},all:function(){return ghSnapshot();},
  noChange:function(){persist();},roll:plRoll,
  toggleAuto:function(on){ghConf().auto=on;ghSave();},
  status:function(){return document.getElementById('syState').textContent;}
};
`+html.slice(end);
const app=http.createServer((req,res)=>{if(req.url==='/'||req.url==='/index.html'){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});res.end(html);}else{res.writeHead(404);res.end();}});
let remote=null,sha=0,puts=0;const errors=[];
const browsers=[];
async function main(){
  await new Promise(resolve=>app.listen(0,'127.0.0.1',resolve));
  const base='http://127.0.0.1:'+app.address().port;
  const desktop=await chromium.launch({headless:true});browsers.push(desktop);
  const mobile=await webkit.launch({headless:true});browsers.push(mobile);
  async function make(browser,options,name){
    const ctx=await browser.newContext(options);
    await ctx.route('**/*',route=>route.request().url().startsWith(base)?route.continue():route.abort());
    await ctx.route('https://api.github.com/**',async route=>{
      const request=route.request();
      if(!request.url().includes('/repos/test/planner/contents/progress.json'))return route.fulfill({status:404,body:'{}'});
      if(request.method()==='PUT'){
        const data=request.postDataJSON();
        if(data.sha!==(remote?'blob'+sha:undefined))return route.fulfill({status:409,body:'{}'});
        remote=JSON.parse(Buffer.from(data.content,'base64').toString('utf8'));sha++;puts++;
        return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({content:{sha:'blob'+sha}})});
      }
      return route.fulfill({status:remote?200:404,contentType:'application/json',body:remote?JSON.stringify({sha:'blob'+sha,encoding:'base64',content:Buffer.from(JSON.stringify(remote)).toString('base64')}):'{}'});
    });
    const page=await ctx.newPage();page.on('pageerror',e=>errors.push(name+': '+e.message));
    await page.goto(base,{waitUntil:'load'});
    await page.waitForFunction(()=>!!window.__syncTest);
    await page.evaluate(n=>window.__syncTest.setup(n),name);
    return page;
  }
  const a=await make(desktop,{viewport:{width:1600,height:1100}},'Computer');
  const b=await make(mobile,{...devices['iPhone 13']},'iPhone');
  assert.equal(await a.locator('#totalBox #stepsList').count(),1);
  assert.equal(await b.locator('#totalBox #stepsList').count(),1);
  console.log('PASS Completed / Steps section retained on desktop and mobile');
  assert(await a.evaluate(()=>window.__syncTest.push(false)));
  assert(await b.evaluate(()=>window.__syncTest.pull(false)));
  await a.locator('#tasksInp').fill('SYNC TEST desktop');await a.locator('#tasksInp').press('Enter');
  await a.evaluate(()=>{window.__syncTest.config().remoteLead='iPhone';});
  await a.locator('#btnGhSave').click({force:true});
  await a.waitForFunction(()=>window.__syncTest.status().startsWith('Saved to GitHub'));
  assert(remote.spaces.states[remote.spaces.active].tasks.some(x=>x.t==='SYNC TEST desktop'));
  console.log('PASS Desktop Save button sends a task despite legacy iPhone leader');

  const desktopLine=a.locator('#tasksList [data-tdtext]').filter({hasText:'SYNC TEST desktop'}).first();
  const ctxProbeBefore=await a.evaluate(()=>{
    const els=[...document.querySelectorAll('#tasksList [data-tdtext]')];
    const el=els.find(x=>x.textContent.includes('SYNC TEST desktop'));
    const id=el&&el.getAttribute('data-tdtext');
    return {id:id, where:!!(id&&plWhere(id)), stateTasks:(state.tasks||[]).map(x=>({id:x.id,t:x.t})),
            domTasks:els.map(x=>({id:x.getAttribute('data-tdtext'),t:x.textContent}))};
  });
  console.log('CTX_PROBE_BEFORE '+JSON.stringify(ctxProbeBefore));
  await desktopLine.click({button:'right'});
  const ctxProbeAfter=await a.evaluate(()=>({show:document.getElementById('plMenu').classList.contains('show'),
    html:document.getElementById('plMenu').innerHTML,plFor:window.plFor||null}));
  console.log('CTX_PROBE_AFTER '+JSON.stringify(ctxProbeAfter));
  assert(await a.locator('#plMenu').evaluate(el=>el.classList.contains('show')));
  assert((await a.locator('#plMenu').innerText()).includes('Emoji'));
  await a.locator('#plMenu [data-plb="b"]').click();
  assert(await a.evaluate(()=>window.__syncTest.state().tasks.some(x=>x.t==='SYNC TEST desktop'&&x.b===true)));
  await desktopLine.click({button:'right'});
  await a.locator('#plMenu [data-ple="🔥"]').click();
  assert(await a.evaluate(()=>window.__syncTest.state().tasks.some(x=>x.t==='🔥 SYNC TEST desktop'&&x.b===true)));
  console.log('PASS Desktop right-click menu opens and applies bold plus emoji');
  assert(await b.evaluate(()=>window.__syncTest.pull(false)));
  assert(await b.evaluate(()=>window.__syncTest.state().tasks.some(x=>x.t==='SYNC TEST desktop')));
  console.log('PASS Desktop changes arrive in mobile WebKit');
  await a.locator('#tasksInp').fill('SYNC TEST desktop second');await a.locator('#tasksInp').press('Enter');
  await b.locator('#tasksInp').fill('SYNC TEST phone');await b.locator('#tasksInp').press('Enter');
  assert(await b.evaluate(()=>window.__syncTest.push(false)));
  assert(await a.evaluate(()=>window.__syncTest.push(false)));
  assert(await b.evaluate(()=>window.__syncTest.pull(false)));
  for(const page of [a,b]){
    assert(await page.evaluate(()=>['SYNC TEST desktop second','SYNC TEST phone'].every(t=>window.__syncTest.state().tasks.some(x=>x.t===t))));
  }
  console.log('PASS Independent edits from real Chromium and WebKit combine');
  const count=puts;
  await a.evaluate(()=>{window.__syncTest.noChange();window.__syncTest.roll();});
  assert(await a.evaluate(()=>window.__syncTest.push(false)));assert.equal(puts,count);
  console.log('PASS Five-minute calendar check cannot create a no-change overwrite');
  await a.locator('#stepsInp').fill('SYNC TEST next step');await a.locator('#stepsInp').press('Enter');
  assert(await a.evaluate(()=>window.__syncTest.push(false)));
  assert(await b.evaluate(()=>window.__syncTest.pull(false)));
  assert(await b.evaluate(()=>window.__syncTest.state().steps.some(x=>x.t==='SYNC TEST next step')));
  console.log('PASS New Steps section is saved and synchronized');
  await a.evaluate(()=>{document.activeElement.blur();window.__syncTest.toggleAuto(true);});
  await b.locator('#tasksInp').fill('SYNC TEST foreground');await b.locator('#tasksInp').press('Enter');
  assert(await b.evaluate(()=>window.__syncTest.push(false)));
  await a.evaluate(()=>window.dispatchEvent(new Event('focus')));
  await a.waitForFunction(()=>window.__syncTest.state().tasks.some(x=>x.t==='SYNC TEST foreground'));
  console.log('PASS Return to foreground retrieves remote changes automatically');
  await a.evaluate(()=>window.__syncTest.toggleAuto(false));
  await a.reload({waitUntil:'load'});await a.waitForFunction(()=>!!window.__syncTest);
  await a.evaluate(()=>window.__syncTest.setup('Computer'));
  assert(await a.evaluate(()=>window.__syncTest.state().tasks.some(x=>x.t==='SYNC TEST foreground')));
  assert.equal(await a.evaluate(()=>window.__syncTest.config().dirty),false);
  console.log('PASS Reload retains synchronized data without phantom dirty state');
  await a.locator('#btnSync').click({force:true});
  assert((await a.locator('#syLeadBox').innerText()).includes('Sync v2: all devices are equal'));
  assert(await a.locator('#syLead').isHidden());
  console.log('PASS Sync panel no longer blocks secondary devices');
  assert.deepEqual(errors,[]);
  console.log('PASS No runtime page errors in Chromium or WebKit');
  console.log('All browser integration checks passed. No live GitHub progress file was read or written.');
}
main().catch(e=>{console.error(e.stack);process.exitCode=1;}).finally(async()=>{for(const browser of browsers)await browser.close();app.close();});
