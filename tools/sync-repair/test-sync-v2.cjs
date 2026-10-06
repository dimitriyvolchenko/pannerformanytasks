'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const code=fs.readFileSync(__dirname+'/sync-v2.js','utf8');
const clone=v=>JSON.parse(JSON.stringify(v));
function fresh(){return {tasks:[],steps:[],done:{},edits:{},theme:'light',plDay:'2026-10-06',plWeek:'2026-10-05'};}
function plan(){const s=fresh();return {...s,format:'mr_rocket_planner',version:12,savedAt:'2026-10-06T08:00:00.000Z',prefs:{theme:'light'},spaces:{active:'main',list:[{id:'main',name:'MR'}],states:{main:s},seeded:{},trash:[]}};}
function response(status,data){return {status,ok:status>=200&&status<300,text:async()=>JSON.stringify(data)};}
function server(initial){
  return {raw:initial?clone(initial):null,n:initial?1:0,puts:0,conflicts:0,fail:null,beforePut:null,history:[],
    async fetch(url,opts){
      if(this.fail)throw this.fail;
      if(url.includes('/commits?'))return response(200,this.history.map((x,i)=>({sha:'old'+i})));
      if(opts.method==='PUT'){
        this.puts++;if(this.beforePut){let cb=this.beforePut;this.beforePut=null;await cb();}
        const b=JSON.parse(opts.body);
        if(b.sha!==(this.raw?'s'+this.n:undefined)){this.conflicts++;return response(409,{});}
        this.history.unshift(clone(this.raw));this.raw=JSON.parse(Buffer.from(b.content,'base64').toString());this.n++;
        return response(200,{content:{sha:'s'+this.n}});
      }
      const ref=new URL(url).searchParams.get('ref');
      const raw=ref&&ref.startsWith('old')?this.history[+ref.slice(3)]:this.raw;
      return raw?response(200,{sha:'s'+this.n,encoding:'base64',content:Buffer.from(JSON.stringify(raw)).toString('base64')}):response(404,{});
    }
  };
}
function client(s,options={}){
  const config={repo:'owner/planner',path:'progress.json',branch:'main',token:'TEST_ONLY',auto:false,dirty:false,
    stamp:'',device:'Computer',lead:false,remoteLead:'iPhone',...options};
  const store=new Map(),elements=new Map();let timerId=0;
  const element=()=>({textContent:'',innerHTML:'',style:{},classList:{add(){},remove(){},toggle(){},contains(){return false;}}});
  const c={raw:plan(),messages:[],config,localStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v)},
    KEY:'planner',GHKEY:'planner:gh',PKEY:'planner:prefs',PREF_KEYS:['theme'],storageOk:true,memPrefs:{theme:'light'},
    spaces:{active:'main',list:[{id:'main',name:'MR'}]},freshState:fresh,
    ghConf:()=>config,ghSave(){},ghReady:()=>!!config.token,guessDevice:()=>config.device,
    progressText(){return JSON.stringify(c.raw);},
    loadProgressText(t){c.raw=JSON.parse(t);c.spaces=c.raw.spaces;return true;},
    b64enc:t=>Buffer.from(t).toString('base64'),b64dec:t=>Buffer.from(t,'base64').toString('utf8'),
    syState:(m,bad)=>c.messages.push({m,bad}),syRefresh(){},syPaint(){},paintSyncDot(){},syReport(){},toast(){},
    hhmm:()=> '12:00',defaultSaveName:()=> 'backup.json',downloadProgress(){},confirm:()=>false,
    document:{hidden:false,activeElement:null,getElementById(k){if(!elements.has(k))elements.set(k,element());return elements.get(k);}},
    setTimeout:()=>++timerId,clearTimeout(){},Date,console,AbortController,
    fetch:(u,o)=>s.fetch(u,o)};
  vm.createContext(c);vm.runInContext(code,c);c.ghStart(false);
  c.edit=fn=>{fn(c.raw.spaces.states.main);Object.assign(c.raw,c.raw.spaces.states.main);c.ghTouched();};
  c.base=()=>c.ghStoreBase({raw:s.raw,core:c.ghCore(s.raw),sha:'s'+s.n},c.ghTarget());
  return c;
}
const cases=[];function test(name,fn){cases.push([name,fn]);}
function plain(v){return JSON.parse(JSON.stringify(v));}
test('Independent checkmarks merge',()=>{const c=client(server(plan()));assert.deepEqual(plain(c.ghMerge({}, {a:true}, {b:true})),{a:true,b:true});});
test('Independent task additions merge',()=>{const c=client(server(plan()));const x=c.ghMerge([],[{id:'a',t:'computer'}],[{id:'b',t:'phone'}]);assert.equal(x.length,2);});
test('Deletion does not resurrect an unchanged task',()=>{const c=client(server(plan()));const a=[{id:'a',t:'old'}];assert.deepEqual(plain(c.ghMerge(a,[],a)),[]);});
test('Delete-versus-edit conflict is not silently resolved',()=>{const c=client(server(plan()));assert.throws(()=>c.ghMerge([{id:'a',t:'old'}],[],[{id:'a',t:'changed'}]),e=>e.syncConflict);});
test('Same-field competing changes are reported',()=>{const c=client(server(plan()));assert.throws(()=>c.ghMerge({text:'a'},{text:'b'},{text:'c'}),e=>e.syncConflict);});
test('Object key order does not produce a dirty marker',()=>{const c=client(server(plan()));assert(c.ghEqual({a:1,b:2},{b:2,a:1}));});
test('No-op save sends no PUT',async()=>{const s=server(plan()),c=client(s);await c.ghPull(false);await c.ghPush(false);assert.equal(s.puts,0);assert.equal(c.config.dirty,false);});
test('Desktop manual save works even with legacy iPhone leader',async()=>{const s=server(plan()),c=client(s);await c.ghPull(false);c.config.remoteLead='iPhone';c.edit(x=>x.tasks.push({id:'pc',t:'desktop edit'}));assert(await c.ghPush(false));assert.equal(s.raw.spaces.states.main.tasks[0].id,'pc');assert.equal(s.raw.lead,'');});
test('iPhone and desktop edits in different tasks survive stale snapshots',async()=>{const s=server(plan()),a=client(s),b=client(s,{device:'iPhone'});await a.ghPull(false);await b.ghPull(false);a.edit(x=>x.tasks.push({id:'pc',t:'PC'}));b.edit(x=>x.tasks.push({id:'phone',t:'Phone'}));await b.ghPush(false);assert(await a.ghPush(false));assert.equal(s.raw.spaces.states.main.tasks.length,2);await b.ghPull(false);assert.equal(b.raw.spaces.states.main.tasks.length,2);});
test('Simultaneous PUT conflict retries with latest SHA and merges',async()=>{const s=server(plan()),a=client(s),b=client(s);await a.ghPull(false);await b.ghPull(false);a.edit(x=>x.done.pc=true);b.edit(x=>x.done.phone=true);const r=await Promise.all([a.ghPush(false),b.ghPush(false)]);assert(r.every(Boolean));assert.deepEqual(s.raw.spaces.states.main.done,{pc:true,phone:true});assert(s.conflicts>=1);});
test('Edits made during an in-flight save remain pending',async()=>{const s=server(plan()),c=client(s);await c.ghPull(false);c.edit(x=>x.tasks.push({id:'first',t:'first'}));s.beforePut=()=>c.edit(x=>x.tasks.push({id:'later',t:'later'}));assert(await c.ghPush(false));assert.equal(s.raw.spaces.states.main.tasks.length,1);assert.equal(c.raw.spaces.states.main.tasks.length,2);assert.equal(c.config.dirty,true);assert(await c.ghPush(false));assert.equal(s.raw.spaces.states.main.tasks.length,2);assert.equal(c.config.dirty,false);});
test('Network failure retains local changes and dirty marker',async()=>{const s=server(plan()),c=client(s);await c.ghPull(false);c.edit(x=>x.done.pc=true);s.fail=new Error('Failed to fetch');assert.equal(await c.ghPush(false),false);assert.equal(c.config.dirty,true);assert.equal(c.raw.spaces.states.main.done.pc,true);});
test('401 is visible and never clears unsent work',async()=>{const s=server(plan()),c=client(s);await c.ghPull(false);c.edit(x=>x.done.pc=true);s.fetch=async()=>response(401,{});assert.equal(await c.ghPush(false),false);assert(c.messages.some(x=>x.m.includes('invalid or expired')));assert(c.config.dirty);});
test('Blank first-time remote can be created explicitly',async()=>{const s=server(null),c=client(s,{dirty:true});assert(await c.ghPush(false));assert(s.raw);});
test('Known legacy stamp establishes baseline without overwriting the phone',async()=>{const s=server(plan()),c=client(s,{dirty:true,stamp:s.raw.savedAt});c.edit(x=>x.done.pc=true);assert(await c.ghPush(false));assert(s.raw.spaces.states.main.done.pc);});
test('Unknown legacy baseline blocks destructive replacement',async()=>{const s=server(plan()),c=client(s,{dirty:true});c.edit(x=>x.done.pc=true);assert.equal(await c.ghPush(false),false);assert.equal(s.puts,0);assert(c.config.dirty);assert(c.localStorage.getItem(c.GHKEY+':recovery-v2'));});
test('Legacy baseline recovered from history',async()=>{const old=plan(),s=server(old);s.raw=clone(old);s.raw.savedAt='2026-10-06T09:00:00.000Z';s.raw.spaces.states.main.done.phone=true;s.history=[old];const c=client(s,{dirty:true,stamp:old.savedAt});c.edit(x=>x.done.pc=true);assert(await c.ghPush(false));assert.deepEqual(s.raw.spaces.states.main.done,{pc:true,phone:true});});
test('Same-field conflict does not overwrite either device',async()=>{const p=plan();p.spaces.states.main.edits.title='original';const s=server(p),a=client(s),b=client(s);await a.ghPull(false);await b.ghPull(false);a.edit(x=>x.edits.title='PC');b.edit(x=>x.edits.title='Phone');await b.ghPush(false);assert.equal(await a.ghPush(false),false);assert.equal(s.raw.spaces.states.main.edits.title,'Phone');assert.equal(a.raw.spaces.states.main.edits.title,'PC');});
test('Settings sync instead of being overwritten by stale local preferences',async()=>{const s=server(plan()),c=client(s);await c.ghPull(false);s.raw.prefs.theme='dark';s.raw.theme='dark';s.n++;assert(await c.ghPull(false));assert.equal(c.raw.prefs.theme,'dark');});
test('Foreground automatic read skips active text editing',async()=>{const s=server(plan()),c=client(s,{auto:true});await c.ghPull(false);c.document.activeElement={matches:()=>true};assert.equal(await c.ghPull(true),false);});
test('Repeated persist without a content change does not dirty the plan',async()=>{const s=server(plan()),c=client(s);await c.ghPull(false);c.ghTouched();c.ghTouched();assert.equal(c.config.dirty,false);});
test('Steps inside Completed are retained in payloads',async()=>{const s=server(plan()),c=client(s);await c.ghPull(false);c.edit(x=>x.steps.push({id:'sp1',t:'next step',done:false}));await c.ghPush(false);assert.equal(s.raw.spaces.states.main.steps[0].t,'next step');});
(async()=>{let passed=0;for(const [name,fn] of cases){try{await fn();console.log('PASS '+name);passed++;}catch(e){console.error('FAIL '+name+'\n'+e.stack);process.exitCode=1;}}console.log(`${passed}/${cases.length} tests passed`);})();
