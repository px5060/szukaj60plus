"""SZUKAJ+: szukanie nowych typów modeli (TRIGGER ×2/×3, STEP2) i dopisanie ich do puli starych modeli SZUKAJ.\nSzukanie puli modeli na całej bazie (seed_<t50|t60>.txt + opcjonalnie szukaj/dopisane.txt).
Uruchom w katalogu szukaj/:  python3 search.py t50|t60 x1x|xx1 [n_konfiguracji] [ziarno] [--dolacz]   (wymaga: pip install numba numpy)
Potem:                        python3 build_szukaj.py t50|t60   → ../index.html"""
import sys, json, itertools, time, re, pathlib, numpy as np
from engine import *

HERE = pathlib.Path(__file__).resolve().parent


def seed_codes():
    """Baza (seed_<t50|t60>.txt = MASTER_SEED appki RAZEM od Nr 1) + kody z dopisane.txt (same cyfry, dowolne odstępy)."""
    name = 't50' if (HERE / 'seed_t50.txt').exists() else 't60'
    s = re.sub(r'\D', '', (HERE / f'seed_{name}.txt').read_text())
    f = HERE / 'dopisane.txt'
    if f.exists():
        s += re.sub(r'\D', '', f.read_text())
    return [s[i:i + 3] for i in range(0, len(s) - len(s) % 3, 3)]


RULES = [(200, 5), (300, 9), (400, 11), (None, 11)]   # None = ponad ostatni próg (bez górnej granicy)
MIN_CYC = 100
MARGIN = 1          # w puli też modele o 1 BUST ponad limit (mogą wejść z nowymi kodami); appka filtruje ściśle


def specs(name):
    al = ALPH[name]
    pats = [a + b + c for a in FIRST[name] for b in '01x' for c in '01x' if a + b + c != 'xxx']
    step = []
    for r in (1, 2, 3) if name == 't50' else (1, 2):
        for U in itertools.combinations(al, r):
            step.append(('SERIA', '∪'.join(U)))
    step += [('UKŁAD', p + ' → ' + q) for p in pats for q in pats]
    trig = pats + [p + ' → ' + q for p in pats for q in pats]
    return al, step, trig


def tabs(preds, al):
    T = np.zeros((len(preds), 3, len(al)), np.uint8); L = np.zeros(len(preds), np.int64)
    for k, p in enumerate(preds):
        T[k], L[k] = table(p, al)
    return T, L


FAMILIES = [(2, False), (3, False), (1, True), (2, True)]   # (tn, STEP2): nowe typy; stary typ (1, False) = pula SZUKAJ


def main():
    name, target = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 6_000_000
    codes = seed_codes()
    al, step, trig = specs(name)
    X = np.array([al.index(c) for c in codes], np.int64)
    y = np.array([c[TARGET_POS[target]] == '1' for c in al], np.uint8)
    STAB, SL = tabs([s for _, s in step], al); TTAB, TL = tabs(trig, al)
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    rng = np.random.default_rng(seed)
    ser_all = np.array([t == 'SERIA' for t, _ in step])
    # pula startowa: stare modele SZUKAJ (STEP → TRIGGER) → format 7 pól
    old = HERE / f'pool_{name}_{target}.json'
    pool = [m + [1, ''] if len(m) == 5 else m for m in json.loads(old.read_text())['pool']] if old.exists() else []
    seen = {json.dumps(m, ensure_ascii=False) for m in pool}
    for tn, use2 in FAMILIES:
        a = rng.integers(0, len(step), n); b = rng.integers(0, len(trig), n); off = rng.integers(1, 8, n)
        x = np.where(ser_all[a], rng.integers(1, 6, n), 1)
        c = rng.integers(0, len(step), n) if use2 else np.full(n, -1)
        cfg = np.unique(np.stack([a, b, x, off, c, np.full(n, tn)], 1).astype(np.int64), axis=0)
        OUT = np.zeros((len(cfg), 13), np.int64)
        t = time.time(); run_cfg(STAB, SL, TTAB, TL, cfg, X, y, len(X), OUT)
        cyc = OUT[:, 1] + OUT[:, 2]; bu = OUT[:, 2]
        lim = np.full(len(cfg), -1)
        for mc, mb in reversed(RULES):
            lim[cyc <= mc if mc is not None else cyc >= 0] = mb
        ok = (cyc >= MIN_CYC) & (lim >= 0) & (bu <= lim + MARGIN)
        strict = ok & (bu <= lim)
        fam = f'TRIGGER ×{tn}' + (' + STEP2' if use2 else '')
        print(f'{name} {target} {fam}: {len(cfg):,} konfiguracji w {time.time()-t:.0f}s; spełnia ściśle {strict.sum():,}, z marginesem {ok.sum():,}', flush=True)
        added = 0
        for lo, hi, take in [(401, 10**9, 1000), (100, 200, 500), (201, 300, 500), (301, 400, 500)]:
            g = np.where(ok & (cyc >= lo) & (cyc <= hi))[0]
            for k in g[np.lexsort((-cyc[g], bu[g] / cyc[g]))][:take]:
                t_, s_ = step[cfg[k, 0]]
                m = [t_[0], s_, int(cfg[k, 2]), trig[cfg[k, 1]], int(cfg[k, 3]), tn, step[cfg[k, 4]][1] if use2 else '']
                j = json.dumps(m, ensure_ascii=False)
                if j not in seen:
                    seen.add(j); pool.append(m); added += 1
        print('   dodano', added, flush=True)
    json.dump({'name': name, 'target': target, 'seedN': len(codes), 'rules': RULES, 'minCyc': MIN_CYC, 'pool': pool},
              open(HERE / f'pool_{name}_{target}.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('   pula zapisana:', len(pool))


if __name__ == '__main__':
    main()
