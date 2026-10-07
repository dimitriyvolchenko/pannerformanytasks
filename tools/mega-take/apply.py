from pathlib import Path
import hashlib
p=Path('index.html'); raw=p.read_bytes(); s=raw.decode()
assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()=='9956568ff3ee8e3823f303d125d767d2a85b7a19'
def change(old,new):
    global s
    assert s.count(old)==1,(s.count(old),old[:100])
    s=s.replace(old,new)
change('var PLANNER_BUILD="2026.10.07.1",','var PLANNER_BUILD="2026.10.07.2",')
change('#megaOv{position:fixed; inset:0; z-index:200; display:none; overflow:auto;', '#megaOv{position:fixed; inset:0; z-index:200; display:none; overflow:auto; overflow-x:hidden;')
change('  /* the page folding away underneath */', '''  /* A refresh is not a new entry: do not fly restored cards in again. */
  #megaOv:not(.gone) .megaitem.mgsettled{animation:none; transform:none}
  /* Keep the full document fold in 2D. Perspective rotation of a very tall
     board can project it across the camera plane and expand an iPad's layout
     viewport several times, even though the board itself is invisible. */
  /* the page folding away underneath */''')
change('to{opacity:0; transform:perspective(1500px) rotateX(16deg) scale(.86) translateY(30px); filter:blur(7px)}','to{opacity:0; transform:translateY(20px) scale(.98); filter:blur(7px)}')
change('from{opacity:0; transform:perspective(1500px) rotateX(16deg) scale(.86) translateY(30px); filter:blur(7px)}','from{opacity:0; transform:translateY(20px) scale(.98); filter:blur(7px)}')
change('''function withMegaHome(fn){
  var restore=!!megaOn&&!megaRebuilding;
  if(restore){megaRebuilding=true;mgKeysOut();megaRestore();}
  try{return fn();}finally{if(restore){applySpot();megaStage();mgKeysIn();megaRebuilding=false;}}
}''','''function withMegaHome(fn){
  var restore=!!megaOn&&!megaRebuilding, scroll=[];
  if(restore){
    var ov=document.getElementById("megaOv");
    [ov].concat([].slice.call(ov.querySelectorAll("[id]"))).forEach(function(el){
      if(el&&(el===ov||el.scrollTop||el.scrollLeft))scroll.push({id:el.id,top:el.scrollTop,left:el.scrollLeft});
    });
    megaRebuilding=true;
    /* Save/Take belong to the persistent toolbar: moving a focused button back
       into the hidden header makes Safari scroll and can break its hit target. */
    megaRestore();
  }
  try{return fn();}finally{
    if(restore){
      try{
        applySpot();megaStage(true);
        scroll.forEach(function(pos){
          var el=document.getElementById(pos.id);if(!el)return;
          el.scrollTop=Math.max(0,Math.min(pos.top,el.scrollHeight-el.clientHeight));
          el.scrollLeft=Math.max(0,Math.min(pos.left,el.scrollWidth-el.clientWidth));
        });
      }finally{megaRebuilding=false;}
    }
  }
}''')
change('function megaTablet(){ var w=window.innerWidth||0; return w>760 && w<=1400; }','function megaTablet(){ var w=document.documentElement.clientWidth||window.innerWidth||0; return w>760 && w<=1400; }')
change('function megaStage(){\n  var els=megaPieces();','function megaStage(stable){\n  var els=megaPieces();')
change('''    el.classList.add("megaitem");
    host.appendChild(el);''','''    el.classList.add("megaitem");
    el.classList.toggle("mgsettled", !!stable);
    host.appendChild(el);''')
change('r.el.classList.remove("megaitem");','r.el.classList.remove("megaitem","mgsettled");')
a=raw.decode();start='/* ================= SYNC THROUGH YOUR OWN GITHUB';end='/* ================= SCROLL FX ================= */'
assert a[a.index(start):a.index(end)]==s[s.index(start):s.index(end)]
assert hashlib.sha256(s.encode()).hexdigest()=='dba5545aec6eb3a67c5fdc4335466bf632978fb8a210d43cca07c698f35fb1f5'
Path('fixed.html').write_text(s,encoding='utf-8',newline='')
print('PASS Exact tested patch; GitHub exchange and storage code unchanged')
