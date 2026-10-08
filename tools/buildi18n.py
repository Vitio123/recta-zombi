"""Valida tools/i18n/<idioma>.txt (id|texto, ⏎ = salto de línea) contra los textos en español del juego
y genera i18n/<idioma>.json, que el juego carga al elegir ese idioma.  Uso (desde web/): python tools/buildi18n.py"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
i = html.index("const CES="); j = html.index(";\nconst CT={}", i)
CES = json.loads(html[i + len("const CES="):j])
os.makedirs(os.path.join(ROOT, "i18n"), exist_ok=True)
ph = lambda t: sorted(re.findall(r"\{\d+\}", t))
ok = True
for f in sorted(os.listdir(os.path.join(ROOT, "tools", "i18n"))):
    if not f.endswith(".txt"): continue
    lang = f[:-4]; d = {}
    for ln in open(os.path.join(ROOT, "tools", "i18n", f), encoding="utf-8").read().splitlines():
        if not ln.strip(): continue
        k, _, v = ln.partition("|"); d[k] = v.replace("⏎", "\n")
    miss = [k for k in CES if k not in d]; extra = [k for k in d if k not in CES]
    badph = [k for k in d if k in CES and ph(d[k]) != ph(CES[k])]
    if miss or extra or badph:
        ok = False; print(lang, "FALTAN", miss[:8], "SOBRAN", extra[:8], "PLACEHOLDERS", badph[:8])
    json.dump({k: d[k] for k in CES if k in d}, open(os.path.join(ROOT, "i18n", lang + ".json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(lang, len(d), "ok" if not (miss or extra or badph) else "CON ERRORES")
sys.exit(0 if ok else 1)
