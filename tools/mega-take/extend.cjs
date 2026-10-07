'use strict';
const fs=require('node:fs');
let code=fs.readFileSync('tools/mega-take/base.cjs','utf8');
const anchor=" for(const p of [a,b]){await p.evaluate(()=>document.activeElement.blur());assert(await p.evaluate(()=>__test.push(false)));}";
if(!code.includes(anchor))throw new Error('Test anchor missing');
const extra=String.raw`
 await a.evaluate(()=>{var s=__test.state();s.heroFree=true;s.spot={done:true,off:true,par:true,today:true,tasks:true,launch:true};var first=document.querySelector('.proj');if(first)s.spot[first.dataset.proj]=true;s.tasks=Array.from({length:24},(_,i)=>({id:'tk_probe_'+i,t:'Test task '+i+' with useful detailed text',done:false}));s.today=Array.from({length:20},(_,i)=>({id:'td_probe_'+i,t:'Priority '+i+' with useful detailed text',done:false}));s.steps=Array.from({length:10},(_,i)=>({id:'sp_probe_'+i,t:'Step '+i,done:false}));__test.persist();__test.refresh();});
 assert(await a.evaluate(()=>__test.push(false)));
 for(const [label,width,height] of [['iPad landscape',1024,768],['iPad portrait',820,1180]]){
  const ip=await make(phone,{viewport:{width,height},deviceScaleFactor:2,isMobile:true,hasTouch:true,userAgent:'Mozilla/5.0 (iPad; CPU OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'},label);
  assert(await ip.evaluate(()=>__test.pull(false)));
  await ip.locator('#btnMega').tap();await ip.waitForFunction(()=>document.body.classList.contains('megaon'));await ip.waitForTimeout(1900);
  const snap=()=>ip.evaluate(()=>{var ov=document.getElementById('megaOv');return {width:innerWidth,doc:document.documentElement.clientWidth,ov:ov.getBoundingClientRect().width,scroll:ov.scrollTop,max:ov.scrollHeight-ov.clientHeight,on:document.body.classList.contains('megaon'),table:ov.classList.contains('mgtab'),bar:document.getElementById('saveCol').parentElement.id,cards:[...ov.querySelectorAll('.megaitem')].map(x=>({id:x.id||x.dataset.proj,seat:x.parentElement.id,anim:getComputedStyle(x).animationName}))};});
  const initial=await snap();assert.equal(initial.width,width,JSON.stringify(initial));assert.equal(initial.ov,width);assert(initial.table);
  await ip.evaluate(()=>{window.__toolbarMoved=false;var sc=document.getElementById('saveCol');new MutationObserver(records=>{if(records.some(r=>[...r.removedNodes].includes(sc)))window.__toolbarMoved=true;}).observe(document.body,{childList:true,subtree:true});});
  for(let n=0;n<3;n++){
   await ip.evaluate(()=>document.getElementById('megaOv').scrollTop=250);const before=await snap();
   const text=label+' remote edit '+n,oldPuts=puts;
   await a.evaluate(t=>{__test.state().tasks[0].t=t;__test.persist();},text);assert(await a.evaluate(()=>__test.push(false)));
   await ip.locator('#btnGhTake').tap();await ip.waitForFunction(t=>__test.state().tasks[0].t===t,text);await ip.waitForFunction(()=>!document.getElementById('btnGhTake').classList.contains('busy'));
   const after=await snap();assert(after.on&&after.table,JSON.stringify(after));assert.equal(after.width,width);assert.equal(after.ov,width);assert.equal(after.bar,'megaBar');
   assert(Math.abs(after.scroll-Math.min(before.scroll,after.max))<=1,JSON.stringify({before,after}));
   assert.deepEqual(after.cards.map(x=>[x.id,x.seat]),before.cards.map(x=>[x.id,x.seat]));assert(after.cards.every(x=>x.anim==='none'));
   assert.equal(puts,oldPuts+1,'Take must not write to GitHub');assert.equal(await ip.evaluate(()=>window.__toolbarMoved),false);
   assert(await ip.locator('#btnGhTake').evaluate(el=>{var r=el.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return el===hit||el.contains(hit);}));
  }
  console.log('PASS WebKit '+label+': three Take taps retain viewport, card seats, scroll and toolbar; updates received without cloud writes');
  const oldPuts=puts,before=await snap();await ip.locator('#btnGhTake').tap();await ip.waitForFunction(()=>!document.getElementById('btnGhTake').classList.contains('busy'));assert.equal(puts,oldPuts);assert.deepEqual((await snap()).cards,before.cards);
  await ip.locator('#stepsInp').fill(label+' local step');await ip.locator('#stepsInp').press('Enter');await ip.locator('#btnGhSave').tap();await ip.waitForFunction(()=>!__test.config().dirty);
  assert(await a.evaluate(()=>__test.pull(false)));assert(await a.evaluate(t=>__test.state().steps.some(x=>x.t===t),label+' local step'));
  const check=ip.locator('#mgProjs .tcheck input').first(),was=await check.isChecked();await check.tap();assert.equal(await check.isChecked(),!was);
  await ip.locator('#btnGhSave').tap();await ip.waitForFunction(()=>!__test.config().dirty);assert(await a.evaluate(()=>__test.pull(false)));
  await ip.locator('#megaOut').tap();await ip.waitForFunction(()=>!document.body.classList.contains('megaon'));await ip.waitForTimeout(1200);
  assert.equal(await ip.locator('#hero #totalBox #stepsBox').count(),1);assert.equal(await ip.locator('#hero #saveCol').count(),1);assert.equal(await ip.locator('.megaitem').count(),0);
  assert.equal(await ip.evaluate(()=>{var ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return ids.length-new Set(ids).size;}),0);
  await ip.locator('#btnMega').tap();await ip.waitForFunction(()=>document.body.classList.contains('megaon'));await ip.waitForTimeout(1800);assert.equal((await snap()).width,width);
  console.log('PASS WebKit '+label+': no-change Take, reverse Save, stage checkbox, clean exit and re-entry; no duplicate cards');
  await ip.context().close();
 }
`;
code=code.replace(anchor,extra+'\n'+anchor);
fs.writeFileSync('tools/mega-take/test.cjs',code);
