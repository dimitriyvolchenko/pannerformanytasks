/* Sync v2: all devices are peers. Compare with an acknowledged baseline;
   never silently replace another device's work with an older whole-plan copy. */
var ghV2={started:false, applying:false, flight:null, observed:null, base:null,
          target:"", blockedUntil:0, conflict:null};
var ghTimer=null;
function ghCopy(v){ return v===undefined?undefined:JSON.parse(JSON.stringify(v)); }
function ghStable(v){
  if(v===undefined) return "undefined";
  if(Array.isArray(v)) return "["+v.map(ghStable).join(",")+"]";
  if(v && typeof v==="object") return "{"+Object.keys(v).sort().map(function(k){
    return JSON.stringify(k)+":"+ghStable(v[k]);
  }).join(",")+"}";
  return JSON.stringify(v);
}
function ghEqual(a,b){ return ghStable(a)===ghStable(b); }
function ghObject(v){ return !!v && typeof v==="object" && !Array.isArray(v); }
function ghSafeKey(k){ return k!=="__proto__" && k!=="constructor" && k!=="prototype"; }
function ghConflictError(path){
  var e=new Error("Both devices changed the same part of the plan. Neither copy was overwritten.");
  e.syncConflict=true; e.path=path||"plan"; return e;
}
/* Three-way merge. Checkmarks/maps merge per key; task arrays merge by stable id.
   Competing edits/deletions or incompatible reordering require a human choice. */
function ghMerge(base,local,remote,path){
  path=path||"plan";
  if(ghEqual(local,remote)) return ghCopy(local);
  if(ghEqual(local,base)) return ghCopy(remote);
  if(ghEqual(remote,base)) return ghCopy(local);
  if(ghObject(local) && ghObject(remote) && (ghObject(base)||base===undefined)){
    var b=base||{}, out={};
    Array.from(new Set(Object.keys(b).concat(Object.keys(local),Object.keys(remote)))).forEach(function(k){
      if(!ghSafeKey(k)) throw ghConflictError(path);
      var v=ghMerge(b[k],local[k],remote[k],path+"."+k);
      if(v!==undefined) out[k]=v;
    });
    return out;
  }
  if(Array.isArray(local) && Array.isArray(remote) && (Array.isArray(base)||base===undefined)){
    var bs=base||[];
    function keyed(a){ var ids=new Set(); return a.every(function(x){
      if(!ghObject(x)||typeof x.id!=="string"||ids.has(x.id)) return false;
      ids.add(x.id); return true;
    }); }
    if(keyed(bs)&&keyed(local)&&keyed(remote)){
      var bm=new Map(bs.map(function(x){return [x.id,x];}));
      var lm=new Map(local.map(function(x){return [x.id,x];}));
      var rm=new Map(remote.map(function(x){return [x.id,x];}));
      var merged=new Map();
      Array.from(new Set(bs.concat(local,remote).map(function(x){return x.id;}))).forEach(function(id){
        var v=ghMerge(bm.get(id),lm.get(id),rm.get(id),path+"["+id+"]");
        if(v!==undefined) merged.set(id,v);
      });
      var common=bs.map(function(x){return x.id;}).filter(function(id){return lm.has(id)&&rm.has(id)&&merged.has(id);});
      function order(a){return a.map(function(x){return x.id;}).filter(function(id){return common.indexOf(id)>=0;});}
      var lo=order(local),ro=order(remote),lc=!ghEqual(lo,common),rc=!ghEqual(ro,common);
      if(lc&&rc&&!ghEqual(lo,ro)) throw ghConflictError(path+".order");
      var primary=lc?local:remote, secondary=lc?remote:local;
      var ids=primary.map(function(x){return x.id;}).filter(function(id){return merged.has(id);});
      secondary.forEach(function(x,i){
        if(!merged.has(x.id)||ids.indexOf(x.id)>=0) return;
        var before=-1;
        for(var j=i-1;j>=0;j--){before=ids.indexOf(secondary[j].id);if(before>=0)break;}
        if(before>=0) ids.splice(before+1,0,x.id); else ids.unshift(x.id);
      });
      return ids.map(function(id){return merged.get(id);});
    }
  }
  throw ghConflictError(path);
}
function ghCore(o){
  if(!o||o.format!=="mr_rocket_planner") throw new Error("That file is not a planner progress file");
  var sp=o.spaces, list, raw;
  if(sp && Array.isArray(sp.list) && sp.list.length && ghObject(sp.states)){
    list=ghCopy(sp.list); raw=sp.states;
  } else {
    list=[{id:"main",name:"MR"}]; raw={main:o};
  }
  var ids=new Set(), states={}, prefs={};
  list.forEach(function(item){
    if(!item||typeof item.id!=="string"||!ghSafeKey(item.id)||ids.has(item.id)||!ghObject(raw[item.id]))
      throw new Error("The progress file has an invalid project list; nothing was replaced");
    ids.add(item.id);
    var st=freshState();
    var keys=sp?Object.keys(raw[item.id]):Object.keys(st);
    keys.forEach(function(k){
      if(!ghSafeKey(k))throw new Error("Unsafe key in progress file");
      if(raw[item.id][k]!==undefined)st[k]=ghCopy(raw[item.id][k]);
    });
    PREF_KEYS.forEach(function(k){delete st[k];});
    states[item.id]=st;
  });
  PREF_KEYS.forEach(function(k){
    var v=o.prefs && o.prefs[k]!==undefined?o.prefs[k]:o[k];
    if(v!==undefined)prefs[k]=ghCopy(v);
  });
  return {list:list,states:states,prefs:prefs,seeded:ghCopy(sp&&sp.seeded||{}),trash:ghCopy(sp&&sp.trash||[])};
}
function ghSnapshot(){return ghCore(JSON.parse(progressText()));}
function ghPayload(model){
  var active=spaces.active;
  if(!model.states[active]) active=model.list[0].id;
  var all={active:active,list:ghCopy(model.list),states:{},seeded:ghCopy(model.seeded),trash:ghCopy(model.trash)};
  model.list.forEach(function(sp){all.states[sp.id]=Object.assign({},ghCopy(model.states[sp.id]),ghCopy(model.prefs));});
  var out=Object.assign({},all.states[active]);
  out.format="mr_rocket_planner";out.version=12;out.syncVersion=2;out.savedAt=new Date().toISOString();
  out.spaces=all;out.prefs=ghCopy(model.prefs);out.device=ghConf().device||guessDevice();out.lead="";
  return out;
}
function ghTarget(){
  var c=ghConf();
  return {repo:c.repo,path:c.path,branch:c.branch||"main",token:c.token};
}
function ghTargetId(t){return [t.repo,t.branch,t.path].join("\n");}
function ghEndpoint(t){
  return "https://api.github.com/repos/"+t.repo.replace(/^\/+|\/+$/g,"")+"/contents/"+
    t.path.replace(/^\/+/,"").split("/").map(encodeURIComponent).join("/");
}
function ghRequest(url,opts,t){
  var ctl=typeof AbortController!=="undefined"?new AbortController():null;
  var timer=ctl?setTimeout(function(){ctl.abort();},25000):null;
  var headers={Authorization:"Bearer "+t.token,Accept:"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"};
  if(opts&&opts.method)headers["Content-Type"]="application/json";
  return fetch(url,Object.assign({headers:headers,cache:"no-store",signal:ctl?ctl.signal:undefined},opts||{}))
    .then(function(r){
      return r.text().then(function(text){
        var data=null;try{data=JSON.parse(text);}catch(e){}
        if(!r.ok){var err=new Error(String(r.status));err.status=r.status;throw err;}
        return data;
      });
    }).finally(function(){if(timer)clearTimeout(timer);});
}
function ghFetchRemote(target){
  var t=target||ghTarget();
  return ghRequest(ghEndpoint(t)+"?ref="+encodeURIComponent(t.branch)+"&t="+Date.now(),null,t)
    .catch(function(e){if(e.status===404)return null;throw e;});
}
function ghReadRemote(cur){
  if(!cur)return null;
  if(cur.encoding && cur.encoding!=="base64") throw new Error("The progress file is too large for this sync route; the local plan is safe");
  var raw=JSON.parse(b64dec(cur.content||""));
  return {raw:raw,core:ghCore(raw),sha:cur.sha};
}
function ghStoreBase(remote,t){
  ghV2.base={target:ghTargetId(t),sha:remote.sha,stamp:remote.raw.savedAt||"",core:ghCopy(remote.core)};
  try{localStorage.setItem(GHKEY+":baseline-v2",JSON.stringify(ghV2.base));}catch(e){}
  var c=ghConf();c.stamp=remote.raw.savedAt||"";c.at=Date.now();c.remoteAt=c.stamp;
  c.remoteDevice=remote.raw.device||"";c.remoteLead="";c.lead=false;ghSave();
}
function ghLoadBase(t){
  var id=ghTargetId(t);
  if(ghV2.target!==id){
    ghV2.target=id;ghV2.base=null;ghV2.conflict=null;
    try{var b=JSON.parse(localStorage.getItem(GHKEY+":baseline-v2")||"null");
      if(b&&b.target===id&&b.core)ghV2.base=b;
    }catch(e){}
  }
  return ghV2.base;
}
/* Upgrade old installations without guessing which copy wins. The old app kept
   savedAt but not a baseline. Recover the matching acknowledged copy from history. */
function ghLegacyBase(remote,t){
  var b=ghLoadBase(t),stamp=ghConf().stamp;
  if(b)return Promise.resolve(b.core);
  if(remote&&stamp&&remote.raw.savedAt===stamp)return Promise.resolve(remote.core);
  if(!stamp||!isFinite(Date.parse(stamp)))return Promise.resolve(null);
  var url="https://api.github.com/repos/"+t.repo+"/commits?path="+encodeURIComponent(t.path)+
    "&sha="+encodeURIComponent(t.branch)+"&per_page=5&until="+encodeURIComponent(new Date(Date.parse(stamp)+180000).toISOString());
  return ghRequest(url,null,t).then(function(commits){
    var candidates=Array.isArray(commits)?commits.slice(0,5):[];
    function next(i){
      if(i>=candidates.length)return Promise.resolve(null);
      return ghRequest(ghEndpoint(t)+"?ref="+encodeURIComponent(candidates[i].sha),null,t).then(function(file){
        var old=ghReadRemote(file);
        return old&&old.raw.savedAt===stamp?old.core:next(i+1);
      });
    }
    return next(0);
  }).catch(function(){return null;});
}
function ghBackup(reason,remote){
  try{
    var entry={savedAt:new Date().toISOString(),reason:reason,local:JSON.parse(progressText()),remote:remote?remote.raw:null};
    localStorage.setItem(GHKEY+":recovery-v2",JSON.stringify(entry));
    if(remote)localStorage.setItem(GHKEY+":conflict-backup-v2",JSON.stringify(entry));
    return true;
  }catch(e){return false;}
}
function ghInstall(model){
  var before=ghSnapshot();
  if(ghEqual(before,model))return true;
  if(!ghBackup("before-sync-apply",null))throw new Error("The browser cannot keep a recovery copy. Export your plan before loading another copy");
  var payload=ghPayload(model);
  ghV2.applying=true;
  try{
    memPrefs=ghCopy(model.prefs);
    if(storageOk)localStorage.setItem(PKEY,JSON.stringify(memPrefs));
    spaces.seeded=ghCopy(model.seeded);spaces.trash=ghCopy(model.trash);
    if(!loadProgressText(JSON.stringify(payload)))throw new Error("Could not apply the synced plan; a recovery copy is kept in this browser");
    return true;
  } finally {ghV2.applying=false;ghV2.observed=ghSnapshot();}
}
function ghDirty(){
  var now=ghSnapshot(),b=ghLoadBase(ghTarget()),c=ghConf();
  if(b)c.dirty=!ghEqual(now,b.core);
  ghV2.observed=now;ghSave();paintSyncDot();return !!c.dirty;
}
function ghAcknowledge(remote,t,sentLocal){
  var latest=ghSnapshot(),next=ghMerge(sentLocal,latest,remote.core);
  ghStoreBase(remote,t);ghInstall(next);ghDirty();
  ghV2.conflict=null;ghV2.blockedUntil=0;syRefresh();
}
function ghErr(e){
  if(e&&e.syncConflict)return e.message;
  var status=e&&e.status,m=e&&e.message||String(e);
  if(status===401||m.indexOf("401")===0)return "This device's GitHub key is invalid or expired. Update it in Sync; the local plan is safe";
  if(status===403||m.indexOf("403")===0)return "GitHub refused this device's request (permissions or rate limit). Check its key: this repository, Contents: Read and write";
  if(status===404||m.indexOf("404")===0)return "Repository, branch or access is unavailable. Check Sync settings on this device";
  if(status===409||status===422)return "The remote copy changed during saving. Your changes remain here; try Sync again";
  if(e&&e.name==="AbortError")return "GitHub did not answer in time. Changes remain in this browser and will retry when connected";
  if(/Failed to fetch|NetworkError|Load failed/.test(m))return "This device cannot reach GitHub. Changes remain in this browser; retry when connected";
  return m;
}
function syAfterFail(){
  syPaint();var el=document.getElementById("syOverlay");if(el)el.classList.add("show");
}
function ghShowConflict(remote,quiet){
  ghV2.conflict=remote;ghConf().dirty=true;ghSave();ghBackup("sync-conflict",remote);
  var msg="Two different copies need a choice. Your local changes have NOT been discarded.";
  syState(msg,true);
  syReport('<div class="fix">'+msg+' Save a backup before replacing either copy.</div>'+ 
    '<div class="sybuttons"><button class="btn" id="syBackupV2">Download this device backup</button>'+ 
    '<button class="btn" id="syKeepV2">Use this device copy</button>'+ 
    '<button class="btn" id="syRemoteV2">Use GitHub copy</button></div>',"");
  document.getElementById("syBackupV2").onclick=function(){downloadProgress(progressText(),defaultSaveName());};
  document.getElementById("syKeepV2").onclick=function(){
    if(confirm("Replace the GitHub plan with this device's entire copy? Changes present only in GitHub will be replaced. Both copies will first be kept in this browser's recovery backup."))ghRun("force-send",false);
  };
  document.getElementById("syRemoteV2").onclick=function(){
    if(confirm("Replace this device's plan with the GitHub copy? This device's unsent changes will first be kept in a recovery backup."))ghRun("force-take",false);
  };
  if(!quiet)syAfterFail();paintSyncDot();
}
function ghReconcile(local,remote,base){
  if(ghEqual(local,remote))return ghCopy(local);
  if(!base)throw ghConflictError("unknown legacy baseline");
  return ghMerge(base,local,remote);
}
function ghDoSync(kind,quiet,t){
  var retries=0,force=kind==="force-send"||kind==="force-take";
  function attempt(){
    return ghFetchRemote(t).then(function(file){
      var remote=ghReadRemote(file);
      return ghLegacyBase(remote,t).then(function(base){
        if(ghTargetId(ghTarget())!==ghTargetId(t))throw new Error("Sync settings changed while the request was running; retry with the current settings");
        var local=ghSnapshot(),c=ghConf(),dirty=base?!ghEqual(local,base):!!c.dirty;
        var merged;
        try{
          if(force){
            if(!ghV2.conflict||!remote||remote.sha!==ghV2.conflict.sha)throw ghConflictError("remote changed again");
            if(!ghBackup("explicit-conflict-resolution",remote))throw new Error("Cannot keep a recovery backup; export the plan before replacing a copy");
            merged=kind==="force-take"?remote.core:local;
          } else if(!remote){
            if(base)throw ghConflictError("remote file removed");
            if(kind==="take"){syState("No progress file exists yet. Use Save to GitHub to create it.",true);return false;}
            merged=local;
          } else if(!dirty){merged=remote.core;}
          else {merged=ghReconcile(local,remote.core,base);}
        }catch(e){if(e.syncConflict){ghShowConflict(remote,quiet);return false;}throw e;}
        var mustWrite=kind==="send"||kind==="force-send";
        if(!mustWrite||remote&&ghEqual(merged,remote.core)){
          if(remote){
            ghStoreBase(remote,t);ghInstall(merged);ghDirty();ghV2.conflict=null;
            syState(c.dirty?"New changes combined locally; not yet sent to GitHub":"Up to date - changes from all devices are available");
          }
          return true;
        }
        var payload=ghPayload(merged),body={message:"planner progress "+payload.savedAt.slice(0,16).replace("T"," "),
          content:b64enc(JSON.stringify(payload,null,2)),branch:t.branch};
        if(remote)body.sha=remote.sha;
        return ghRequest(ghEndpoint(t),{method:"PUT",body:JSON.stringify(body)},t).then(function(result){
          if(!result||!result.content||!result.content.sha)throw new Error("GitHub returned no confirmation; your unsent marker was kept");
          var ack={raw:payload,core:merged,sha:result.content.sha};
          try{ghAcknowledge(ack,t,local);}catch(e){
            ghStoreBase(ack,t);c.dirty=true;ghSave();
            if(e.syncConflict){ghShowConflict(ack,quiet);return false;}throw e;
          }
          syState(c.dirty?"Saved to GitHub; changes made during the save are still pending":"Saved to GitHub at "+hhmm()+" from "+(c.device||"this device"));
          if(!quiet)toast(c.dirty?"Saved; newer edits remain to send":"Progress saved to GitHub");
          return true;
        }).catch(function(e){
          if((e.status===409||e.status===422)&&!force&&retries++<2)return attempt();
          throw e;
        });
      });
    });
  }
  return attempt();
}
function ghEditing(){
  var el=document.activeElement;
  return !!(el&&el.matches&&el.matches('input,textarea,[contenteditable="true"]'));
}
function ghSchedule(){
  clearTimeout(ghTimer);
  if(!ghV2||!ghV2.started||!ghReady()||!ghConf().auto||!ghConf().dirty||ghV2.conflict)return;
  ghTimer=setTimeout(function(){ghPush(true);},Math.max(4000,ghV2.blockedUntil-Date.now()));
}
function ghRun(kind,quiet){
  if(!ghReady()){syState("Set up Sync on this device: repository and a key with Contents: Read and write",true);if(!quiet)syAfterFail();return Promise.resolve(false);}
  if(!ghV2.started)ghStart(false);
  if(quiet&&(document.hidden||ghEditing()||ghV2.conflict||Date.now()<ghV2.blockedUntil))return Promise.resolve(false);
  if(ghV2.flight){
    if(quiet)return Promise.resolve(false);
    return ghV2.flight.then(function(){return ghRun(kind,false);});
  }
  clearTimeout(ghTimer);ghLoadBase(ghTarget());
  if(!quiet)syState(kind.indexOf("take")>=0?"Checking the GitHub copy...":"Saving to GitHub...");
  var target=ghTarget();
  var job=ghDoSync(kind,quiet,target).catch(function(e){
    ghV2.blockedUntil=Date.now()+30000;
    syState("Not synced: "+ghErr(e),true);
    if(!quiet){syAfterFail();toast("Not saved to GitHub - see Sync. Local changes are kept.");}
    return false;
  }).finally(function(){
    if(ghV2.flight===job)ghV2.flight=null;
    paintSyncDot();ghSchedule();
  });
  ghV2.flight=job;return job;
}
function ghPush(quiet){return ghRun("send",!!quiet);}
function ghPull(quiet){return ghRun("take",!!quiet);}
function ghApply(text){
  try{ghInstall(ghCore(JSON.parse(text)));return true;}catch(e){syState(ghErr(e),true);return false;}
}
function ghTouched(){
  if(!ghV2||!ghV2.started||ghV2.applying)return;
  var now=ghSnapshot();
  if(ghEqual(now,ghV2.observed))return;
  ghV2.observed=now;
  var b=ghLoadBase(ghTarget()),c=ghConf();
  c.dirty=b?!ghEqual(now,b.core):true;
  ghSave();paintSyncDot();ghSchedule();
}
function ghCycle(){
  if(!ghReady()||!ghConf().auto||document.hidden||ghEditing())return;
  if(ghConf().dirty)ghPush(true);else ghPull(true);
}
function ghStart(run){
  if(ghV2.started)return;
  ghV2.started=true;ghLoadBase(ghTarget());ghV2.observed=ghSnapshot();
  if(ghV2.base)ghDirty();
  ghConf().lead=false;ghConf().remoteLead="";ghSave();paintSyncDot();
  if(run!==false)ghCycle();
}

function ghRecovery(){
  var raw=localStorage.getItem(GHKEY+":conflict-backup-v2")||localStorage.getItem(GHKEY+":recovery-v2");
  var entry=null;try{entry=JSON.parse(raw||"null");}catch(e){}
  if(!entry){syState("No recovery copies have been needed on this device yet");return;}
  syReport('<div class="fix">Recovery copies kept on this device before a sync replacement.</div>'+ 
    '<button class="btn" id="syRecoveryLocalV2">Download local recovery copy</button>'+ 
    (entry.remote?'<button class="btn" id="syRecoveryRemoteV2">Download GitHub recovery copy</button>':''),"");
  document.getElementById("syRecoveryLocalV2").onclick=function(){downloadProgress(JSON.stringify(entry.local,null,2),"planner-local-recovery.json");};
  if(entry.remote)document.getElementById("syRecoveryRemoteV2").onclick=function(){downloadProgress(JSON.stringify(entry.remote,null,2),"planner-remote-recovery.json");};
}
