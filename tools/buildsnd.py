"""Genera web/snd/*.json: instrumentos reales muestreados, recortados y comprimidos (mp3 mono en base64).

Fuentes (licencias libres):
  - FluidR3_GM (Frank Wen) vía gleitz/midi-js-soundfonts — CC BY 3.0
  - VCSL, Versilian Community Sample Library (Sam Gossner) vía danigb/samples — CC0
  - Roland TR-808 sample set, Michael Fischer (1994) — gratuito
Uso:  python tools/buildsnd.py   (desde web/)   (necesita ffmpeg en el PATH)
"""
import base64, json, os, re, shutil, subprocess, sys, tempfile, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "snd")
CACHE = os.path.join(os.path.dirname(ROOT), ".sndcache")  # fuera del repo
FF = shutil.which("ffmpeg") or sys.exit("falta ffmpeg")
os.makedirs(OUT, exist_ok=True); os.makedirs(CACHE, exist_ok=True)

def get(url):
    key = re.sub(r"[^A-Za-z0-9._-]", "_", url)[-180:]
    p = os.path.join(CACHE, key)
    if not os.path.exists(p):
        q = urllib.parse.quote(url, safe=":/?=&")
        with urllib.request.urlopen(q, timeout=60) as r, open(p, "wb") as f: f.write(r.read())
    return open(p, "rb").read()

def enc(raw, ext, dur, fade=0.25, rate=32000, br="48k", hp=None):
    """recorta silencio inicial, limita duración con fundido, mono mp3"""
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "in." + ext); dst = os.path.join(td, "out.mp3")
        open(src, "wb").write(raw)
        af = ["silenceremove=start_periods=1:start_threshold=-55dB:start_silence=0.002"]
        if hp: af.append(f"highpass=f={hp}")
        af.append(f"atrim=0:{dur}")
        af.append(f"afade=t=out:st={max(0.01, dur - fade)}:d={fade}")
        cmd = [FF, "-v", "error", "-y", "-i", src, "-af", ",".join(af), "-ac", "1", "-ar", str(rate), "-b:a", br, dst]
        subprocess.run(cmd, check=True)
        return base64.b64encode(open(dst, "rb").read()).decode()

# ---------- instrumentos melódicos (FluidR3 GM) ----------
NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
def nn(m): return f"{NAMES[m % 12]}{m // 12 - 1}"

MEL = {  # clave: (archivo GM, nota baja, nota alta, duración s, fundido s)
    "piano":     ("acoustic_grand_piano", 33, 96, 3.2, .5),
    "epiano":    ("electric_piano_1", 36, 84, 2.6, .4),
    "synth":     ("lead_2_sawtooth", 36, 84, 2.0, .2),
    "strings":   ("string_ensemble_1", 33, 96, 3.4, .5),
    "violin":    ("violin", 55, 96, 3.0, .4),
    "cello":     ("cello", 36, 72, 3.0, .4),
    "contrabass":("contrabass", 28, 55, 2.6, .4),
    "timpani":   ("timpani", 36, 60, 2.6, .6),
    "nylon":     ("acoustic_guitar_nylon", 40, 96, 2.4, .4),
    "steel":     ("acoustic_guitar_steel", 40, 84, 2.4, .4),
    "eguitar":   ("electric_guitar_clean", 40, 84, 2.2, .4),
    "drive":     ("overdriven_guitar", 40, 79, 2.0, .3),
    "bass":      ("electric_bass_finger", 28, 55, 1.8, .3),
    "upright":   ("acoustic_bass", 28, 55, 1.8, .3),
    "synbass":   ("synth_bass_1", 24, 55, 1.6, .3),
    "glock":     ("glockenspiel", 72, 108, 2.0, .5),
    "xylo":      ("xylophone", 60, 96, 1.2, .3),
    "marimba":   ("marimba", 48, 84, 1.5, .4),
    "accordion": ("accordion", 48, 84, 2.4, .3),
    "brass":     ("brass_section", 48, 84, 2.0, .3),
}
GM = "https://gleitz.github.io/midi-js-soundfonts/FluidR3_GM/{}-mp3.js"

def build_mel(key):
    gm, lo, hi, dur, fade = MEL[key]
    js = get(GM.format(gm)).decode("utf-8", "ignore")
    data = dict(re.findall(r'"([A-G]b?\d)":\s*"data:audio/mp3;base64,([^"]+)"', js))
    notes = {}
    for m in range(lo, hi + 1, 3):
        b = data.get(nn(m))
        if not b: continue
        e = enc(base64.b64decode(b), "mp3", dur, fade)
        if len(base64.b64decode(e)) > 2000: notes[str(m)] = e  # descarta notas mudas
    obj = {"kind": "mel", "src": "FluidR3_GM " + gm + " (CC BY 3.0)", "notes": notes}
    json.dump(obj, open(os.path.join(OUT, key + ".json"), "w"), separators=(",", ":"))
    return key, len(notes)

# ---------- batería y percusión acústica (VCSL, CC0) ----------
VB = "https://danigb.github.io/samples/vcsl/"
VC = {  # pieza: (ruta de la muestra sin extensión, duración, fundido, highpass)
    "kick":    ("Struck Membranophones/Bass Drum 1/BDrumNew_hit_v6_rr1_Sum", .45, .2, 30),
    "bdorch":  ("Struck Membranophones/Bass Drum 2/bassdrum_hit_f", 2.5, .8, None),
    "snare":   ("Struck Membranophones/Snare Drum, Modern 1/Snare2_HitSN_v8_rr1_Mid", .5, .2, 80),
    "snare2":  ("Struck Membranophones/Snare Drum, Modern 1/Snare2_HitSN_v8_rr2_Mid", .5, .2, 80),
    "ghost":   ("Struck Membranophones/Snare Drum, Modern 1/Snare2_HitSN_v3_rr1_Mid", .3, .15, 80),
    "rim":     ("Struck Membranophones/Snare Drum, Modern 1/Snare2_stick_v1_rr1_Mid", .25, .1, 100),
    "roll":    ("Struck Membranophones/Snare Drum, Modern 1/Snare2_rollSN_v5_rr1_Mid", 2.0, .4, 80),
    "hat":     ("Struck Idiophones/Hi-Hat Cymbal/HiHat_HitC_v3_rr1_Mid", .25, .12, 300),
    "hat2":    ("Struck Idiophones/Hi-Hat Cymbal/HiHat_HitC_v3_rr2_Mid", .25, .12, 300),
    "ohat":    ("Struck Idiophones/Hi-Hat Cymbal/HiHat_HitO_rr1_Mid", 1.0, .4, 300),
    "phat":    ("Struck Idiophones/Hi-Hat Cymbal/HiHat_Close_rr1_Mid", .25, .1, 300),
    "tomHi":   ("Struck Membranophones/Tom 1/Stick/TomH_HitS_v4_rr1_Mid", .9, .35, 50),
    "tomLo":   ("Struck Membranophones/Tom 2/Stick/TomL_HitS_v4_rr1_Mid", 1.1, .4, 40),
    "crash":   ("Struck Idiophones/Suspended Cymbal 1/susCymb1_hit_f1", 2.6, 1.0, 200),
    "ride":    ("Struck Idiophones/Suspended Cymbal 1/susCymb1_hit_pp1", 1.4, .6, 200),
    "bell":    ("Struck Idiophones/Suspended Cymbal 1/susCymb1_hit_bell_mf1", 1.2, .5, 300),
    "clash":   ("Struck Idiophones/Clash Cymbals 1/cymbal_crash1_ff2", 2.6, 1.0, 150),
    "clap":    ("Struck Idiophones/Claps/Clap_rr1", .45, .15, 150),
    "clap2":   ("Struck Idiophones/Claps/Clap_rr2", .45, .15, 150),
    "bongoHi": ("Struck Membranophones/Bongos/BongoH_Hit1_v3_rr1_Mid", .45, .15, 120),
    "bongoHi2":("Struck Membranophones/Bongos/BongoH_Hit1_v2_rr2_Mid", .45, .15, 120),
    "bongoLo": ("Struck Membranophones/Bongos/BongoL_Hit1_v3_rr1_Mid", .55, .2, 90),
    "bongoSlap":("Struck Membranophones/Bongos/BongoH_HitMuted1_v3_rr1_Mid", .3, .1, 150),
    "congaHi": ("Struck Membranophones/Conga/Quinto_HitN_v3_rr1_Sum", .6, .2, 80),
    "conga":   ("Struck Membranophones/Conga/Conga_HitN_v3_rr1_Sum", .7, .25, 70),
    "congaLo": ("Struck Membranophones/Conga/Tumba_HitN_v4_rr1_Sum", .8, .3, 50),
    "congaSlap":("Struck Membranophones/Conga/Conga_HitFM_v2_rr1_Sum", .35, .12, 100),
    "claves":  ("Struck Idiophones/Claves/Claves1_Hit_v3_rr1_Mid", .35, .12, 300),
    "cowbell": ("Struck Idiophones/Cowbells/Cowbell1_Normal_v3_rr1_Mid", .5, .2, 200),
    "cowMute": ("Struck Idiophones/Cowbells/Cowbell1_Muted_v3_rr1_Mid", .25, .1, 200),
    "agogoHi": ("Struck Idiophones/Agogo Bells/Agogo_High_v3_rr1_Mid", .6, .25, 300),
    "agogoLo": ("Struck Idiophones/Agogo Bells/Agogo_Low_v1_rr1_Mid", .6, .25, 300),
    "guiro":   ("Struck Idiophones/Guiro/Guiro_Hit_rr1_Mid", .35, .1, 200),
    "guiroLong":("Struck Idiophones/Guiro/Guiro_Med_rr1_Mid", .7, .15, 200),
    "shaker":  ("Struck Idiophones/Shaker, Small/Mid_Shaker_Slap_rr1", .25, .1, 400),
    "shaker2": ("Struck Idiophones/Shaker, Small/Mid_Shaker_Slap_rr2", .25, .1, 400),
    "tamb":    ("Struck Idiophones/Tambourine 1/Tamb1_Hit_v2_rr1_Mid", .6, .25, 300),
    "tambShake":("Struck Idiophones/Tambourine 1/Tamb1_Shake_rr1_Mid", .6, .2, 300),
    "cabasa":  ("Struck Idiophones/Cabasa/Cabasa1_Hit_rr1_Mid", .3, .1, 400),
    "wood":    ("Struck Idiophones/Woodblock/wood_click_f_rr1", .3, .1, 200),
    "triangle":("Struck Idiophones/Triangles/Triangle1_Hit_v2_rr1_Mid", 2.0, .8, 500),
    "gong":    ("Struck Idiophones/Gong 1/gong_f", 4.0, 1.5, None),
    "ratchet": ("Struck Idiophones/Ratchet/Ratchet1_Fast_rr1_Mid", .8, .2, 200),
    "cajon":   ("Struck Idiophones/Cajon/Cajon_hit1_f_rr1", .5, .2, 40),
    "cajonHi": ("Struck Idiophones/Cajon/Cajon_hit2_f_rr1", .35, .12, 100),
}
VIDX = None
def vresolve(path):
    """si la muestra pedida no existe, elige la más parecida (misma articulación, velocidad cercana)"""
    global VIDX
    if VIDX is None:
        VIDX = {x["name"]: x["websfzUrl"] for x in json.loads(get("https://raw.githubusercontent.com/danigb/samples/main/audio/vcsl/instruments.json"))}
    cat, inst, rel = path.split("/", 2)
    d = json.loads(get(VIDX[inst]))
    samples = sorted({r["sample"] for g in d["groups"] for r in g["regions"]})
    want = inst + "/" + rel
    if want in samples: return cat + "/" + want
    base = re.sub(r"_v\d+.*$", "", want)
    cand = [x for x in samples if x.startswith(base)] or [x for x in samples if x.startswith(want.rsplit("_", 1)[0])]
    if not cand: raise SystemExit("sin muestra para " + path + " · hay: " + ", ".join(samples[:12]))
    vw = int((re.search(r"_v(\d+)", want) or [0, 5])[1])
    cand.sort(key=lambda x: (abs(int((re.search(r"_v(\d+)", x) or [0, vw])[1]) - vw), x))
    return cat + "/" + cand[0]

def build_vcsl():
    def one(item):
        k, (path, dur, fade, hp) = item
        raw = get(VB + vresolve(path) + ".ogg")
        return k, enc(raw, "ogg", dur, fade, rate=44100, br="64k", hp=hp)
    with ThreadPoolExecutor(8) as ex: hits = dict(ex.map(one, VC.items()))
    json.dump({"kind": "kit", "src": "VCSL (CC0)", "hits": hits}, open(os.path.join(OUT, "kit.json"), "w"), separators=(",", ":"))
    return "kit", len(hits)

# ---------- caja de ritmos Roland TR-808 ----------
DM = "https://danigb.github.io/samples/drum-machines/TR-808/"
def build_808():
    names = json.loads(get(DM + "dm.json"))["samples"]
    def pick(prefix, pref):
        c = [n for n in names if n.split("/")[-1].startswith(prefix)]
        for p in pref:
            for n in c:
                if n.endswith(p): return n
        return c[len(c) // 2] if c else None
    want = {"kick": ("bd", ["bd2575", "bd2550", "bd5050"]), "kickShort": ("bd", ["bd5010", "bd5025"]),
            "snare": ("sd", ["sd5050", "sd2550", "sd0050"]), "hat": ("ch", ["ch"]), "ohat": ("oh", ["oh25", "oh50"]),
            "clap": ("cp", ["cp"]), "cowbell": ("cb", ["cb"]), "crash": ("cy", ["cy5050", "cy2550"]),
            "tomHi": ("ht", ["ht50", "ht25"]), "tomMid": ("mt", ["mt50", "mt25"]), "tomLo": ("lt", ["lt50", "lt25"]),
            "shaker": ("ma", ["ma"]), "claves": ("cl", ["cl"]), "rim": ("rs", ["rs"]),
            "congaHi": ("hc", ["hc50"]), "conga": ("mc", ["mc50"]), "congaLo": ("lc", ["lc50"])}
    def one(item):
        k, (pre, pref) = item
        n = pick(pre, pref)
        if not n: return k, None
        raw = get(DM + n + ".ogg")
        long = k in ("kick", "crash", "ohat")
        return k, enc(raw, "ogg", 1.6 if long else .7, .3, rate=44100, br="64k")
    with ThreadPoolExecutor(8) as ex: hits = {k: v for k, v in ex.map(one, want.items()) if v}
    json.dump({"kind": "kit", "src": "Roland TR-808 samples, Michael Fischer (free)", "hits": hits}, open(os.path.join(OUT, "kit808.json"), "w"), separators=(",", ":"))
    return "kit808", len(hits)

if __name__ == "__main__":
    only = sys.argv[1:]
    jobs = [k for k in MEL if not only or k in only]
    with ThreadPoolExecutor(6) as ex:
        for k, n in ex.map(build_mel, jobs): print("mel", k, n, "notas")
    if not only or "kit" in only: print(*build_vcsl())
    if not only or "kit808" in only: print(*build_808())
    tot = 0
    for f in sorted(os.listdir(OUT)):
        s = os.path.getsize(os.path.join(OUT, f)); tot += s; print(f"{f:18s} {s/1024:8.0f} KB")
    print(f"TOTAL {tot/1024/1024:.2f} MB")
