--- a/index.html
+++ b/index.html
@@ -7,6 +7,7 @@
 <meta name="apple-mobile-web-app-status-bar-style" content="default">
 <meta name="apple-mobile-web-app-title" content="Mission">
 <title>MR Mission Planner</title>
+<link rel="manifest" href="manifest.webmanifest">
 <link rel="apple-touch-icon" sizes="180x180" type="image/png" href="assets/icons/planner-sweep-180.png">
 <link rel="icon" sizes="192x192" type="image/png" href="assets/icons/planner-sweep-192.png">
 <link rel="icon" sizes="32x32" type="image/png" href="assets/icons/planner-sweep-32.png">
@@ -17,6 +18,20 @@
 #megaSyncStatus{display:block;max-width:44vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10px;font-weight:500;line-height:1.5;letter-spacing:0;text-transform:none;color:var(--ink-dim)}
 #megaSyncStatus[data-bad="true"]{color:var(--redp)}
 </style>
+
+<style id="planner-20261008-2">
+.planner-badge-toggle{display:inline-flex;align-items:center;gap:4px;flex:0 0 auto;border:1px solid var(--line2);border-radius:999px;background:rgba(255,255,255,.65);color:var(--ink-dim);padding:4px 7px;font:600 10px/1.2 system-ui;cursor:pointer;white-space:nowrap;min-height:27px}
+.planner-badge-toggle .badge-light{width:6px;height:6px;border-radius:50%;background:#aeb5c0}
+.planner-badge-toggle.on{background:#fff3f3;border-color:#edbcc1;color:#9d3c49}.planner-badge-toggle.on .badge-light{background:#ed4a5c}
+.planner-badge-toggle:focus-visible{outline:2px solid var(--blue);outline-offset:3px}
+.badge-number{min-width:1em;text-align:center}.planner-badge-settings{margin-top:14px;padding-top:14px;border-top:1px solid var(--line2);font-size:12px;line-height:1.5}.planner-badge-settings p{margin:7px 0;color:var(--ink-dim)}
+#btnLogo{position:relative}#plannerBadgeTotal:not(:empty){position:absolute;right:-5px;top:-7px;background:#ec3e50;color:#fff;border:2px solid var(--card);border-radius:20px;font:700 10px/17px system-ui;min-width:20px;padding:0 4px;pointer-events:none}
+#todayBox .th,#tasksBox .th{flex-wrap:wrap;gap:6px}#todayBox .th b:not(.badge-number),#tasksBox .th b:not(.badge-number){min-width:0}
+#megaOv .mgsettled{overflow-anchor:none}#megaOv{overflow-anchor:none}
+@media(min-width:1401px){#hero .badge-word{display:none}#hero .planner-badge-toggle{padding:4px 5px}#hero #todayBox .th,#hero #tasksBox .th{gap:4px}}
+@media(pointer:coarse){.planner-badge-toggle{min-height:34px;padding:6px 8px}}
+</style>
+
 </head>
 <body class="scattered">
 <style>
@@ -3117,6 +3132,7 @@
   </div>
 </div>
 
+<form id="plannerSyncCredentials" autocomplete="off" method="post" onsubmit="return false"></form>
 <div class="overlay" id="syOverlay">
   <div class="modal narrow">
     <header><h2>Sync through your GitHub</h2><span class="spacer"></span><span class="sydot" id="syDot"></span></header>
@@ -3124,19 +3140,19 @@
       <p class="thp">The planner keeps one progress file in a repository of yours and reads it back on every device.
         Fill this in once here, once on the phone - and both open the same plan.</p>
       <div class="syrow"><label>Repository</label>
-        <input type="text" id="syRepo" placeholder="your-name/planner-data" spellcheck="false"></div>
+        <input type="text" id="syRepo" value="dimitriyvolchenko/pannerformanytasks" placeholder="dimitriyvolchenko/pannerformanytasks" spellcheck="false" form="plannerSyncCredentials" name="planner-sync-syRepo" autocomplete="off"></div>
       <div class="syrow"><label>File</label>
-        <input type="text" id="syPath" placeholder="progress.json" spellcheck="false"></div>
+        <input type="text" id="syPath" placeholder="progress.json" spellcheck="false" form="plannerSyncCredentials" name="planner-sync-syPath" autocomplete="off"></div>
       <div class="syrow"><label>Branch</label>
-        <input type="text" id="syBranch" placeholder="main" spellcheck="false"></div>
+        <input type="text" id="syBranch" placeholder="main" spellcheck="false" form="plannerSyncCredentials" name="planner-sync-syBranch" autocomplete="off"></div>
       <div class="syrow keyrow"><label>Access key</label>
-        <input type="password" id="syToken" placeholder="github_pat_..." spellcheck="false" autocomplete="off">
+        <input type="password" id="syToken" placeholder="github_pat_..." spellcheck="false" form="plannerSyncCredentials" name="planner-sync-syToken" autocomplete="new-password">
         <div class="sykeyrow">
           <button class="btn" id="syPaste" title="Take the key from the clipboard and put it in the field">paste the key</button>
           <button class="btn" id="syShow" title="Show what is in the field">show</button>
         </div></div>
       <div class="syrow"><label>This device</label>
-        <input type="text" id="syDevice" placeholder="iPhone" spellcheck="false"></div>
+        <input type="text" id="syDevice" placeholder="iPhone" spellcheck="false" form="plannerSyncCredentials" name="planner-sync-syDevice" autocomplete="off"></div>
       <div class="sylead" id="syLeadBox"></div>
       <p class="thp syhint">A page put on the home screen keeps its own store, separate from the browser it was added from - that is why
         it asks for the key once more there. Copy the key, open the plan from the home screen, and press <b>paste the key</b>: it is
@@ -5614,7 +5630,8 @@
 
 /* ================= STATE ================= */
 var KEY="mr_rocket_planner_v2";
-var PLANNER_BUILD="2026.10.08.1", ZOOMKEY="", localZoom=1;
+var DEFAULT_SYNC_REPO="dimitriyvolchenko/pannerformanytasks";
+var PLANNER_BUILD="2026.10.08.2", ZOOMKEY="", localZoom=1;
 /* Compact phones start at a readable 100%. Their scale is independent of the
    old device-wide value and of tablet/desktop layouts. Pinch zoom stays enabled. */
 function zoomProfile(){
@@ -5652,13 +5669,15 @@
 }
 function tabRefresh(){
   if(!tabRepaint||tabConflict||ghEditing())return;
+  var previous=state;
   tabRepaint=false;
   var disk=readSpace(spaces.active),base=tabBases[spaces.active];
   if(disk&&base&&!ghEqual(base,disk)){
     try{state=tabProjectMerge(base,state,disk);tabBases[spaces.active]=ghCopy(disk);}
     catch(e){tabConflict={id:spaces.active,local:ghCopy(state),remote:disk,path:e.path};showTabConflict();return;}
   }
-  refreshAll();
+  if(megaOn&&!megaBusy&&megaView&&megaView.space===spaces.active)refreshMegaData(previous);else refreshAll();
+  paintPlannerBadge();ghTouched();
 }
 function showTabConflict(){
   var el=document.getElementById("plannerHealth");
@@ -5684,7 +5703,7 @@
     today:[],week:[],todayNext:[],weekNext:[],todayView:"now",weekView:"now",
     plLog:[],plDay:"",plWeek:"",spotSave:null,starts:{},launched:{},launchBox:true,
     saveName:"",saveDirName:"",ptask:{},stickBtn:null,stickBtnHidden:false,stickersHidden:false,bink:[],
-    pairs:[],pairsNext:[],parView:"now",parFace:"list",tasks:[],tasksNext:[],tasksView:"now",timeoff:[],timeoffNext:[],timeoffView:"now",steps:[],stepsNext:[],stepsView:"now",instrOpen:false,korean:false,logo:"wok",
+    pairs:[],pairsNext:[],parView:"now",parFace:"list",tasks:[],tasksNext:[],tasksView:"now",timeoff:[],timeoffNext:[],timeoffView:"now",steps:[],stepsNext:[],stepsView:"now",badgeSources:{today:true,tasks:false},instrOpen:false,korean:false,logo:"wok",
     theme:"light",pinkBar:false,pinkColor:"",heroZoom:1,heroFree:false,darkness:50,boldAll:false,inproc:{},ie:false,iedone:{},hideDone:{},hideAllT:{},flipped:{},back:{}};
 }
 var state=freshState();
@@ -5777,7 +5796,7 @@
   state=freshState();
   var pp=readSpace(id);
   if(pp && typeof pp==="object"){ Object.keys(state).forEach(function(k){ if(pp[k]!==undefined) state[k]=pp[k]; }); }
-  applyPrefs();state.heroZoom=localZoom;tabBases[id]=ghCopy(pp||{});
+  applyPrefs();state.heroZoom=localZoom;tabBases[id]=ghCopy(pp||{});cleanMisplacedStepAddresses(id);
 }
 loadStateOf(spaces.active);
 /* one-time migration: the watermark is switched off in this release */
@@ -5785,6 +5804,7 @@
 function persist(){
   writeSpace(spaces.active,state);writePrefs();
   if(typeof ghTouched==="function")ghTouched();
+  if(typeof paintPlannerBadge==="function")paintPlannerBadge();
 }
 
 /* ================= HELPERS ================= */
@@ -6122,7 +6142,7 @@
     return;
   }
   list.forEach(function(p,i){ host.appendChild(renderProject(p,i)); });
-  observeCards();
+  observeCards();setupPlannerTaskInputs();
 }
 /* a brand new stage, straight from the board */
 function addStage(){
@@ -8372,6 +8392,7 @@
     mv.classList.toggle("hidden", !ahead);
     mv.textContent=cfg.mvLab+(a.length?(" ("+a.length+")"):"");
   }
+  setupPlannerTaskInputs();
 }
 function renderToday(){ renderList(PLISTS.today); renderList(PLISTS.tasks); renderList(PLISTS.timeoff); renderList(PLISTS.steps); renderList(PLISTS.week); paintLogCount(); }
 
@@ -8611,8 +8632,9 @@
 function addTo(cfg){
   var inp=document.getElementById(cfg.inp);
   var v=inp.value.trim(); if(!v) return;
+  if(cfg.key==="steps"&&isPlannerSyncAddress(v)){inp.value="";plannerRememberDraft(inp);toast("Repository address belongs in Sync, not in Steps.");return;}
   plArr(plKey(cfg)).push({id:plId(cfg.pre), t:v, done:false});
-  inp.value=""; persist(); renderList(cfg);
+  inp.value="";plannerRememberDraft(inp);persist();renderList(cfg);
 }
 /* ---------- carrying the next list into the running one ---------- */
 function plMoveIn(cfg, quiet){
@@ -8793,7 +8815,7 @@
     }
   });
   document.getElementById(cfg.add).addEventListener("click", function(){ addTo(cfg); });
-  document.getElementById(cfg.inp).addEventListener("keydown", function(e){ if(e.key==="Enter") addTo(cfg); });
+  document.getElementById(cfg.inp).addEventListener("keydown",function(e){if(e.key==="Enter"&&!e.isComposing&&!ghComposing){e.preventDefault();addTo(cfg);}else if(e.key==="Escape"){this.value="";plannerRememberDraft(this);this.blur();}});
   /* the switch turns the box over to the next day / the next week and back */
   document.getElementById(cfg.sw).addEventListener("click", function(ev){
     ev.stopPropagation();
@@ -8988,7 +9010,8 @@
       document.body.classList.remove("mgback","mgtl","mgstk");
       document.querySelectorAll("[style*='--fd']").forEach(function(e){ e.style.removeProperty("--fd"); });
       megaOn=false;megaBusy=false;megaView=null;
-      try{ applySpot(); renderToday(); renderPairs(); renderLaunch(); render(); }catch(e){}
+      if(megaDataRefreshed){megaDataRefreshed=false;refreshAll();}
+      else {applySpot();renderToday();renderPairs();renderLaunch();render();}
       try{ fitHeroWide(); syncHeroHeight(); }catch(e){}
     }, 560);
   }, 380+megaSaved.length*70);
@@ -11424,12 +11447,13 @@
 var ghMem=null;
 function ghConf(){
   if(ghMem) return ghMem;
-  var o={repo:"",path:"progress.json",branch:"main",token:"",auto:false,stamp:"",at:0,dirty:false,
+  var o={repo:DEFAULT_SYNC_REPO,path:"progress.json",branch:"main",token:"",auto:false,stamp:"",at:0,dirty:false,
          device:"",lead:false,remoteDevice:"",remoteLead:"",remoteAt:""};
   try{
     var raw=localStorage.getItem(GHKEY);
     if(raw){ var p2=JSON.parse(raw); Object.keys(p2||{}).forEach(function(k){ o[k]=p2[k]; }); }
   }catch(e){}
+  if(!o.repo||!String(o.repo).trim())o.repo=DEFAULT_SYNC_REPO;
   if(!o.device) o.device=guessDevice();
   ghMem=o; return o;
 }
@@ -11713,7 +11737,7 @@
     memPrefs=ghCopy(model.prefs);
     if(storageOk)localStorage.setItem(PKEY,JSON.stringify(memPrefs));
     spaces.seeded=ghCopy(model.seeded);spaces.trash=ghCopy(model.trash);
-    if(!loadProgressText(JSON.stringify(payload)))throw new Error("Could not apply the synced plan; a recovery copy is kept in this browser");
+    if(!loadProgressText(JSON.stringify(payload),true))throw new Error("Could not apply the synced plan; a recovery copy is kept in this browser");
     return true;
   } finally {ghV2.applying=false;ghV2.observed=ghSnapshot();}
 }
@@ -11857,12 +11881,8 @@
 document.addEventListener("compositionend",function(){ghComposing=false;},true);
 function ghPrepareManual(){
   if(ghComposing){syState("Finish the current character before syncing. Your text is kept.",true);return false;}
-  var draft=[].slice.call(document.querySelectorAll('.tadd input,#parA,#parB,[data-addinp],[data-subinp]')).filter(function(el){return el.getClientRects().length&&String(el.value||"").trim();})[0];
-  if(draft){syState("A new task is still in its field. Press Enter to add it before syncing. Your draft is kept.",true);return false;}
+  if(!prepareAllPlannerEntries())return false;
   document.querySelectorAll("#plMenu.show,#richMenu.show,#ctxMenu.show,#lineMenu.show,#pinkMenu.show").forEach(function(el){el.classList.remove("show");});
-  var el=document.activeElement;
-  if(el&&!el.closest("#syOverlay")&&(el.isContentEditable||
-    (el.matches("input,textarea")&&el.closest("[data-tdtext],[data-lb],[data-pt],.sticker,.backface"))))el.blur();
   var selection=window.getSelection();if(selection&&!selection.isCollapsed)selection.removeAllRanges();
   if(ghEditing()){
     ghV2.manualWaiting=true;
@@ -11915,7 +11935,8 @@
 }
 function ghCycle(){
   if(ghV2.pendingAck&&!ghFlushAck())return;
-  tabRefresh();if(!ghReady()||!ghConf().auto||document.hidden||ghEditing())return;
+  tabRefresh();if(!ghReady()||!ghConf().auto||document.hidden)return;
+  if(ghEditing()){ghV2.deferred=true;ghSchedule();return;}
   if(ghConf().dirty)ghPush(true);else ghPull(true);
 }
 function ghStart(run){
@@ -11981,7 +12002,7 @@
 }
 function syRead(){
   var c=ghConf(), g=function(id){ var el=document.getElementById(id); return el?el.value.trim():""; };
-  c.repo=ghTidyRepo(g("syRepo"));
+  c.repo=ghTidyRepo(g("syRepo"))||DEFAULT_SYNC_REPO;
   c.path=(g("syPath")||"progress.json").replace(/^\/+/,"").replace(/\s+/g,"");
   c.branch=(g("syBranch")||"main").replace(/\s+/g,"");
   c.token=g("syToken").replace(/\s+/g,"");
@@ -12161,7 +12182,8 @@
 if(cloudSaveButton)cloudSaveButton.title="Save this device's changes to GitHub and combine independent edits from other devices";
 
 
-function loadProgressText(txt){
+function loadProgressText(txt, stableSync){
+  var previous=state;
   try{
     var o=JSON.parse(txt),model=ghCore(o),active=o.spaces&&o.spaces.active||spaces.active;
     if(!model.states[active])active=model.list[0].id;
@@ -12170,7 +12192,9 @@
     try{localStorage.setItem(PKEY,JSON.stringify(memPrefs));storageNotice(PKEY,false);}catch(e){storageNotice(PKEY,true);}
     spaces.list=ghCopy(model.list);spaces.active=active;spaces.seeded=ghCopy(model.seeded);spaces.trash=ghCopy(model.trash);
     spaces.list.forEach(function(sp){writeSpace(sp.id,Object.assign({},model.states[sp.id],model.prefs,{heroZoom:localZoom}),true);});
-    persistSpaces();loadStateOf(active);paintTabs();refreshAll();return true;
+    persistSpaces();loadStateOf(active);paintTabs();
+    if(stableSync&&megaOn&&!megaBusy&&megaView&&megaView.space===active)refreshMegaData(previous);else refreshAll();
+    setupPlannerTaskInputs();paintPlannerBadge();return true;
   }catch(e){syState("Import not applied: "+(e.message||"invalid planner file"),true);return false;}
 }
 /* share sheet - on iPhone this is the "Save to Files" route */
@@ -12507,7 +12531,7 @@
 };
 var LG_PLAIN_BG={ wok:"#F5C5AF", flat:"#FFFFFF", cup:"#FFFFFF", sign:"#FFFFFF", kanji:"#FFFFFF" };
 var LG_FILL={ wok:.80, flat:.80, cup:.80, sign:.74 };
-var LG_NAME={ sweep:"Sweep check", check:"Classic check", wok:"Коробка вок", flat:"Лапша и палочки", cup:"Стакан лапши", sign:"Вывеска", kanji:"Иероглиф 案",
+var LG_NAME={ sweep:"Swoosh · reference", check:"Classic check", wok:"Коробка вок", flat:"Лапша и палочки", cup:"Стакан лапши", sign:"Вывеска", kanji:"Иероглиф 案",
   ph1:"Вдвоём", ph2:"В раковине", ph3:"Большие глаза", ph4:"Под ёлкой" };
 var LG_GNAME={ checks:"Blue checkmarks", plain:"свой фон", music:"красный", speech:"синий", photo:"фотографии" };
 var LG_ARTS=["wok","flat","cup","sign","kanji"];
@@ -12534,7 +12558,7 @@
 function lgReady(fn){ if(LG_READY) fn(); else LG_WAIT.push(fn); }
 
 
-/* Two original, resolution-independent blue checkmarks. The PNG is full-bleed;
+/* Two resolution-independent blue marks. Sweep follows the supplied reference. The PNG is full-bleed;
    iOS supplies its own rounded icon mask. */
 function drawBlueCheck(art,S){
   var c=document.createElement("canvas");c.width=c.height=S;var x=c.getContext("2d");
@@ -12545,7 +12569,7 @@
   x.shadowColor="rgba(14,21,112,.23)";x.shadowBlur=8;x.shadowOffsetY=4;
   var white=x.createLinearGradient(0,160,0,365);white.addColorStop(0,"#FFFFFF");white.addColorStop(1,"#EDF3FF");
   x.fillStyle=white;x.strokeStyle=white;
-  if(art==="sweep"){x.fill(new Path2D("M 111 256 C 98 242 109 223 125 231 L 208 288 C 213 292 218 292 224 288 L 402 158 C 411 152 419 160 412 169 L 247 349 C 231 367 212 367 196 350 Z"));}
+  if(art==="sweep"){x.fill(new Path2D("M 73.59 294.33 L 75.17 296.98 L 75.17 298.56 L 77.29 301.21 L 77.29 302.26 L 78.87 303.85 L 79.93 305.97 L 85.22 311.25 L 85.75 311.25 L 87.33 312.84 L 87.86 312.84 L 90.51 314.95 L 91.56 314.95 L 96.32 317.60 L 97.91 317.60 L 98.44 318.13 L 99.49 318.13 L 101.61 319.18 L 103.72 319.18 L 104.25 319.71 L 107.43 319.71 L 107.95 320.24 L 123.29 320.24 L 123.82 319.71 L 128.05 319.71 L 128.57 319.18 L 131.75 319.18 L 132.28 318.66 L 133.86 318.66 L 134.39 318.13 L 136.51 318.13 L 137.03 317.60 L 139.68 317.60 L 140.21 317.07 L 141.26 317.07 L 141.79 316.54 L 143.38 316.54 L 145.49 315.48 L 149.20 314.95 L 150.78 313.90 L 152.37 313.90 L 153.95 312.84 L 155.54 312.84 L 157.13 311.78 L 158.18 311.78 L 158.71 311.25 L 159.77 311.25 L 160.30 310.72 L 162.94 310.20 L 164.53 309.14 L 165.59 309.14 L 167.17 308.08 L 168.23 308.08 L 170.87 306.49 L 172.46 306.49 L 173.52 305.44 L 175.63 304.38 L 178.28 303.85 L 185.68 300.15 L 187.26 300.15 L 188.32 299.09 L 189.38 299.09 L 190.97 298.03 L 192.02 298.03 L 200.48 293.80 L 202.07 293.80 L 204.18 292.22 L 206.83 291.69 L 215.29 287.46 L 217.93 286.93 L 218.99 285.87 L 221.63 285.34 L 230.09 281.11 L 232.74 280.59 L 233.79 279.53 L 236.44 279.00 L 244.90 274.77 L 247.54 274.24 L 248.60 273.18 L 249.66 273.18 L 254.94 270.54 L 256.00 270.54 L 257.59 269.48 L 258.64 269.48 L 259.70 268.43 L 262.34 267.90 L 266.05 265.78 L 267.10 265.78 L 269.75 264.20 L 270.80 264.20 L 272.39 263.14 L 273.45 263.14 L 274.51 262.08 L 277.15 261.55 L 285.61 257.32 L 288.25 256.79 L 289.31 255.74 L 291.95 255.21 L 300.41 250.98 L 303.06 250.45 L 304.11 249.39 L 305.17 249.39 L 306.76 248.33 L 307.82 248.33 L 308.87 247.28 L 311.52 246.75 L 315.22 244.63 L 316.80 244.63 L 321.56 241.99 L 322.62 241.99 L 323.68 240.93 L 326.32 240.40 L 330.02 238.29 L 331.61 238.29 L 333.72 237.23 L 334.78 236.17 L 337.43 235.64 L 344.83 231.94 L 346.41 231.94 L 348.53 230.89 L 349.59 229.83 L 351.17 229.83 L 359.63 225.60 L 362.28 225.07 L 369.68 221.37 L 372.32 220.84 L 374.44 219.25 L 377.08 218.72 L 384.48 215.02 L 387.13 214.49 L 389.24 212.91 L 391.89 212.38 L 395.59 210.26 L 396.64 210.26 L 399.29 208.68 L 400.34 208.68 L 401.93 207.62 L 402.99 207.62 L 404.05 206.56 L 406.69 206.03 L 410.39 203.92 L 411.45 203.92 L 414.09 202.33 L 415.15 202.33 L 416.74 201.28 L 417.79 201.28 L 418.85 200.22 L 421.49 199.69 L 429.95 195.46 L 432.60 194.93 L 433.66 193.87 L 436.30 193.34 L 439.47 191.76 L 438.41 191.76 L 437.89 192.29 L 436.83 192.29 L 436.30 192.82 L 435.24 192.82 L 433.13 193.87 L 431.01 193.87 L 430.48 194.40 L 428.90 194.40 L 426.78 195.46 L 425.20 195.46 L 424.67 195.99 L 420.97 196.52 L 418.85 197.57 L 417.26 197.57 L 416.74 198.10 L 415.15 198.10 L 414.62 198.63 L 410.92 199.16 L 409.33 200.22 L 407.22 200.22 L 406.69 200.75 L 405.10 200.75 L 404.57 201.28 L 403.52 201.28 L 401.40 202.33 L 396.64 202.86 L 395.06 203.92 L 393.47 203.92 L 392.94 204.45 L 391.36 204.45 L 390.83 204.98 L 387.13 205.51 L 385.01 206.56 L 383.43 206.56 L 382.90 207.09 L 379.20 207.62 L 377.61 208.68 L 372.85 209.21 L 371.26 210.26 L 369.68 210.26 L 367.56 211.32 L 365.45 211.32 L 364.92 211.85 L 363.33 211.85 L 361.22 212.91 L 359.63 212.91 L 359.10 213.44 L 355.40 213.97 L 353.29 215.02 L 351.70 215.02 L 351.17 215.55 L 349.06 215.55 L 348.53 216.08 L 347.47 216.08 L 346.94 216.61 L 345.89 216.61 L 343.77 217.67 L 341.13 217.67 L 340.60 218.20 L 339.54 218.20 L 339.01 218.72 L 337.95 218.72 L 335.84 219.78 L 333.72 219.78 L 333.20 220.31 L 331.61 220.31 L 329.49 221.37 L 327.91 221.37 L 327.38 221.90 L 323.68 222.43 L 321.56 223.48 L 319.98 223.48 L 319.45 224.01 L 317.33 224.01 L 315.22 225.07 L 313.63 225.07 L 312.05 226.13 L 307.29 226.66 L 305.70 227.71 L 304.11 227.71 L 303.59 228.24 L 299.89 228.77 L 299.36 229.30 L 298.30 229.30 L 297.77 229.83 L 296.18 229.83 L 295.66 230.36 L 293.54 230.36 L 291.43 231.41 L 289.84 231.41 L 288.25 232.47 L 285.61 232.47 L 285.08 233.00 L 284.02 233.00 L 283.49 233.53 L 282.44 233.53 L 280.32 234.59 L 275.56 235.11 L 273.98 236.17 L 272.39 236.17 L 271.86 236.70 L 270.28 236.70 L 269.75 237.23 L 266.05 237.76 L 263.93 238.82 L 261.82 238.82 L 259.70 239.87 L 258.11 239.87 L 256.53 240.93 L 251.77 241.46 L 250.18 242.52 L 248.60 242.52 L 248.07 243.05 L 246.48 243.05 L 245.95 243.57 L 243.84 243.57 L 242.25 244.63 L 240.67 244.63 L 240.14 245.16 L 238.02 245.16 L 237.49 245.69 L 236.44 245.69 L 235.91 246.22 L 234.32 246.22 L 232.21 247.28 L 230.09 247.28 L 229.56 247.80 L 227.98 247.80 L 227.45 248.33 L 226.39 248.33 L 224.28 249.39 L 222.69 249.39 L 222.16 249.92 L 220.05 249.92 L 218.46 250.98 L 216.87 250.98 L 216.34 251.51 L 214.76 251.51 L 214.23 252.03 L 210.53 252.56 L 210.00 253.09 L 208.94 253.09 L 208.41 253.62 L 206.83 253.62 L 206.30 254.15 L 204.18 254.15 L 203.66 254.68 L 202.60 254.68 L 200.48 255.74 L 198.90 255.74 L 198.37 256.26 L 196.25 256.26 L 195.72 256.79 L 194.67 256.79 L 194.14 257.32 L 192.55 257.32 L 190.44 258.38 L 188.32 258.38 L 187.79 258.91 L 186.21 258.91 L 184.62 259.97 L 183.03 259.97 L 182.51 260.49 L 180.39 260.49 L 179.86 261.02 L 178.28 261.02 L 176.69 262.08 L 175.10 262.08 L 174.57 262.61 L 171.93 262.61 L 171.40 263.14 L 170.34 263.14 L 169.82 263.67 L 168.23 263.67 L 167.70 264.20 L 165.59 264.20 L 165.06 264.72 L 160.83 264.72 L 160.30 265.25 L 157.13 265.25 L 156.60 265.78 L 141.79 265.78 L 141.26 265.25 L 139.15 265.25 L 138.62 264.72 L 135.45 264.72 L 133.86 263.67 L 132.28 263.67 L 131.22 262.61 L 129.63 262.61 L 127.52 261.02 L 124.87 259.97 L 122.76 257.85 L 122.23 257.85 L 121.17 256.79 L 121.17 256.26 L 120.64 256.26 L 119.06 254.68 L 119.06 254.15 L 116.94 252.03 L 116.94 251.51 L 114.83 248.86 L 113.24 245.69 L 113.24 244.63 L 112.71 244.10 L 112.71 242.52 L 112.18 241.99 L 112.18 240.93 L 111.66 240.40 L 111.66 238.82 L 111.13 238.29 L 111.13 235.11 L 110.60 234.59 L 110.60 228.24 L 111.13 227.71 L 111.13 224.01 L 111.66 223.48 L 111.66 220.84 L 112.18 220.31 L 112.18 218.72 L 112.71 218.20 L 112.71 216.08 L 113.24 215.55 L 113.24 213.97 L 114.30 212.38 L 114.30 211.32 L 114.83 210.79 L 114.83 209.21 L 116.94 204.98 L 116.94 203.92 L 123.29 191.23 L 122.23 191.76 L 122.23 192.29 L 119.59 194.93 L 119.59 195.46 L 118.00 196.52 L 118.00 197.05 L 110.07 205.51 L 110.07 206.03 L 108.48 207.62 L 108.48 208.15 L 106.90 209.21 L 106.90 209.74 L 104.78 211.85 L 104.78 212.38 L 102.67 214.49 L 102.67 215.02 L 96.32 222.43 L 96.32 222.95 L 95.26 224.01 L 94.21 226.13 L 92.62 227.71 L 92.09 229.30 L 90.51 230.89 L 90.51 231.41 L 88.39 234.06 L 87.86 235.64 L 86.28 237.23 L 86.28 238.29 L 84.16 240.93 L 83.63 241.99 L 83.63 243.05 L 82.57 244.10 L 80.99 247.28 L 80.99 248.33 L 79.93 249.39 L 79.93 250.45 L 78.87 252.03 L 78.87 253.09 L 77.82 254.15 L 77.82 255.21 L 77.29 255.74 L 77.29 257.32 L 75.17 261.55 L 75.17 263.67 L 74.64 264.20 L 74.64 265.25 L 73.59 267.37 L 73.59 270.01 L 73.06 270.54 L 73.06 273.18 L 72.53 273.71 L 72.53 278.47 L 72.00 279.00 L 72.00 284.82 L 72.53 285.34 L 72.53 289.57 L 73.06 290.10 L 73.06 292.22 L 73.59 292.75 Z"));}
   else{x.lineWidth=43;x.lineCap="round";x.lineJoin="round";x.stroke(new Path2D("M 123 264 L 218 351 L 391 159"));}
   return c;
 }
@@ -12639,7 +12663,7 @@
       if(!link){link=document.createElement("link");link.rel=rel;link.sizes=size+"x"+size;document.head.appendChild(link);}
       link.type="image/png";
       var asset=(o.art==="sweep"||o.art==="check")&&/^https?:$/.test(location.protocol);
-      link.href=asset?"assets/icons/planner-"+o.art+"-"+size+".png":logoPngOf(o.art,o.bg,size);
+      link.href=asset?"assets/icons/planner-"+o.art+"-"+size+".png?v="+PLANNER_BUILD:logoPngOf(o.art,o.bg,size);
     }
     iconLink("apple-touch-icon",180);iconLink("icon",192);iconLink("icon",32);
     var b=document.getElementById("btnLogo");if(b){var im=b.querySelector("img");if(im&&png)im.src=png;}
@@ -12774,6 +12798,222 @@
 document.addEventListener("focusout",function(){setTimeout(tabRefresh,0);},true);
 window.addEventListener("focus",tabRefresh);
 
+/* Planner 2026.10.08.2: data updates never unseat the open focus workspace. */
+function megaScrollState(){
+  var ov=document.getElementById('megaOv'), saved={top:ov.scrollTop,left:ov.scrollLeft,parts:[],anchor:null};
+  ov.querySelectorAll('[id]').forEach(function(el){if(el.scrollTop||el.scrollLeft)saved.parts.push({el:el,top:el.scrollTop,left:el.scrollLeft});});
+  var top=(document.getElementById('megaBar').getBoundingClientRect().bottom||60)+8;
+  var candidates=[].slice.call(ov.querySelectorAll('[data-td],[data-pr],.megaitem'));
+  for(var i=0;i<candidates.length;i++){
+    var el=candidates[i],r=el.getBoundingClientRect();
+    if(r.top>=top&&r.top<innerHeight&&r.height){
+      saved.anchor={el:el,top:r.top,td:el.getAttribute('data-td'),pr:el.getAttribute('data-pr')};break;
+    }
+  }
+  return saved;
+}
+function megaScrollRestore(s){
+  var ov=document.getElementById('megaOv');ov.scrollTop=s.top;ov.scrollLeft=s.left;
+  s.parts.forEach(function(p){if(p.el.isConnected){p.el.scrollTop=p.top;p.el.scrollLeft=p.left;}});
+  if(s.anchor){
+    var a=s.anchor, el=a.el;
+    if(!el.isConnected){var attr=a.td?'data-td':(a.pr?'data-pr':null),v=a.td||a.pr;
+      if(attr)el=[].slice.call(ov.querySelectorAll('['+attr+']')).filter(function(n){return n.getAttribute(attr)===v;})[0];}
+    if(el&&el.isConnected)ov.scrollTop+=el.getBoundingClientRect().top-a.top;
+  }
+}
+function stageMarkupFor(st){
+  var keep=state,out={};state=st;
+  try{effProjects().forEach(function(p,i){out[p.id]=renderProject(p,i).innerHTML;});}
+  finally{state=keep;}
+  return out;
+}
+function refreshMegaData(previous){
+  // Not a close/reopen operation: card nodes, toolbar and their parents stay put.
+  var scroll=megaScrollState(), old=stageMarkupFor(previous), wanted={}, list=effProjects();
+  list.forEach(function(p,i){
+    wanted[p.id]=true;
+    var card=[].slice.call(document.querySelectorAll('.proj')).filter(function(el){return el.dataset.proj===p.id;})[0];
+    var fresh=renderProject(p,i);
+    if(!card){card=fresh;document.getElementById('projects').appendChild(card);}
+    else if(old[p.id]!==fresh.innerHTML)card.innerHTML=fresh.innerHTML;
+    card.classList.toggle('collapsed',!!state.collapsed[p.id]);
+    card.classList.toggle('inproc',procOn(p.id));
+    if(card.closest('#megaOv'))card.classList.add('inview','mgsettled');
+  });
+  document.querySelectorAll('.proj').forEach(function(el){if(!wanted[el.dataset.proj])el.remove();});
+  megaSaved=megaSaved.filter(function(r){return !r.el.classList.contains('proj')||wanted[r.el.dataset.proj];});
+  reflowProjects();
+  Object.keys(PLISTS).forEach(function(k){
+    var cfg=PLISTS[k];
+    if(!ghEqual(previous[cfg.key],state[cfg.key])||!ghEqual(previous[cfg.nkey],state[cfg.nkey])||previous[cfg.vkey]!==state[cfg.vkey])renderList(cfg);
+  });
+  if(!ghEqual(previous.pairs,state.pairs)||!ghEqual(previous.pairsNext,state.pairsNext)||previous.parView!==state.parView||previous.parFace!==state.parFace)renderPairs();
+  if(!ghEqual(previous.stickers,state.stickers)||!ghEqual(previous.slinks,state.slinks)){
+    var notes={};(state.stickers||[]).forEach(function(st){notes[st.id]=true;var el=stkEl(st.id);
+      if(!el){stickerEl(st);return;}
+      applyBox(st,el);el.querySelector('.stname').textContent=stkName(st);
+      var tx=el.querySelector('.stx');if(st.rh)tx.innerHTML=st.rh;else tx.textContent=st.t||'';
+      var ink=el.querySelector('.ink');if(ink)ink.innerHTML=inkPaths(st);
+    });
+    board.querySelectorAll('.sticker').forEach(function(el){if(!notes[el.dataset.sid])el.remove();});drawLinks();
+  }
+  renderLaunch();paintLogCount();paintTabs();render();applySpot();
+  // Layout/skin choices received from another screen are applied on exit, not
+  // halfway through the user's open focus session. The synced data is not altered.
+  if(previous.logo!==state.logo)applyLogo();
+  paintPlannerBadge();megaScrollRestore(scroll);megaDataRefreshed=true;
+}
+var megaDataRefreshed=false;
+
+/* Protect task fields from credentials/autofill and keep genuine drafts local. */
+function isPlannerSyncAddress(value){
+  var s=String(value||'').trim().replace(/https?:\/\/(?:www\.)?github\.com\//gi,'').replace(/[\s,;]+$/,'').replace(/\/+$/,'');
+  return /^(?:dimitriyvolchenko\/pannerformanytasks)(?:[\s,;]+dimitriyvolchenko\/pannerformanytasks)*$/i.test(s);
+}
+function cleanMisplacedStepAddresses(id){
+  var removed=[];
+  ['steps','stepsNext'].forEach(function(k){(state[k]||[]).forEach(function(it){if(isPlannerSyncAddress(it.t))removed.push({list:k,item:ghCopy(it)});});});
+  if(!removed.length)return;
+  // Never discard even accidental entries without keeping a recoverable copy.
+  try{
+    var key=KEY+':misplaced-step-addresses',saved=JSON.parse(localStorage.getItem(key)||'[]');
+    saved.push({space:id,at:new Date().toISOString(),entries:removed});
+    localStorage.setItem(key,JSON.stringify(saved));
+  }catch(e){return;}
+  ['steps','stepsNext'].forEach(function(k){state[k]=(state[k]||[]).filter(function(it){return !isPlannerSyncAddress(it.t);});});
+  writeSpace(id,state);
+}
+function plannerTaskField(el){
+  return !!(el&&el.matches&&el.matches('.tadd input,[data-addinp],[data-subinp]'));
+}
+function plannerDraftOwner(el){
+  var cfg=Object.keys(PLISTS||{}).map(function(k){return PLISTS[k];}).filter(function(c){return c.inp===el.id;})[0];
+  return spaces.active+":"+(cfg?plKey(cfg):(el.id||('stage-'+(el.getAttribute('data-addinp')||'')+'-sub-'+(el.getAttribute('data-subinp')||''))));
+}
+function plannerDraftKey(el){return KEY+':entry-draft-v1:'+(el.dataset.plannerDraftOwner||plannerDraftOwner(el));}
+function plannerRememberDraft(el){
+  if(!plannerTaskField(el))return;
+  try{var k=plannerDraftKey(el);if(el.value.trim()&&!isPlannerSyncAddress(el.value))localStorage.setItem(k,el.value);else localStorage.removeItem(k);}catch(e){}
+}
+function plannerCommitField(el){
+  if(!plannerTaskField(el)||!el.isConnected||!el.value.trim()||ghComposing)return false;
+  var key=plannerDraftKey(el);
+  if(el.id==='stepsInp'&&isPlannerSyncAddress(el.value)){el.value='';try{localStorage.removeItem(key);}catch(e){};return true;}
+  if(el.hasAttribute('data-addinp'))commitAdd(el.getAttribute('data-addinp'));
+  else if(el.hasAttribute('data-subinp'))commitSub(el.getAttribute('data-subinp'));
+  else{var cfg=Object.keys(PLISTS).map(function(k){return PLISTS[k];}).filter(function(c){return c.inp===el.id;})[0];if(!cfg)return false;addTo(cfg);}
+  try{localStorage.removeItem(key);}catch(e){}return true;
+}
+function prepareAllPlannerEntries(){
+  if(ghComposing){syState('Finish the current character before saving. Your text is kept.',true);return false;}
+  var active=document.activeElement;
+  // Every inline editor already has a blur-to-commit handler, including Parallels,
+  // stage names, waiting notes, project names and the reverse side of a card.
+  if(active&&!active.closest('#syOverlay')&&(active.isContentEditable||active.matches('input,textarea'))){
+    if(plannerTaskField(active))plannerCommitField(active);
+    if(active.isConnected)active.blur();
+  }
+  document.querySelectorAll('.tadd input,[data-addinp],[data-subinp]').forEach(function(el){if(el.getClientRects().length)plannerCommitField(el);});
+  var pa=document.getElementById('parA'),pb=document.getElementById('parB');
+  if(pa&&pb&&(pa.value.trim()||pb.value.trim())&&(pa.getClientRects().length||pb.getClientRects().length))parAddNow();
+  return true;
+}
+function setupPlannerTaskInputs(){
+  document.querySelectorAll('.tadd input,[data-addinp],[data-subinp]').forEach(function(el){
+    el.setAttribute('autocomplete','off');el.setAttribute('data-form-type','other');el.setAttribute('data-lpignore','true');el.setAttribute('data-1p-ignore','true');
+    el.setAttribute('name','planner-entry-'+(el.id||el.getAttribute('data-addinp')||el.getAttribute('data-subinp')));
+    if(!el.hasAttribute('aria-label'))el.setAttribute('aria-label',el.placeholder||'New planner task');
+    var owner=plannerDraftOwner(el);
+    if(el.dataset.plannerDraftOwner&&el.dataset.plannerDraftOwner!==owner){plannerRememberDraft(el);el.value='';}
+    el.dataset.plannerDraftOwner=owner;
+    if(el.id==='stepsInp'&&isPlannerSyncAddress(el.value))el.value='';
+    if(!el.value){try{var draft=localStorage.getItem(plannerDraftKey(el));if(draft&&!isPlannerSyncAddress(draft))el.value=draft;}catch(e){}}
+  });
+}
+document.addEventListener('input',function(e){plannerRememberDraft(e.target);},true);
+document.addEventListener('keydown',function(e){
+  if(e.key==='Enter'&&(e.isComposing||ghComposing||e.keyCode===229))e.stopImmediatePropagation();
+},true);
+document.addEventListener('focusout',function(e){
+  var el=e.target;
+  // Commit on leaving the field, not on a typing timeout: a pause must not split
+  // a half-written sentence into multiple tasks. Mobile Save also commits it.
+  if(plannerTaskField(el)&&!window.matchMedia('(pointer:coarse)').matches&&!ghComposing){
+    plannerCommitField(el);
+  }
+},true);
+window.addEventListener('pageshow',setupPlannerTaskInputs);
+
+/* Badge = unfinished CURRENT tasks in the enabled sources of the active project.
+   Permission belongs to this device; source selection belongs to the project. */
+var plannerBadgeLast=null,plannerBadgeQueued=false;
+function plannerBadgeSources(){return state.badgeSources||{today:true,tasks:false};}
+function plannerBadgeCount(){
+  var s=plannerBadgeSources(),count=0;
+  ['today','tasks'].forEach(function(k){if(s[k])count+=(state[k]||[]).filter(function(t){return !t.done&&String(t.t||'').trim();}).length;});
+  return count;
+}
+function plannerBadgeStatus(){
+  if(typeof navigator.setAppBadge!=='function')return 'Open the installed Home Screen web app to use its icon badge. The counter here still works.';
+  if(typeof Notification!=='undefined'&&Notification.permission==='denied')return 'Badges are blocked on this device. Allow notifications/badges for Planner in system settings.';
+  if(typeof Notification!=='undefined'&&Notification.permission!=='granted')return 'Allow notifications on this device to show the Home Screen badge.';
+  return 'Badge updates while Planner is open or when it receives changes. No background push service is configured.';
+}
+function paintPlannerBadge(){
+  var count=plannerBadgeCount(),sources=plannerBadgeSources();
+  document.querySelectorAll('[data-planner-badge-source]').forEach(function(b){var k=b.dataset.plannerBadgeSource,on=!!sources[k];
+    b.classList.toggle('on',on);b.setAttribute('aria-pressed',String(on));
+    var n=(state[k]||[]).filter(function(t){return !t.done&&String(t.t||'').trim();}).length;
+    b.title=(on?'Exclude ':'Include ')+(k==='today'?'Priority for today':'Tasks')+' in the icon badge: '+n+' unfinished';
+    b.querySelector('.badge-number').textContent=on?String(n):'off';
+  });
+  var value=document.getElementById('plannerBadgeTotal');if(value)value.textContent=count?String(count):'';
+  var status=document.getElementById('plannerBadgeStatus');if(status)status.textContent=plannerBadgeStatus();
+  if(plannerBadgeQueued)return;plannerBadgeQueued=true;
+  Promise.resolve().then(function(){
+    plannerBadgeQueued=false;var n=plannerBadgeCount();
+    if(n===plannerBadgeLast||typeof navigator.setAppBadge!=='function')return;
+    plannerBadgeLast=n;
+    try{var job=n?navigator.setAppBadge(n):(navigator.clearAppBadge?navigator.clearAppBadge():navigator.setAppBadge(0));
+      Promise.resolve(job).catch(function(){plannerBadgeLast=null;var st=document.getElementById('plannerBadgeStatus');if(st)st.textContent=plannerBadgeStatus();});
+    }catch(e){plannerBadgeLast=null;}
+  });
+}
+function plannerBadgePermission(){
+  if(typeof Notification==='undefined'||typeof navigator.setAppBadge!=='function'){toast('Use Planner as a Home Screen web app on a supported device.');paintPlannerBadge();return;}
+  if(Notification.permission==='denied'){toast('Allow Planner notifications and badges in system settings.');paintPlannerBadge();return;}
+  if(Notification.permission==='default'){
+    try{Notification.requestPermission().then(function(){plannerBadgeLast=null;paintPlannerBadge();}).catch(function(){paintPlannerBadge();});}catch(e){paintPlannerBadge();}
+  }else{plannerBadgeLast=null;paintPlannerBadge();}
+}
+function setupPlannerBadges(){
+  ['today','tasks'].forEach(function(k){
+    var title=document.getElementById(k==='today'?'todayTitle':'tasksTitle');if(!title||document.querySelector('[data-planner-badge-source="'+k+'"]'))return;
+    var b=document.createElement('button');b.type='button';b.className='planner-badge-toggle';b.dataset.plannerBadgeSource=k;
+    b.setAttribute('aria-label','Toggle icon badge for '+(k==='today'?'Priority for today':'Tasks'));
+    b.innerHTML='<span class="badge-light" aria-hidden="true"></span><span class="badge-word">badge</span><b class="badge-number"></b>';
+    title.insertAdjacentElement('afterend',b);
+  });
+  var h=document.getElementById('btnLogo');if(h&&!document.getElementById('plannerBadgeTotal')){var badge=document.createElement('b');badge.id='plannerBadgeTotal';badge.setAttribute('aria-label','Unfinished tasks included in icon badge');h.appendChild(badge);}
+  var box=document.createElement('div');box.className='planner-badge-settings';
+  box.innerHTML='<b>Home Screen badge</b><p id="plannerBadgeStatus" role="status"></p><button type="button" class="btn" id="plannerAllowBadge">Allow icon badge on this device</button><p>Counts unfinished Priority for today and/or Tasks in the active project. Tomorrow and later lists are not counted. Both switches on = the sum; both off = no badge.</p><button type="button" class="btn" id="plannerRecoveredSteps">Export recovered misplaced addresses</button>';
+  document.querySelector('#syOverlay .body').appendChild(box);
+  document.getElementById('plannerAllowBadge').onclick=plannerBadgePermission;
+  document.getElementById('plannerRecoveredSteps').onclick=function(){var raw=localStorage.getItem(KEY+':misplaced-step-addresses');if(raw)downloadProgress(raw,'planner-recovered-misplaced-addresses.json');else toast('No misplaced addresses needed to be removed.');};
+  document.addEventListener('click',function(e){
+    var b=e.target.closest('[data-planner-badge-source]');if(!b)return;e.preventDefault();e.stopPropagation();
+    var s=Object.assign({},plannerBadgeSources()),k=b.dataset.plannerBadgeSource;s[k]=!s[k];state.badgeSources=s;persist();paintPlannerBadge();
+    if(s[k])plannerBadgePermission();
+  });
+  document.addEventListener('visibilitychange',function(){if(!document.hidden){plannerBadgeLast=null;paintPlannerBadge();}});
+  paintPlannerBadge();
+}
+setupPlannerTaskInputs();setupPlannerBadges();
+if('serviceWorker' in navigator&&/^https?:$/.test(location.protocol)){
+  navigator.serviceWorker.register('./sw.js',{scope:'./',updateViaCache:'none'}).catch(function(){/* Foreground badge works without a worker; no cache is installed. */});
+}
+
 })();
 </script>
 
