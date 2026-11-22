#!/usr/bin/env python3
"""Anpassar koncerngeneratorns utdata (Ohan-entreprenad/koncern) till en ideell förening.
Kör: python3 themes/v12/postprocess.py <generatorns utmapp> docs/v12"""
import re, sys, shutil, json, html
from pathlib import Path

src, dst = Path(sys.argv[1]), Path(sys.argv[2])
M = json.loads((Path(__file__).resolve().parents[2] / "docs/media/manifest.json").read_text())
ALT = {k: v["alt"] for k, v in M.items()}
C = json.loads((Path(__file__).resolve().parents[2] / "content/content.json").read_text())
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)
shutil.copy(Path(__file__).resolve().parents[2] / "docs/media/logo-ljus.png", dst / "img/logo.png")
(dst / "paket.json").unlink(missing_ok=True)
(dst / "investerare.html").unlink(missing_ok=True)

JUNK = ["Language/Språk", "Visselblåsarfunktion", "LinkedIn", "English", "Pressrum", "Nyheter och press", "Rapporter",
        "Till bolagets webbplats", "Investerare"]
anchor = lambda lab: re.compile(r'<a\b[^>]*>(?:(?!</a>).)*?' + re.escape(lab) + r'(?:(?!</a>).)*?</a>', re.S)

TEXT = [
    ("Uppsala Crew-koncernen", "Uppsala Crew IF"),
    ("Uppsala Crew är en koncern med 3 bolag som tillsammans täcker hela kedjan.", "Tre platser i Uppsala där vi tränar och tävlar, inomhus, utomhus och i backen."),
    ("Våra bolag", "Platser"), ("Vår verksamhet", "Sporter"), ("Jobba hos oss", "Engagera dig"),
    ("Se lediga jobb", "Se uppdragen"), ("Lediga jobb", "Engagera dig"), ("Just nu söker vi", "Här behöver vi dig"),
    ("Hittar du inget som passar? Skicka en spontanansökan till något av våra bolag.", "Vill du hjälpa till på annat sätt? Mejla oss så hittar vi en uppgift som passar."),
    ("Aktuellt från koncernen", "Aktuellt i föreningen"), ("Pågående och färdiga projekt", "Träning och tävlingar"),
    ("Se alla projekt", "Alla aktiviteter"), ("Alla projekt", "Alla aktiviteter"), (">Projekt<", ">Aktiviteter<"),
    ("Läs om vårt hållbarhetsarbete", "Läs om vårt ansvar"), (">Hållbarhet<", ">Vårt ansvar<"),
    ("Upptäck vår verksamhet", "Upptäck våra sporter"), ("Läs om vår verksamhet", "Läs om våra sporter"),
    ("Alla nyckeltal", "Mer om föreningen"), (">Koncernen<", ">Föreningen<"), ("Huvudkontor", "Postadress"),
    ("Integritets- och cookiepolicy", "Integritetspolicy"), ("Om Uppsala Crew", "Om föreningen"),
    ("koncernen", "föreningen"), ("Koncernen", "Föreningen"),
]

def fix(s, name):
    s = re.sub(r"<span class=\"(figtext|foto-not)\">Illustrationsbild</span>", "", s)
    s = re.sub(r'<span class="fpa-status">[^<]*</span>', "", s)
    for lab in JUNK:
        s = anchor(lab).sub("", s)
    s = re.sub(r'<a href="#" aria-label="Sök">(?:(?!</a>).)*?</a>', "", s, flags=re.S)
    s = re.sub(r'<a href="#" lang="?en"?>(?:(?!</a>).)*?</a>', "", s, flags=re.S)
    s = re.sub(r'<(a|button)\b[^>]*>(?:(?!</\1>).)*?<span>Sök</span>(?:(?!</\1>).)*?</\1>', "", s, flags=re.S)
    s = re.sub(r"<li>\s*</li>", "", s)
    s = s.replace("<small>04</small><b>Kontakta oss", "<small>03</small><b>Kontakta oss")
    for old, new in (("freeski-hopp", "snowboard-hopp"), ("tjejer-skate", "skate-luft-inne"), ("instruktorer", "kvallshopp")):
        s = re.sub(r'(<div class="bild-slide[^"]*"><div class="bild-fyll"><img src="img/)' + old + r'\.jpg" srcset="img/' + old + r'-s\.jpg 700w, img/' + old + r'\.jpg 1600w"([^>]*?)alt="[^"]*"',
                   lambda m: m.group(1) + new + '.jpg" srcset="img/' + new + '-s.jpg 700w, img/' + new + '.jpg 1600w"' + m.group(2) + 'alt="' + ALT[new] + '"', s, count=1)
    s = s.replace('href="investerare.html', 'href="om-oss.html')
    s = s.replace('href="om-oss.html#press"', 'href="om-oss.html"')
    s = s.replace('href="#">Integritets', 'href="integritetspolicy.html">Integritets')
    s = s.replace('<span class="ord">Uppsala Crew</span>', '<img class="logo-bild" src="img/logo.png" width="52" height="52" alt=""><span class="ord">Uppsala Crew</span>')
    s = s.replace('<p class="fot-namn">Uppsala Crew</p>', '<p class="fot-namn"><img src="img/logo.png" width="64" height="64" alt="Uppsala Crew IF logotyp" loading="lazy">Uppsala Crew IF</p>')
    s = re.sub(r'(<h1>[^<]*</h1>)<a class="textlank" href="verksamhet.html">(?:(?!</a>).)*?</a>',
               lambda m: m.group(1) + '<p class="ingress hero-ingress">' + html.escape(C["intro"]["lead"]) + '</p><div class="knappar hero-knappar"><a class="knapp knapp-primar" href="om-oss.html#kontakt">Bli medlem</a><a class="knapp knapp-ljus" href="verksamhet.html">Våra sporter</a></div>', s, count=1, flags=re.S)
    for a, b in TEXT:
        s = s.replace(a, b)
    s = s.replace('href="#"', 'href="om-oss.html#kontakt"' if name == "karriar.html" else 'href="projekt.html"' if name == "projekt.html" else 'href="om-oss.html"')
    s = s.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"', 1) if 'name="robots"' not in s else s
    return s

EXTRA = """<style>
.logga{display:inline-flex;align-items:center;gap:12px}
.logga .logo-bild{width:52px;height:52px;flex:none;border-radius:50%}
@media(max-width:700px){.logga .logo-bild{width:42px;height:42px}}
.fot-namn{display:flex;align-items:center;gap:14px}
.fot-namn img{width:64px;height:64px;border-radius:50%;background:#fff}
.hero-band .slide-text{top:auto!important;bottom:clamp(56px,9vh,110px)!important;left:clamp(24px,5vw,80px)!important;right:auto!important;max-width:min(560px,calc(100% - 48px))!important}
.hero-band .slide-text .hero-knappar .knapp{width:auto!important;flex:0 0 auto!important;padding-inline:28px}
@media(min-width:701px){.hero-band .slide-text h1{font-size:clamp(34px,3.6vw,56px)!important}}
.hero-band .slide-text h1,.hero-band .slide-text h2{font-size:clamp(34px,4.2vw,64px)!important;line-height:1.04}
.hero-band .slide-text .hero-ingress{color:rgba(255,255,255,.88);font-size:clamp(16px,1.25vw,19px);line-height:1.55;margin:22px 0 0!important;max-width:52ch}
.hero-band .slide-text .hero-knappar{display:flex!important;flex-wrap:wrap;gap:12px;margin-top:26px;justify-content:flex-start!important;width:100%}
.hero-band .slide-text .hero-knappar .knapp-ljus{background:#fff;color:#0c2b4b}
.hero-band .bild-slide .bild-fyll::after{background:linear-gradient(0deg,rgba(6,18,32,.78),rgba(6,18,32,.15) 55%,rgba(6,18,32,.05))!important}
.hero-band .spel-kontroll{top:auto!important;bottom:clamp(56px,9vh,110px)!important}
@media(max-width:700px){.hero-band .spel-kontroll{top:96px!important;bottom:auto!important;right:24px!important}.hero-band .slide-text{bottom:40px!important}}
</style></head>"""
for f in dst.glob("*.html"):
    f.write_text(fix(f.read_text(), f.name).replace('</head>', EXTRA, 1))

# Integritetspolicy byggs på om-oss-sidans skal
om = (dst / "om-oss.html").read_text()
body = "".join(f"<h2>{html.escape(x['h'])}</h2><p>{html.escape(x['p'])}</p>" for x in C["privacy"])
main = f'<main id="main"><section class="sektion"><div class="wrap" style="max-width:760px;padding-top:9rem;padding-bottom:4rem"><h1>Integritetspolicy</h1>{body}</div></section></main>'
pol = re.sub(r'<main id="main">.*?</main>', main, om, flags=re.S)
pol = re.sub(r"<title>[^<]*</title>", "<title>Integritetspolicy – Uppsala Crew IF</title>", pol)
(dst / "integritetspolicy.html").write_text(pol)

left = {}
for f in dst.glob("*.html"):
    t = f.read_text()
    for w in ["Investerare", "bolag ", "koncern", "LinkedIn", "Lediga jobb", 'href="#"', "Illustrationsbild", "aktie"]:
        if w in t:
            left.setdefault(w, []).append(f.name)
print("kvar:", left or "inget")
