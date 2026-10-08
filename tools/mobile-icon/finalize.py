from pathlib import Path
import hashlib
p=Path('fixed.html')
s=p.read_text(encoding='utf-8')
assert hashlib.sha256(s.encode()).hexdigest()=='65ff200aa78d9ce829827ac5389c6c530acaeac201f9b6677021abc54fe70da7'
def once(old,new):
 global s
 assert s.count(old)==1,old
 s=s.replace(old,new)
once('  document.documentElement.style.setProperty("--heroH", Math.round(h.getBoundingClientRect().height)+"px");',
'''  var value=Math.round(h.getBoundingClientRect().height)+"px";
  if(document.documentElement.style.getPropertyValue("--heroH")!==value)
    document.documentElement.style.setProperty("--heroH",value);''')
once('if(window.ResizeObserver){ try{ new ResizeObserver(syncHeroHeight).observe(document.getElementById("hero")); }catch(e){} }',
'''/* ResizeObserver is a measurement phase. Defer layout-dependent writes to the
   next frame, and avoid writing an unchanged height, to prevent a WebKit loop. */
var heroMeasureFrame=0;
function queueHeroHeight(){
  if(heroMeasureFrame)return;
  heroMeasureFrame=requestAnimationFrame(function(){heroMeasureFrame=0;syncHeroHeight();});
}
if(window.ResizeObserver){try{new ResizeObserver(queueHeroHeight).observe(document.getElementById("hero"));}catch(e){}}''')
assert hashlib.sha256(s.encode()).hexdigest()=='c8b1896b19d5f683ffe2adad8191d62f8ef981361df6b5137906899ae15e01a2'
p.write_text(s,encoding='utf-8',newline='')
print('PASS Layout measurement writes coalesced outside ResizeObserver delivery')
