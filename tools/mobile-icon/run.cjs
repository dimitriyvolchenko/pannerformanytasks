'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
let source=fs.readFileSync('native.cjs','utf8');
function once(old,next){assert.equal(source.split(old).length-1,1,old);source=source.replace(old,next);}
// Direct test-fixture state changes must refresh the DOM, just as the real
// Highlight button does. Otherwise Mega Focus has no highlighted DOM cards.
once('__test.state().spot={tasks:true,done:true,today:true,par:true,off:true};__test.persist();',
     '__test.state().spot={tasks:true,done:true,today:true,par:true,off:true};__test.persist();__test.refresh();');
once("await b.locator('[data-logo=\"sweep-blue\"]').tap();await b.locator('#icoClose').tap();",
`await b.locator('[data-logo="check-blue"]').tap();
 assert.equal(await b.evaluate(()=>__test.state().logo),'check-blue');
 assert((await b.locator('link[rel="apple-touch-icon"]').getAttribute('href')).endsWith('planner-check-180.png'));
 assert.equal(await b.locator('[data-logo="check-blue"]').getAttribute('aria-pressed'),'true');
 await b.locator('[data-logo="sweep-blue"]').tap();await b.locator('#icoClose').tap();`);
once(' // Test compact sizing across ordinary, narrow and landscape phone viewports.',
` // Verify the restored acknowledgement path with a real open WebKit editor.
 assert(await a.evaluate(()=>__test.push(false)));assert(await b.evaluate(()=>__test.pull(false)));
 remote=JSON.parse(JSON.stringify(remote));
 remote.spaces.states[remote.spaces.active].steps.push({id:'spCIREMOTE',t:'REMOTE DURING EDIT',done:false});sha++;
 await b.evaluate(()=>{__test.state().tasks[0].t='EDIT SENT';__test.persist();__test.refresh();});
 let release;holdPut=new Promise(r=>release=r);const arrived=new Promise(r=>putArrived=r);
 await b.locator('#btnGhSave').dispatchEvent('click');await arrived;putArrived=null;
 const onceCount=puts;await b.locator('#btnGhSave').dispatchEvent('click');
 await b.waitForTimeout(120);assert.equal(puts,onceCount,'Repeated Save duplicated a pending PUT');
 await b.locator('#tasksList [data-tdtext]').first().dblclick();
 await b.locator('#tasksList input').fill('EDIT DURING SAVE');release();holdPut=null;
 await b.waitForFunction(()=>!document.getElementById('btnGhSave').classList.contains('busy'));
 assert.equal(await b.locator('#tasksList input').inputValue(),'EDIT DURING SAVE');
 assert((await b.evaluate(()=>__test.status())).includes('Saved to GitHub'));
 assert(remote.spaces.states[remote.spaces.active].tasks.some(x=>x.t==='EDIT SENT'));
 await b.locator('#btnGhSave').dispatchEvent('click');
 await b.waitForFunction(()=>!document.getElementById('btnGhSave').classList.contains('busy'));
 assert(remote.spaces.states[remote.spaces.active].tasks.some(x=>x.t==='EDIT DURING SAVE'));
 assert(remote.spaces.states[remote.spaces.active].steps.some(x=>x.id==='spCIREMOTE'));
 assert(await a.evaluate(()=>__test.pull(false)));
 pass('In-flight Save acknowledgement preserves later editor text and remote additions; duplicate Save is deduplicated');
 // Test compact sizing across ordinary, narrow and landscape phone viewports.`);
fs.writeFileSync('native-expanded.cjs',source);
require(path.resolve('native-expanded.cjs'));
