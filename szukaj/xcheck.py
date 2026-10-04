"""Porównanie silnika JS (worker z index.html) z engine.py na modelach z puli (wszystkie typy: TRIGGER ×n, STEP2)."""
import json, re, subprocess, sys, pathlib, numpy as np, random
from engine import *
repo = pathlib.Path(sys.argv[1]); name = sys.argv[2]
html = (repo / 'index.html').read_text()
wsrc = re.search(r'<script id="wsrc" type="text/js-worker">(.*?)</script>', html, re.S).group(1)
pools = json.loads(re.search(r'const POOLS = (\{.*?\});\s', html).group(1))
seed = re.search(r"const MASTER_SEED = '(\d+)'", html).group(1)
al = ALPH[name]; random.seed(3)
codes = [seed[i:i+3] for i in range(0, len(seed), 3)] + random.choices(al, k=37)   # + 37 "nowych" kodów
X = np.array([al.index(c) for c in codes], np.int64)
bad = 0
for t, P in pools.items():
    y = np.array([c[TARGET_POS[t]] == '1' for c in al], np.uint8)
    fam = {}
    for m in P['pool']: fam.setdefault((m[5], bool(m[6])), []).append(m)
    mods = [m for L in fam.values() for m in random.sample(L, min(150, len(L)))]
    js = wsrc + f"""
setData({{AL:{json.dumps(al)},X:{json.dumps(X.tolist())},Y:{json.dumps(y.tolist())}}});
const R={{rules:[[200,5],[300,9],[400,11]],minCyc:100}};
console.log(JSON.stringify({json.dumps(mods, ensure_ascii=False)}.map(m=>{{const r=sim(m,R);return [r.nb,r.nw,r.nbu,r.pnl,r.k5,r.k5w,r.bs,r.ph,r.srow,r.wz,r.cnt,r.st,r.tc];}})));"""
    tmp = pathlib.Path('/tmp/claude-0/xcheck.js'); tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(js.replace('onmessage =', 'const _om =').replace('postMessage', '(()=>0)'))
    p = subprocess.run(['node', str(tmp)], capture_output=True, text=True)
    if p.returncode: print(p.stderr[:2000]); sys.exit(1)
    out = json.loads(p.stdout)
    o = np.zeros(13, np.int64)
    for m, r in zip(mods, out):
        sim_model(m, al, X, y, o)
        if list(o) != r: bad += 1; print('RÓŻNICA', m, list(o), r)
    print(name, t, 'sprawdzono', len(mods), 'modeli', {k: len(v) for k, v in fam.items()}, 'różnic:', bad)
