#!/usr/bin/env python3
"""Anpassar koncerngeneratorns utdata (Ohan-entreprenad/koncern) till en ideell förening.

Kör: python3 themes/v12/postprocess.py <generatorns utmapp> docs/v12

Gör följande med generatorns sajt:
- tar bort koncerninnehåll som inte passar en förening (investerare, pressrum, lediga jobb, språkval, sök)
- föreningens logga i sidhuvud och sidfot, nyttig topprad (telefon, e-post, Instagram)
- toppbilden: bildspelets bilder ligger ovanpå varandra (generatorn staplade dem, så heron blev vit efter
  första bildbytet) och texten med Bli medlem-knappen ligger fast medan bilderna tonar över
- Bli medlem: egen sida med formulär, medlemsband med formulär på startsidan, knapp i sidhuvudet på alla bredder
- Kontakt: egen sida med formulär, formulär på startsidan och på Om oss
- egna titlar och metabeskrivningar per sida, integritetspolicy
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
BANK = src.parent / "koncern" / "bildbank"
C = json.loads((REPO / "content/content.json").read_text())
M = json.loads((REPO / "docs/media/manifest.json").read_text())
O = C["org"]
E = lambda s: html.escape(s, quote=True)

if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)
shutil.copy(REPO / "docs/media/logo-ljus.png", dst / "img/logo.png")
(dst / "paket.json").unlink(missing_ok=True)
(dst / "investerare.html").unlink(missing_ok=True)


def bild(namn):
    """Ser till att bilden finns i img/ (generatorn kopierar bara de bilder den själv använder)."""
    for suf in ("", "-s"):
        mal = dst / "img" / f"{namn}{suf}.jpg"
        if not mal.exists() and (BANK / mal.name).exists():
            shutil.copy(BANK / mal.name, mal)
    return (f'<img src="img/{namn}.jpg" srcset="img/{namn}-s.jpg 700w, img/{namn}.jpg 1600w" sizes="100vw" '
            f'alt="{E(M[namn]["alt"])}"')


# ------------------------------------------------------------------------------------------------ texter
JUNK = ["Language/Språk", "Visselblåsarfunktion", "LinkedIn", "English", "Pressrum", "Nyheter och press", "Rapporter",
        "Till bolagets webbplats", "Investerare"]
anchor = lambda lab: re.compile(r'<a\b[^>]*>(?:(?!</a>).)*?' + re.escape(lab) + r'(?:(?!</a>).)*?</a>', re.S)

TEXT = [
    ("Uppsala Crew-koncernen", "Uppsala Crew IF"),
    ("Uppsala Crew är en koncern med 3 bolag som tillsammans täcker hela kedjan.", "Tre platser i Uppsala där vi tränar och tävlar, inomhus, utomhus och i backen."),
    ("Våra bolag", "Platser"), ("Vår verksamhet", "Sporter"), ("Jobba hos oss", "Engagera dig"),
    ("Se lediga jobb", "Se uppdragen"), ("Lediga jobb", "Engagera dig"), ("Just nu söker vi", "Här behöver vi dig"),
    ("Hittar du inget som passar? Skicka en spontanansökan till något av våra bolag.", "Vill du hjälpa till på annat sätt? Skriv till oss så hittar vi en uppgift som passar."),
    ("Aktuellt från koncernen", "Aktuellt i föreningen"), ("Pågående och färdiga projekt", "Träning och tävlingar"),
    ("Se alla projekt", "Alla aktiviteter"), ("Alla projekt", "Alla aktiviteter"), (">Projekt<", ">Aktiviteter<"),
    ("Läs om vårt hållbarhetsarbete", "Läs om vårt ansvar"), (">Hållbarhet<", ">Vårt ansvar<"),
    ("Upptäck vår verksamhet", "Upptäck våra sporter"), ("Läs om vår verksamhet", "Läs om våra sporter"),
    ("Alla nyckeltal", "Mer om föreningen"), (">Koncernen<", ">Föreningen<"), ("Huvudkontor", "Postadress"),
    ("Integritets- och cookiepolicy", "Integritetspolicy"), ("Om Uppsala Crew", "Om föreningen"),
    ("koncernen", "föreningen"), ("Koncernen", "Föreningen"),
]

META = {
    "index.html": ("Uppsala Crew IF – skateboard, snowboard och freeski i Uppsala",
                   "Uppsala Crew IF är Uppsalas ideella förening för skateboard, snowboard och freeski. Skateskola, tävlingar och åkning på Allis, KAP-rampen och i Sunnerstabacken. Bli medlem för 50–100 kr per år."),
    "verksamhet.html": ("Sporter – Uppsala Crew IF", "Skateboard, snowboard, freeski och skateskola med Uppsala Crew IF i Uppsala."),
    "bolag.html": ("Platser – Uppsala Crew IF", "Här åker vi: Sunnerstabacken, Allis Uppsala och KAP-rampen i Uppsala."),
    "projekt.html": ("Aktiviteter – Uppsala Crew IF", "Träning och tävlingar med Uppsala Crew IF: Miniramp Madness, Uppsala Rail Jam, skateskola och coachning i funparken."),
    "hallbarhet.html": ("Vårt ansvar – Uppsala Crew IF", "Idrott för alla, oavsett plånbok: låg medlemsavgift, barn och vuxna på samma ramp och egen tjejklass på våra tävlingar."),
    "karriar.html": ("Engagera dig – Uppsala Crew IF", "Bli instruktör, funktionär eller hjälp till i styrelsen. Uppsala Crew IF drivs helt ideellt."),
    "om-oss.html": ("Om föreningen – Uppsala Crew IF", "Uppsala Crew IF bildades 2022 och arbetar för skateboard, snowboard och freeski i Uppsala."),
    "bli-medlem.html": ("Bli medlem – Uppsala Crew IF", "Bli medlem i Uppsala Crew IF för 50–100 kr per år. Fritt tillträde till evenemang och olycksfallsförsäkring på föreningens aktiviteter."),
    "kontakt.html": ("Kontakt – Uppsala Crew IF", f"Kontakta Uppsala Crew IF på {O['email']} eller {O['phone']}, eller skicka ett meddelande via formuläret."),
    "integritetspolicy.html": ("Integritetspolicy – Uppsala Crew IF", "Så hanterar Uppsala Crew IF dina personuppgifter enligt GDPR."),
}

# ------------------------------------------------------------------------------------------------ komponenter
CHECK = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" '
         'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
FORMNOT = f'<p class="uc-not">Formuläret öppnar ett färdigskrivet mejl till {O["email"]}. Inga uppgifter sparas på webbplatsen.</p>'
SAMTYCKE = ('<label class="uc-check"><input type="checkbox" required><span>Jag godkänner att föreningen sparar mina uppgifter '
            'enligt <a href="integritetspolicy.html">integritetspolicyn</a>.</span></label>')


def medlemsform():
    avg = "".join(f'<label><input type="radio" name="avgift" value="{v}"><span>{v}</span></label>' for v in ("50 kr", "75 kr", "100 kr"))
    return f"""<form class="uc-form" data-mail="{O['email']}" data-subject="Medlemsansökan Uppsala Crew IF" action="mailto:{O['email']}" method="post" enctype="text/plain">
<h3>Medlemsansökan</h3><p class="uc-form-intro">Fyll i namn och e-post så mejlar vi instruktioner för betalning.</p>
<div class="uc-rad"><div class="uc-falt"><label for="m-namn">Namn</label><input id="m-namn" name="namn" data-label="Namn" autocomplete="name" required></div>
<div class="uc-falt"><label for="m-epost">E-post</label><input id="m-epost" name="epost" type="email" data-label="E-post" autocomplete="email" required></div></div>
<div class="uc-falt"><label for="m-sport">Vad åker du? <span class="uc-valfri">Valfritt</span></label><select id="m-sport" name="sport" data-label="Sport"><option value="">Välj</option><option>Skateboard</option><option>Snowboard</option><option>Freeski</option><option>Flera av dem</option><option>Vill börja</option></select></div>
<fieldset class="uc-belopp" data-label="Medlemsavgift"><legend>Medlemsavgift per år</legend><div>{avg}</div><p class="uc-hint">Välj det du har råd med.</p></fieldset>
{SAMTYCKE}
<button class="knapp knapp-primar" type="submit">Skicka medlemsansökan</button>
<p class="uc-status" role="status" aria-live="polite"></p>{FORMNOT}</form>"""


def kontaktform():
    amnen = "".join(f"<option>{a}</option>" for a in ("Medlemskap", "Skateskola", "Tävlingar", "Engagera mig", "Samarbete och sponsring", "Annat"))
    return f"""<form class="uc-form" data-mail="{O['email']}" data-subject="Meddelande via uppsalacrew.se" action="mailto:{O['email']}" method="post" enctype="text/plain">
<h3>Skicka ett meddelande</h3>
<div class="uc-rad"><div class="uc-falt"><label for="k-namn">Namn</label><input id="k-namn" name="namn" data-label="Namn" autocomplete="name" required></div>
<div class="uc-falt"><label for="k-epost">E-post</label><input id="k-epost" name="epost" type="email" data-label="E-post" autocomplete="email" required></div></div>
<div class="uc-falt"><label for="k-arende">Ärende</label><select id="k-arende" name="arende" data-label="Ärende" data-amne>{amnen}</select></div>
<div class="uc-falt"><label for="k-meddelande">Meddelande</label><textarea id="k-meddelande" name="meddelande" data-label="Meddelande" rows="5" required></textarea></div>
{SAMTYCKE}
<button class="knapp knapp-primar" type="submit">Skicka meddelande</button>
<p class="uc-status" role="status" aria-live="polite"></p>{FORMNOT}</form>"""


def formaner():
    return "".join(f"<li>{CHECK}<span>{E(b)}</span></li>" for b in C["membership"]["benefits"])


def medlem_sektion():
    return f"""<section class="sek pa-farg uc-medlem" id="bli-medlem" aria-labelledby="bm-h"><div class="wrap uc-split">
<div class="uc-text"><span class="etikett">Medlemskap</span><h2 id="bm-h">Bli medlem på en minut</h2>
<p class="uc-pris">50–100 kr<small>per år</small></p><p class="uc-ingress">{E(C['membership']['price_note'])}</p>
<ul class="uc-lista">{formaner()}</ul></div>
<div>{medlemsform()}</div></div></section>"""


def kontakt_sektion(cls="pa-yta", full=False, rubrik="Frågor? Skriv till oss"):
    extra = (f"<div><dt>Org.nr</dt><dd>{O['orgnr']}</dd></div>"
             f'<div><dt>Facebook</dt><dd><a href="{O["facebook"]}" rel="noopener">Uppsala Crew IF</a></dd></div>') if full else ""
    return f"""<section class="sek {cls} uc-kontakt" id="kontakt" aria-labelledby="ko-h"><div class="wrap uc-split">
<div class="uc-text"><span class="etikett">Kontakt</span><h2 id="ko-h">{E(rubrik)}</h2>
<p class="uc-ingress">Om träning, medlemskap, tävlingar eller samarbete. Fyll i formuläret eller hör av dig direkt.</p>
<dl class="uc-info"><div><dt>E-post</dt><dd><a href="mailto:{O['email']}">{O['email']}</a></dd></div>
<div><dt>Telefon</dt><dd><a href="tel:{O['phone_href']}">{O['phone']}</a></dd></div>
<div><dt>Postadress</dt><dd>{O['street']}, {O['zip']} {O['city']}</dd></div>
<div><dt>Instagram</dt><dd><a href="{O['instagram']}" rel="noopener">{O['instagram_handle']}</a></dd></div>{extra}</dl></div>
<div>{kontaktform()}</div></div></section>"""


def sidhero(h1, ingress, bildnamn, smula):
    return f"""<section class="sidhero" aria-labelledby="h1"><div class="bild-fyll">{bild(bildnamn)} fetchpriority=high decoding="async"></div>
<div class="wrap"><nav class="brodsmula" aria-label="Brödsmulor"><a href="index.html">Start</a> / <span aria-current="page">{E(smula)}</span></nav><h1 id="h1">{E(h1)}</h1><p class="ingress">{E(ingress)}</p></div></section>"""


# ------------------------------------------------------------------------------------------------ hjälpare
def div_slut(s, start):
    """Index direkt efter den </div> som stänger <div> som börjar vid start."""
    djup, i = 0, start
    for m in re.finditer(r"<div\b|</div>", s[start:]):
        djup += 1 if m.group() == "<div" else -1
        if djup == 0:
            return start + m.end()
    raise ValueError("div utan slut")


def statisk_herotext(s):
    """Lyfter ut första bildens text ur bildspelet så att den ligger fast över alla bilder och tar bort de andras."""
    block, pos = [], 0
    while (i := s.find('<div class="slide-text hero-txt">', pos)) != -1:
        j = div_slut(s, i)
        block.append(s[i:j])
        s = s[:i] + s[j:]
        pos = i
    if block:
        s = s.replace('<div class="spel-kontroll">', block[0] + '<div class="spel-kontroll">', 1)
    return s


def fix(s, name):
    s = re.sub(r'<span class="(figtext|foto-not)">Illustrationsbild</span>', "", s)
    s = re.sub(r'<span class="fpa-status">[^<]*</span>', "", s)
    for lab in JUNK:
        s = anchor(lab).sub("", s)
    s = re.sub(r'<a href="#" aria-label="Sök">(?:(?!</a>).)*?</a>', "", s, flags=re.S)
    s = re.sub(r'<a href="#" lang="?en"?>(?:(?!</a>).)*?</a>', "", s, flags=re.S)
    s = re.sub(r'<(a|button)\b[^>]*>(?:(?!</\1>).)*?<span>Sök</span>(?:(?!</\1>).)*?</\1>', "", s, flags=re.S)
    s = re.sub(r"<li>\s*</li>", "", s)
    s = s.replace("<small>04</small><b>Kontakta oss", "<small>03</small><b>Kontakta oss")
    # Topprad med något användbart
    s = re.sub(r'<div class="topprad"><div class="wrap">.*?</div></div>',
               f'<div class="topprad"><div class="wrap"><a href="tel:{O["phone_href"]}">{O["phone"]}</a>'
               f'<a class="t-dold" href="mailto:{O["email"]}">{O["email"]}</a><a href="{O["instagram"]}" rel="noopener">Instagram</a></div></div>',
               s, count=1, flags=re.S)
    # Logga
    s = s.replace('<span class="ord">Uppsala Crew</span>', '<img class="logo-bild" src="img/logo.png" width="52" height="52" alt=""><span class="ord">Uppsala Crew</span>')
    s = s.replace('<p class="fot-namn">Uppsala Crew</p>', '<p class="fot-namn"><img src="img/logo.png" width="64" height="64" alt="Uppsala Crew IF logotyp" loading="lazy">Uppsala Crew IF</p>')
    # Sidhuvud: Bli medlem-knapp och Kontakt i menyn
    s = s.replace('<a class="knapp knapp-primar head-kontakt" href="om-oss.html#kontakt">Kontakta oss</a>',
                  '<a class="knapp knapp-primar head-kontakt" href="bli-medlem.html">Bli medlem</a>')
    s = re.sub(r'(<a href="om-oss.html"[^>]*>Om oss</a>)</nav>', r'\1<a href="kontakt.html">Kontakt</a></nav>', s, count=1)
    s = s.replace('<li><a href="om-oss.html">Om oss</a></li></ul>', '<li><a href="om-oss.html">Om oss</a></li><li><a href="kontakt.html">Kontakt</a></li><li><a href="bli-medlem.html">Bli medlem</a></li></ul>', 1)
    s = s.replace('<h4>Genvägar</h4><ul>', '<h4>Genvägar</h4><ul><li><a href="bli-medlem.html">Bli medlem</a></li>')
    # Toppbild: högupplösta bilder, fast text, Bli medlem
    for old, new in (("freeski-hopp", "snowboard-hopp"), ("tjejer-skate", "allis-hall-1"), ("instruktorer", "freeski-hopp")):
        s = re.sub(r'(<div class="bild-slide[^"]*"><div class="bild-fyll">)<img src="img/' + old + r'\.jpg" srcset="[^"]*" sizes="100vw" alt="[^"]*"',
                   lambda m: m.group(1) + bild(new), s, count=1)
    s = s.replace("<h1>Vi bygger Uppsalas skate- och snowscen</h1>", "<h1>Vi bygger Uppsalas <br>skate- och snowscen</h1>")
    s = re.sub(r'(<h1>(?:[^<]|<br>)*</h1>)<a class="textlank" href="verksamhet.html">(?:(?!</a>).)*?</a>',
               lambda m: m.group(1) + '<p class="ingress hero-ingress">Ideell förening för skateboard, snowboard och freeski i Uppsala sedan 2022.</p>'
               '<div class="knappar hero-knappar"><a class="knapp knapp-primar" href="bli-medlem.html">Bli medlem</a><a class="knapp knapp-ljus" href="verksamhet.html">Våra sporter</a></div>',
               s, count=1, flags=re.S)
    if 'class="hero hero-band"' in s:
        s = statisk_herotext(s)
    for a, b in TEXT:
        s = s.replace(a, b)
    # Länkar: allt som heter Bli medlem går till medlemssidan, resten av kontaktlänkarna till kontaktsidan
    s = re.sub(r'<a\b([^>]*?)href="[^"]*"([^>]*)>((?:(?!</a>).)*?Bli medlem(?:(?!</a>).)*?</a>)',
               lambda m: f'<a{m.group(1)}href="bli-medlem.html"{m.group(2)}>{m.group(3)}', s, flags=re.S)
    s = s.replace('href="om-oss.html#kontakt"', 'href="kontakt.html"')
    s = s.replace('href="investerare.html', 'href="om-oss.html').replace('href="om-oss.html#press"', 'href="om-oss.html"')
    s = s.replace('href="#">Integritets', 'href="integritetspolicy.html">Integritets')
    if name == "karriar.html":
        s = s.replace('href="#"', 'href="kontakt.html?arende=Engagera%20mig"')
        s = s.replace('href="kontakt.html"', 'href="kontakt.html?arende=Engagera%20mig"')
    s = s.replace('href="#"', 'href="projekt.html"' if name == "projekt.html" else 'href="om-oss.html"')
    # Startsidan: medlemsband efter Vårt ansvar, kontaktformulär före genvägarna
    if name == "index.html":
        s = s.replace('<section class="sek " aria-labelledby="fpa-h">', medlem_sektion() + '<section class="sek " aria-labelledby="fpa-h">', 1)
        s = s.replace('<section class="hsf "', kontakt_sektion() + '<section class="hsf "', 1)
    if name == "om-oss.html":
        s = re.sub(r'<div id="press">.*?</section></div>', "", s, count=1, flags=re.S)
        s = re.sub(r'<section class="sek pa-ton" id="kontakt">.*?</section>', lambda m: kontakt_sektion("pa-ton", full=True), s, count=1, flags=re.S)
    if 'name="robots"' not in s:
        s = s.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"', 1)
    return s


def satt_meta(s, name):
    if name not in META:
        return s
    t, d = (E(x) for x in META[name])
    s = re.sub(r"<title>[^<]*</title>", f"<title>{t}</title>", s, count=1)
    s = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{d}">', s, count=1)
    s = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{t}">', s, count=1)
    s = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{d}">', s, count=1)
    return s


CSS = """<style>
/* Logga */
.logga{display:inline-flex;align-items:center;gap:12px}
.logga .logo-bild{width:52px;height:52px;flex:none;border-radius:50%}
@media(max-width:700px){.logga .logo-bild{width:42px;height:42px}}
@media(max-width:479px){.logga .ord,.logga .tag{display:none!important}}
.fot-namn{display:flex;align-items:center;gap:14px}
.fot-namn img{width:64px;height:64px;border-radius:50%;background:#fff}
/* Bli medlem-knappen syns i sidhuvudet på alla bredder */
.head-kontakt{display:inline-flex!important}
@media(max-width:599px){.head-kontakt{min-height:40px!important;padding:8px 16px!important;font-size:13.5px!important}}
/* Toppbild: bilderna ligger ovanpå varandra, texten ligger fast */
.hero-band .band-bild{min-height:max(620px,78svh)!important}
.hero-band .bild-slide{position:absolute!important;inset:0!important;height:100%!important}
.hero-band .bild-slide .bild-fyll::after{background:linear-gradient(0deg,rgba(6,18,32,.78),rgba(6,18,32,.15) 55%,rgba(6,18,32,.05))!important}
.hero-band .slide-text{position:absolute!important;z-index:3!important;display:block!important;text-align:left!important;padding:0!important;top:auto!important;right:auto!important;
  bottom:clamp(56px,9vh,110px)!important;left:max(clamp(24px,5vw,80px),calc((100% - 1240px) / 2))!important;width:min(860px,calc(100% - 48px))!important;max-width:none!important}
.hero-band .slide-text>*{margin-left:0!important;margin-right:0!important}
.hero-band .slide-text h1{color:#fff;max-width:none!important;width:auto!important;font-size:clamp(36px,min(4.4vw,8.5vh),68px)!important;line-height:1.02!important}
.hero-band .slide-text .hero-ingress{color:rgba(255,255,255,.9);font-size:clamp(16px,1.25vw,19px);line-height:1.55;margin:22px 0 0!important;max-width:52ch!important}
.hero-band .slide-text .hero-knappar{display:flex!important;flex-wrap:wrap;gap:12px;margin-top:26px!important;justify-content:flex-start!important}
.hero-band .slide-text .hero-knappar .knapp{width:auto!important;flex:0 0 auto!important;padding-inline:28px}
.hero-band .slide-text .hero-knappar .knapp-ljus{background:#fff;color:#0c2b4b}
.hero-band .spel-kontroll{z-index:4!important;top:auto!important;bottom:clamp(56px,9vh,110px)!important}
@media(max-width:700px){
  .hero-band .band-bild{min-height:max(720px,100svh)!important}
  .hero-band .slide-text{bottom:140px!important}
  .hero-band .slide-text h1{font-size:clamp(32px,9vw,44px)!important}
  .hero-band .slide-text h1 br{display:none}
  .hero-band .slide-text .hero-knappar .knapp{padding-inline:20px}
  .hero-band .spel-kontroll{top:96px!important;bottom:auto!important;right:24px!important}
}
/* Formulär och sektioner för medlemskap och kontakt */
.uc-split{display:grid;gap:clamp(32px,4vw,72px);align-items:start}
@media(min-width:960px){.uc-split{grid-template-columns:1fr 1fr}}
.uc-text h2{font-size:calc(clamp(30px,3.4vw,48px) * var(--skala-r))}
.uc-ingress{font-size:clamp(17px,1.3vw,19px);line-height:1.55;margin:16px 0 0;max-width:34em;opacity:.9}
.uc-pris{font:var(--w-siffra) clamp(48px,5.4vw,76px)/1 var(--font-r);letter-spacing:-.03em;margin:22px 0 0}
.uc-pris small{font-size:.3em;font-weight:500;letter-spacing:0;margin-left:10px;opacity:.8}
.uc-lista{list-style:none;padding:0;margin:28px 0 0;display:grid;gap:14px;max-width:34em}
.uc-lista li{display:grid;grid-template-columns:26px 1fr;gap:12px;align-items:start;line-height:1.5}
.uc-lista svg{width:22px;height:22px;color:var(--c-a);margin-top:1px}
.uc-h3{font:var(--w-r) 24px/1.2 var(--font-r);letter-spacing:var(--tr-r);margin:44px 0 0}
.uc-steg{list-style:none;padding:0;margin:20px 0 0;counter-reset:s;display:grid;gap:14px}
.uc-steg li{counter-increment:s;display:grid;grid-template-columns:40px 1fr;gap:12px;align-items:center}
.uc-steg li::before{content:counter(s);width:36px;height:36px;border-radius:50%;background:var(--c-p);color:#fff;display:grid;place-items:center;font-weight:700}
.uc-faq{margin-top:12px;border-top:1px solid var(--c-line)}
.uc-faq details{border-bottom:1px solid var(--c-line)}
.uc-faq summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:16px;padding:16px 0;font-weight:600;min-height:44px;align-items:center}
.uc-faq summary::-webkit-details-marker{display:none}
.uc-faq summary::after{content:"+";flex:none;width:30px;height:30px;border-radius:50%;background:var(--c-ton);display:grid;place-items:center;font-size:18px}
.uc-faq details[open] summary::after{content:"–"}
.uc-faq details p{margin:0 0 16px;color:var(--c-mut);max-width:40em}
.uc-info{display:grid;gap:18px;margin:32px 0 0}
@media(min-width:560px){.uc-info{grid-template-columns:1fr 1fr}}
.uc-info dt{font:600 12.5px/1.3 var(--font-t);letter-spacing:.14em;text-transform:uppercase;opacity:.7;margin-bottom:6px}
.uc-info dd{margin:0;font-size:17px;font-weight:600}
.uc-info a{color:inherit}
.uc-form{background:var(--c-bg);color:var(--c-ink);border:1px solid var(--c-line);border-radius:18px;padding:clamp(22px,3vw,40px);box-shadow:0 24px 60px rgba(8,28,49,.14)}
.uc-form h3{font:var(--w-r) clamp(24px,2vw,28px)/1.15 var(--font-r);letter-spacing:var(--tr-r);color:var(--c-rubrik);margin:0}
.uc-form-intro{margin:8px 0 0;color:var(--c-mut)}
.uc-rad{display:grid;gap:0 16px}
@media(min-width:560px){.uc-rad{grid-template-columns:1fr 1fr}}
.uc-falt{margin-top:18px}
.uc-falt label{display:flex;justify-content:space-between;gap:8px;font-weight:600;font-size:14.5px;margin-bottom:7px}
.uc-valfri{font-weight:500;color:var(--c-mut)}
.uc-falt input,.uc-falt select,.uc-falt textarea{width:100%;min-height:52px;padding:13px 15px;font:inherit;font-size:16px;color:var(--c-ink);background:#fff;border:1.5px solid var(--c-ton2);border-radius:12px;transition:border-color .15s}
.uc-falt textarea{min-height:150px;resize:vertical}
.uc-falt input:hover,.uc-falt select:hover,.uc-falt textarea:hover{border-color:#9aa6b2}
.uc-falt input:focus,.uc-falt select:focus,.uc-falt textarea:focus{outline:3px solid #2f7bdc;outline-offset:1px;border-color:var(--c-p)}
.uc-belopp{border:0;padding:0;margin:18px 0 0;min-width:0}
.uc-belopp legend{font-weight:600;font-size:14.5px;margin-bottom:8px;padding:0}
.uc-belopp div{display:flex;gap:10px}
.uc-belopp label{flex:1;position:relative}
.uc-belopp input{position:absolute;opacity:0;width:1px;height:1px}
.uc-belopp span{display:flex;align-items:center;justify-content:center;min-height:50px;border:1.5px solid var(--c-ton2);border-radius:999px;font-weight:700;cursor:pointer;transition:background .15s,color .15s,border-color .15s}
.uc-belopp span:hover{border-color:var(--c-p)}
.uc-belopp input:checked+span{background:var(--c-p);border-color:var(--c-p);color:#fff}
.uc-belopp input:focus-visible+span{outline:3px solid #2f7bdc;outline-offset:2px}
.uc-hint{margin:8px 0 0;font-size:13.5px;color:var(--c-mut)}
.uc-check{display:grid;grid-template-columns:22px 1fr;gap:10px;margin-top:20px;font-size:14px;line-height:1.5;color:var(--c-mut);cursor:pointer}
.uc-check input{width:20px;height:20px;margin:1px 0 0;accent-color:var(--c-p)}
.uc-check a{color:var(--c-p-text)}
.uc-form .knapp{width:100%;margin-top:22px;min-height:54px;font-size:16px}
.uc-status{margin:14px 0 0;font-weight:600;color:var(--c-p-text)}
.uc-status:empty{display:none}
.uc-not{margin:12px 0 0;font-size:13px;color:var(--c-mut)}
@media(min-width:960px){.uc-sticky{position:sticky;top:110px}}
@media(max-width:959px){.uc-sticky{order:-1}}
.uc-juridik .brodsmula{color:var(--c-mut)}
.uc-juridik h1{font-size:calc(clamp(34px,4vw,56px) * var(--skala-r));margin-bottom:12px}
.uc-juridik h2{font-size:24px;margin:36px 0 10px}
.uc-juridik p{max-width:44em}
</style></head>"""

FORM_JS = """(function () {
  "use strict";
  document.querySelectorAll("form[data-mail]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!f.reportValidity()) return;
      var rader = [];
      f.querySelectorAll("[data-label]").forEach(function (el) {
        var v = "";
        if (el.tagName === "FIELDSET") { var c = el.querySelector("input:checked"); v = c ? c.value : ""; }
        else { v = (el.value || "").trim(); }
        if (v) rader.push(el.getAttribute("data-label") + ": " + v);
      });
      var amne = f.getAttribute("data-subject");
      var a = f.querySelector("[data-amne]");
      if (a && a.value) amne += " – " + a.value;
      window.location.href = "mailto:" + f.getAttribute("data-mail") + "?subject=" + encodeURIComponent(amne) + "&body=" + encodeURIComponent(rader.join("\\n"));
      var s = f.querySelector(".uc-status");
      if (s) s.textContent = "Ditt e-postprogram öppnas med allt ifyllt. Skicka mejlet så är det klart. Händer inget? Mejla " + f.getAttribute("data-mail") + ".";
    });
  });
  var arende = new URLSearchParams(location.search).get("arende");
  var sel = document.getElementById("k-arende");
  if (arende && sel) { for (var i = 0; i < sel.options.length; i++) { if (sel.options[i].value === arende) sel.selectedIndex = i; } }
})();
"""
(dst / "assets/form.js").write_text(FORM_JS)

for f in dst.glob("*.html"):
    s = fix(f.read_text(), f.name).replace("</head>", CSS, 1).replace("</body>", '<script src="assets/form.js" defer></script>\n</body>', 1)
    f.write_text(satt_meta(s, f.name))

# ------------------------------------------------------------------------------------------------ nya sidor på Om oss-sidans skal
skal = re.sub(r'\saria-current=(?:"page"|page)', "", (dst / "om-oss.html").read_text())


def ny_sida(namn, main):
    s = re.sub(r'<main id="main">.*?</main>', lambda m: f'<main id="main">{main}</main>', skal, count=1, flags=re.S)
    (dst / namn).write_text(satt_meta(s, namn))


m = C["membership"]
faq = {x["q"]: x["a"] for x in C["faq"]}
fragor = "".join(f'<details><summary>{E(q)}</summary><p>{E(faq[q])}</p></details>'
                 for q in ("Vad kostar det att bli medlem?", "Vem kan bli medlem?", "Är jag försäkrad på era aktiviteter?"))
steg = "".join(f"<li>{E(x)}</li>" for x in m["steps"])
ny_sida("bli-medlem.html", sidhero("Bli medlem", f"Medlemsavgiften är {m['price']}. {m['price_note']}", "skateskola-grupp", "Bli medlem") + f"""
<section class="sek"><div class="wrap uc-split">
<div class="uc-text"><span class="etikett">Det här ingår</span><h2>Därför ska du bli medlem</h2><ul class="uc-lista">{formaner()}</ul>
<h3 class="uc-h3">Så går det till</h3><ol class="uc-steg">{steg}</ol>
<h3 class="uc-h3">Vanliga frågor</h3><div class="uc-faq">{fragor}</div></div>
<div class="uc-sticky">{medlemsform()}</div></div></section>""")

kontaktsida = sidhero("Kontakt", "Du når oss enklast via formuläret eller e-post. För senaste nytt om träningar och tävlingar, följ @uppsalacrew på Instagram.",
                      "allis-hall-2", "Kontakt") + kontakt_sektion("", full=True, rubrik="Hör av dig")
ny_sida("kontakt.html", kontaktsida)
k = (dst / "kontakt.html").read_text().replace('<a href="kontakt.html">Kontakt</a></nav>', '<a href="kontakt.html" aria-current="page">Kontakt</a></nav>', 1)
(dst / "kontakt.html").write_text(k)

pol = "".join(f"<h2>{E(x['h'])}</h2><p>{E(x['p'])}</p>" for x in C["privacy"])
ny_sida("integritetspolicy.html", f"""<section class="sek uc-juridik"><div class="wrap" style="max-width:860px">
<nav class="brodsmula" aria-label="Brödsmulor"><a href="index.html">Start</a> / <span aria-current="page">Integritetspolicy</span></nav>
<h1>Integritetspolicy</h1>{pol}</div></section>""")

# ------------------------------------------------------------------------------------------------ kontroll
left = {}
for f in sorted(dst.glob("*.html")):
    t = f.read_text()
    for w in ["Investerare", "koncern", "LinkedIn", "Lediga jobb", 'href="#"', "Illustrationsbild", "om-oss.html#kontakt"]:
        if w in t:
            left.setdefault(w, []).append(f.name)
    for href in re.findall(r'href="([a-z-]+\.html)', t):
        if not (dst / href).exists():
            left.setdefault("trasig länk " + href, []).append(f.name)
print("sidor:", ", ".join(sorted(p.name for p in dst.glob("*.html"))))
print("kvar:", left or "inget")
