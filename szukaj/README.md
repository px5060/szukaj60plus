# SZUKAJ+ — wyszukiwarka modeli STEP → [STEP2] → TRIGGER ×n → zakład

Appka = `../index.html` (repo osobne od RAZEM, własny adres).

- **Kody** są wspólne z RAZEM: ten sam klucz pamięci (`t50razem_v1_added` / `t60razem_v1_added`).
  Kod wpisany tu widać w RAZEM i odwrotnie. ⟲ cofa ostatni kod w obu miejscach.
- **Silnik**: STEP (SERIA ×x albo UKŁAD) → [STEP2, raz] → TRIGGER ×tn (kolejne trafienia) → zakład na ostatnim TRIGGER+offset,
  progresja trwała K8 (8, 8, 16, 32, 64, 128, 256, 512), kurs 3,0. Model = `[typ, STEP, x, TRIGGER, off, tn, STEP2]`;
  `tn = 1` i pusty STEP2 = stary model SZUKAJ (wynik 1:1 z silnikiem 1T z RAZEM). `xcheck.py`: silnik JS ze strony = engine.py.
- **Kryteria** (domyślne, zmieniane na stronie): do 200 cykli max 5 BUST, do 300 max 9, do 400 max 11,
  ponad 400 max 11 (te pokazywane zawsze najwyżej, ★), min. 100 cykli.
  Sprawdzane po każdym kodzie na całym ciągu (baza + dopisane).
- **GRA** pokazuje modele spełniające kryteria, które są na kroku 5 / 6 / 7 (64 / 128 / 256 zł):
  GRA na następnym wierszu, zakład ustawiony, STEP otwarty (z kodami, które dadzą TRIGGER).
- **TABELA**: wybierz model (albo dotknij karty na GRA) — na ciąg kodów nanoszone są jego etykiety
  (STEP, TRIGGER, przed grą, krok i stawka, WIN / przegrana / BUST), najnowsze u góry.
- **Import kodów** (zakładka SZUKAJ): plik eksportu z RAZEM lub jej tabel (.json z `codes`, pełny ciąg od Nr 1)
  albo plik tekstowy; kody muszą zgadzać się z ciągiem, dopisywane są tylko nowe.
- **Tylko pula z chmury**: szukanie w telefonie jest wyłączone (losowanie dawało różne modele na telefonie i PC). Pulę aktualizuje `search.py` na nowym ciągu (`dopisane.txt`), potem build i nowa wersja appki.

## Pula z chmury (duże przeszukanie)

```
pip install numba numpy
python3 search.py t50 x1x            # T60: python3 search.py t60 x1x ; python3 search.py t60 xx1
python3 build_szukaj.py t50          # T60: python3 build_szukaj.py t60   → ../index.html
```

`search.py` bierze pulę starych modeli i dla każdego nowego typu (TRIGGER ×2, ×3, STEP2, STEP2 + TRIGGER ×2) liczy kilka milionów konfiguracji na bazie `seed_<t50|t60>.txt` (+ kody z `dopisane.txt`, jeśli jest)
i zapisuje pulę warstwową: najlepsze wg BUST/cykl w przedziałach 401+ / 100–200 / 201–300 / 301–400 cykli.
Kolejne uruchomienia z innym ziarnem i `--dolacz` dokładają modele do istniejącej puli:
`python3 search.py t50 x1x 6000000 21 --dolacz`.
