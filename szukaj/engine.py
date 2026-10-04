"""Silnik SZUKAJ+ — STEP ×x → [STEP2] → TRIGGER ×tn → zakład na ostatnim TRIGGER+offset (tn=1 bez STEP2 = silnik 1T z RAZEM).
Progresja trwała K8 (8,8,16,32,64,128,256,512), kurs 3.0. Predykat = lista pozycji ' → ', każda pozycja = unia wzorców '∪'
('x' = dowolna cyfra). Kody trzymane jako indeksy alfabetu; predykat = tablica (L × nA) zero-jedynkowa."""
import numpy as np
from numba import njit, prange

ST = np.array([8, 8, 16, 32, 64, 128, 256, 512], np.int64)
CUM = np.cumsum(ST)
ALPH = {'t50': [a + b + c for a in '01' for b in '01' for c in '01'],
        't60': [a + b + c for a in '0123' for b in '01' for c in '01']}
FIRST = {'t50': '01x', 't60': '0123x'}
TARGET_POS = {'x1x': 1, 'xx1': 2, '1xx': 0}


def load(path):
    s = open(path).read().strip()
    return [s[i:i + 3] for i in range(0, len(s), 3)]


def m1(p, c):
    return any(len(q) == 3 and all(a == 'x' or a == b for a, b in zip(q, c)) for q in p.split('∪'))


def table(pred, alph):
    """'x01 → 0xx∪2xx' → (3 × nA) uint8, L"""
    parts = pred.split(' → ')
    t = np.zeros((3, len(alph)), np.uint8)
    for j, p in enumerate(parts):
        t[j] = [m1(p, c) for c in alph]
    return t, len(parts)


@njit(cache=True)
def hit(tab, L, X, i):
    if i < L - 1:
        return False
    for j in range(L):
        if tab[j, X[i - L + 1 + j]] == 0:
            return False
    return True


@njit(cache=True)
def sim(stab, sL, ttab, tL, x, off, s2tab, s2L, use2, tn, X, y, N, out):
    """Model: STEP (×x pod rząd) → [STEP2, jeden raz] → TRIGGER ×tn (kolejne trafienia, nie muszą być pod rząd) → zakład na ostatnim TRIGGER+off.
    out: [zakł, W, BUST, bilans, k5_wejścia, k5_W, bs_teraz, faza, w_STEP, w_ZAKŁ, cnt, st, tc]
    faza: 0 czekam na STEP, 1 STEP otwarty (st 1 = czekam na STEP2, st 2 = liczę TRIGGERY), 2 zakład ustawiony (w_ZAKŁ ≥ N)"""
    st = 0; cnt = 0; tc = 0; bs = 0; i = 0; pnl = 0; nb = 0; nw = 0; nbu = 0; k5 = 0; k5w = 0; srow = -1; wz = -1; ph = 0
    while i < N:
        if st == 0:
            if hit(stab, sL, X, i):
                cnt += 1
                if cnt >= x:
                    st = 1 if use2 else 2; srow = i
            else:
                cnt = 0
            i += 1
        elif st == 1:
            if hit(s2tab, s2L, X, i):
                st = 2
            i += 1
        elif hit(ttab, tL, X, i):
            tc += 1
            if tc < tn:
                i += 1
                continue
            bp = i + off
            if bp >= N:
                ph = 2; wz = bp
                break
            nb += 1
            if bs == 4:
                k5 += 1
            if y[X[bp]]:
                pnl += ST[bs] * 3 - CUM[bs]; nw += 1
                if bs >= 4:
                    k5w += 1
                bs = 0
            elif bs == 7:
                pnl -= CUM[7]; nbu += 1; bs = 0
            else:
                bs += 1
            st = 0; cnt = 0; tc = 0; i = bp + 1
        else:
            i += 1
    if ph == 0 and st >= 1:
        ph = 1
    out[0] = nb; out[1] = nw; out[2] = nbu; out[3] = pnl; out[4] = k5; out[5] = k5w
    out[6] = bs; out[7] = ph; out[8] = srow; out[9] = wz; out[10] = cnt; out[11] = st; out[12] = tc


@njit(parallel=True, cache=True)
def run_cfg(STAB, SL, TTAB, TL, cfg, X, y, N, OUT):
    """cfg: [STEP, TRIGGER, x, off, STEP2 (-1 = brak), tn]; STEP2 z tej samej listy co STEP"""
    for k in prange(cfg.shape[0]):
        a, b, x, off, c, tn = cfg[k, 0], cfg[k, 1], cfg[k, 2], cfg[k, 3], cfg[k, 4], cfg[k, 5]
        cc = c if c >= 0 else 0
        sim(STAB[a], SL[a], TTAB[b], TL[b], x, off, STAB[cc], SL[cc], c >= 0, tn, X, y, N, OUT[k])


def sim_model(m, al, X, y, out):
    """m = [typ, STEP, x, TRIGGER, off, tn, STEP2]"""
    a, la = table(m[1], al); b, lb = table(m[3], al)
    s2 = m[6] if len(m) > 6 else ''
    c, lc = table(s2 or 'xxx', al)
    sim(a, la, b, lb, m[2], m[4], c, lc, bool(s2), m[5] if len(m) > 5 else 1, X, y, len(X), out)


def limit_for(cycles, rules):
    """rules = [(max_cykli, max_bust), ...] rosnąco; zwraca max_bust lub None (poza regułami)."""
    for mc, mb in rules:
        if mc is None or cycles <= mc:
            return mb
    return None
