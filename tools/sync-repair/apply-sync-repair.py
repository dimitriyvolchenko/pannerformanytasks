"""Apply the reviewed synchronization repair to the exact audited HTML snapshot.
No progress.json data is read or modified by this build step.
"""
from pathlib import Path
import hashlib
import re

path = Path('index.html')
raw = path.read_bytes()
expected = 'e32bb34b873d2bb93a9299678fd30e0ddfc1b2ab'
actual = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
assert actual == expected, f'Source changed: {actual}. Review before applying.'
s = raw.decode('utf-8')

def once(old, new):
    global s
    assert s.count(old) == 1, 'Missing or ambiguous patch anchor: ' + old[:70]
    s = s.replace(old, new, 1)

def section(start, end, replacement):
    global s
    assert s.count(start) == 1 and s.count(end) == 1
    a = s.index(start)
    b = s.index(end, a)
    s = s[:a] + replacement + '\n' + s[b:]

section('function ghLeads(){', 'function guessDevice(){',
        '/* Compatibility hook: leadership never blocks a device from saving. */\nfunction ghLeads(){ return true; }')
section('function ghFetchRemote(){', '/* a quiet dot on the sync button',
        Path(__file__).with_name('sync-v2.js').read_text())

a=s.index('function progressText(){'); b=s.index('/* everything the page has to redo', a)
part=s[a:b]
assert part.count('  persist();') == 1
part=part.replace('  persist();', '  writeSpace(spaces.active, state);')
part=part.replace('  payload.spaces=all;', '  all.seeded=spaces.seeded||{}; all.trash=spaces.trash||[];\n  payload.prefs=readPrefs()||{};\n  payload.spaces=all;')
s=s[:a]+part+s[b:]

once('b.classList.toggle("hasnew", !!(ghReady() && c.dirty && !(c.auto && ghLeads())));',
     'b.classList.toggle("hasnew", !!(ghReady() && c.dirty));')
a=s.index('  var L=document.getElementById("syLead");', s.index('function syPaint(){'))
b=s.index('  paintSyncDot();',a)
s=s[:a]+'''  var L=document.getElementById("syLead");
  if(L){ L.hidden=true; L.style.display="none"; L.disabled=true; }
  var box=document.getElementById("syLeadBox");
  if(box){
    box.innerHTML="<b>Sync v2: all devices are equal.</b> Save to GitHub works on every device. "+
      "With auto on, changes are sent and checked on returning to the app. "+
      "Independent edits are combined; competing edits never overwrite silently.<br>"+
      '<button class="btn" id="syRecoveryV2">Recovery copies</button>';
    document.getElementById("syRecoveryV2").onclick=ghRecovery;
  }
'''+s[b:]
once('  } else syState(document.getElementById("syState").textContent);',
     '  } /* Keep any error state visible until the next actual sync result. */')
section('document.getElementById("syLead").addEventListener("click", function(){',
        'document.getElementById("syPush").addEventListener',
        '''document.getElementById("syLead").addEventListener("click", function(){
  var c=ghConf(); c.lead=false; c.remoteLead=""; ghSave(); syPaint();
  syState("All devices can save; choosing a main device is no longer needed");
});''')
once('  syState(c.auto?"Every change is sent a few seconds later, and the newer copy is taken when the page opens"\n                :"Sending and taking now happen only by hand");',
     '  syState(c.auto?"Automatic two-way sync is on for this device"\n                :"Automatic sync is off; Save to GitHub still works by hand");\n  if(c.auto)ghCycle();')
once('setTimeout(function(){ paintSyncDot(); if(ghReady() && ghConf().auto) ghPull(true).then(function(){ syPaint(); }); }, 1200);',
'''setTimeout(function(){ ghStart(); }, 1200);
window.addEventListener("focus", ghCycle);
window.addEventListener("online", function(){ ghV2.blockedUntil=0; ghCycle(); });
document.addEventListener("visibilitychange", function(){ if(!document.hidden)ghCycle(); });
document.addEventListener("focusout", function(){ if(ghV2.started)ghSchedule(); }, true);
setInterval(ghCycle, 30000);
/* Export and synchronization are different operations. */
var exportButton=document.getElementById("btnExport");
if(exportButton){ exportButton.textContent="backup file"; exportButton.title="Export a local JSON backup. To sync devices, use Save to GitHub."; }
var cloudSaveButton=document.getElementById("btnGhSave");
if(cloudSaveButton)cloudSaveButton.title="Save this device's changes to GitHub and combine independent edits from other devices";
''')
once('          if(!canWrite){', '          if(canWrite===false){')
once('          out+=syRepLine("ok","The key may write to it");',
     '          out+=syRepLine("ok","The repository is accessible. An actual save verifies this key has Contents: Read and write");')
# Context menus are appended to <body>, while Mega Focus is z-index 200.
# Keep every floating editor above that fullscreen layer.
once('#plMenu{position:fixed; z-index:150;', '#plMenu{position:fixed; z-index:320;')
once('#richMenu{position:fixed; z-index:140;', '#richMenu{position:fixed; z-index:320;')
once('#ctxMenu{position:fixed; z-index:130;', '#ctxMenu{position:fixed; z-index:320;')
once('#lineMenu{position:fixed; z-index:150;', '#lineMenu{position:fixed; z-index:320;')
once('#pinkMenu{position:fixed; z-index:150;', '#pinkMenu{position:fixed; z-index:320;')
assert s.count('id="stepsList"')==1
assert s.count('function ghPush(')==1 and s.count('function ghPull(')==1
assert s.count('<script')==raw.decode().count('<script')
assert 'if(!c.auto || !ghLeads()) return;' not in s
path.write_text(s, encoding='utf-8', newline='')
print('Audited source blob:',actual)
print('Patched HTML bytes:',len(s.encode()))
print('Only application code changed; progress.json was not modified.')
