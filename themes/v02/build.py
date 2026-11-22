#!/usr/bin/env python3
"""v02 "Zine" – DIY-skejtzine för Uppsala Crew IF. Endast standardbibliotek."""
import json
import shutil
from html import escape
from pathlib import Path

V = "v02"
ROOT = Path(__file__).resolve().parents[2]
C = json.loads((ROOT / "content/content.json").read_text(encoding="utf-8"))
M = json.loads((ROOT / "docs/media/manifest.json").read_text(encoding="utf-8"))
OUT = ROOT / "docs" / V
P = f"/uppsalacrew/{V}/"
MED = "/uppsalacrew/media/"
SITE = "https://www.uppsalacrew.se"
ORG = C["org"]
TITLES = {p["slug"]: p["title"] for p in C["pages"]}
SPORTS = {s["slug"]: s for s in C["sports"]}
PLACES = {p["slug"]: p for p in C["places"]}


def e(s):
    return escape(str(s), quote=True)


def u(slug):
    return P + (slug + "/" if slug else "")


def img(name, sizes="100vw", lazy=True, cls="", alt=None):
    m = M[name]
    ws = m["widths"]
    srcset = ", ".join(f"{MED}{name}-{w}.webp {w}w" for w in ws)
    src = f"{MED}{name}-{[w for w in ws if w <= 960][-1]}.webp"
    a = e(alt if alt is not None else m["alt"])
    load = 'loading="lazy" decoding="async"' if lazy else 'fetchpriority="high"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{src}" srcset="{srcset}" sizes="{sizes}" width="{m["w"]}" '
            f'height="{m["h"]}" alt="{a}" {load}>')


# ---------------------------------------------------------------- layout
NAV_MAIN = [("skateboard", "Skateboard"), ("snowboard-och-freeski", "Snö och freeski"),
            ("skateskola", "Skateskola"), ("platser", "Platser"), ("tavlingar", "Tävlingar"),
            ("kontakt", "Kontakt")]
NAV_GROUPS = [
    ("Sporter", ["skateboard", "snowboard-och-freeski", "skateskola", "tavlingar"]),
    ("Platser", ["platser", "platser/sunnerstabacken", "platser/allis-uppsala", "platser/kap-rampen"]),
    ("Föreningen", ["om-foreningen", "tjejer", "engagera-dig", "partners", "galleri", "vanliga-fragor", "kontakt"]),
]


def header(slug):
    def cur(s):
        return ' aria-current="page"' if s == slug or (s and slug.startswith(s + "/")) else ""
    main = "".join(f'<li><a href="{u(s)}"{cur(s)}>{t}</a></li>' for s, t in NAV_MAIN)
    groups = ""
    for i, (g, items) in enumerate(NAV_GROUPS):
        links = "".join(f'<li><a href="{u(s)}"{cur(s)}>{e(TITLES[s])}</a></li>' for s in items)
        groups += f'<div class="panel__group pop" style="--i:{i}"><p class="panel__h">{g}</p><ul>{links}</ul></div>'
    return f"""<a class="skip" href="#innehall">Hoppa till innehållet</a>
<header class="top"><div class="top__in">
<a class="brand" href="{u('')}"><img src="{MED}logo-rund-64.png" width="44" height="44" alt=""><span>Uppsala Crew <b>IF</b></span></a>
<nav class="top__nav" aria-label="Huvudmeny"><ul>{main}</ul></nav>
<a class="btn btn--accent top__cta" href="{u('bli-medlem')}">Bli medlem</a>
<button class="menubtn" type="button" aria-expanded="false" aria-controls="meny"><span>Meny</span></button>
</div>
<div class="panel" id="meny" hidden><div class="panel__in"><span class="tape tape--tc"></span>
<nav aria-label="Alla sidor"><div class="panel__grid">{groups}</div></nav>
<div class="panel__foot"><a class="btn btn--accent" href="{u('bli-medlem')}">Bli medlem</a><a class="btn btn--ghost" href="{u('')}">Startsidan</a></div>
</div></div></header>"""


def footer():
    return f"""<footer class="foot"><div class="wrap foot__grid">
<div class="foot__brand"><img src="{MED}logo-rund-192.png" width="96" height="96" alt="Uppsala Crew IF logotyp" loading="lazy"><p>{e(ORG['tagline'])}.</p></div>
<div><h2 class="foot__h">Kontakt</h2><p><a href="mailto:{ORG['email']}">{ORG['email']}</a><br><a href="tel:{ORG['phone_href']}">{ORG['phone']}</a><br>{ORG['street']}, {ORG['zip']} {ORG['city']}</p></div>
<div><h2 class="foot__h">Följ oss</h2><p><a href="{ORG['instagram']}" rel="noopener">Instagram {ORG['instagram_handle']}</a><br><a href="{ORG['facebook']}" rel="noopener">Facebook</a></p></div>
<div><h2 class="foot__h">Mer</h2><p><a href="{u('vanliga-fragor')}">Vanliga frågor</a><br><a href="{u('partners')}">Partners och förbund</a><br><a href="{u('integritetspolicy')}">Integritetspolicy</a></p></div>
</div><p class="wrap foot__legal">{ORG['legal']} · Org.nr {ORG['orgnr']} · Grundad {ORG['founded']}</p></footer>"""


def org_ld():
    return {"@context": "https://schema.org", "@type": "SportsOrganization", "name": ORG["name"],
            "legalName": ORG["legal"], "url": SITE + "/", "logo": SITE + "/media/logo-rund-512.png",
            "email": ORG["email"], "telephone": ORG["phone_href"], "foundingDate": ORG["founded"],
            "taxID": ORG["orgnr"], "sport": ["Skateboarding", "Snowboarding", "Freeskiing"],
            "address": {"@type": "PostalAddress", "streetAddress": ORG["street"], "postalCode": ORG["zip"],
                        "addressLocality": ORG["city"], "addressCountry": "SE"},
            "sameAs": [ORG["instagram"], ORG["facebook"]]}


def crumbs(slug):
    trail = [("", "Start")]
    parts = slug.split("/")
    for i in range(len(parts)):
        s = "/".join(parts[: i + 1])
        trail.append((s, TITLES[s]))
    return trail


def page(slug, title, desc, body, ld=None, og=None, preload=None):
    lds = [org_ld()] + list(ld or [])
    nav_html = ""
    if slug and slug != "404":
        tr = crumbs(slug)
        lds.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": t, "item": f"{SITE}/{s + '/' if s else ''}"}
            for i, (s, t) in enumerate(tr)]})
        li = "".join(f'<li><a href="{u(s)}">{e(t)}</a></li>' for s, t in tr[:-1])
        nav_html = f'<nav class="crumbs wrap" aria-label="Brödsmulor"><ol>{li}<li aria-current="page">{e(tr[-1][1])}</li></ol></nav>'
    full = f"{title} – {ORG['name']}" if slug else f"{ORG['name']} – {title}"
    canon = f"{SITE}/{slug + '/' if slug and slug != '404' else ''}"
    og_img = f"{SITE}/media/{og or 'snowboard-hopp'}-{[w for w in M[og or 'snowboard-hopp']['widths'] if w <= 960][-1]}.webp"
    pre = ""
    if preload:
        m = M[preload]
        pre = (f'<link rel="preload" as="image" href="{MED}{preload}-{[w for w in m["widths"] if w <= 960][-1]}.webp" imagesrcset="'
               + ", ".join(f"{MED}{preload}-{w}.webp {w}w" for w in m["widths"]) + '" imagesizes="(min-width: 900px) 50vw, 100vw">')
    ldjson = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    doc = f"""<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="noindex">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#F1EEE6">
<meta property="og:type" content="website">
<meta property="og:locale" content="sv_SE">
<meta property="og:site_name" content="{ORG['name']}">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{MED}logo-rund-64.png" type="image/png">
<link rel="apple-touch-icon" href="{MED}logo-rund-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap">
{pre}
<link rel="stylesheet" href="{P}assets/style.css">
<script>document.documentElement.classList.add('js')</script>
{ldjson}
</head>
<body>
<div class="grain" aria-hidden="true"></div>
{header(slug)}
<main id="innehall">
{nav_html}{body}
{MARQ}
</main>
{footer()}
<script src="{P}assets/site.js" defer></script>
</body>
</html>
"""
    target = OUT / "404.html" if slug == "404" else OUT / (slug + "/index.html" if slug else "index.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")


def head(eyebrow, h1, lead, image=None, extra=""):
    pic = ""
    if image:
        pic = f'<div class="phero__pic pop" style="--i:2">{img(image, "(min-width: 900px) 46vw, 100vw", lazy=False)}<span class="tape tape--tl"></span></div>'
    return f"""<section class="phero wrap{' phero--pic' if image else ''}">
<div class="phero__txt"><p class="eyebrow pop" style="--i:0">{e(eyebrow)}</p><h1 class="pop" style="--i:1">{e(h1)}</h1>
<p class="lead pop" style="--i:2">{e(lead)}</p>{extra}</div>{pic}</section>"""


def sections_html(secs, start=0):
    out = ""
    for i, s in enumerate(secs):
        ps = "".join(f"<p>{e(p)}</p>" for p in s["p"])
        out += f'<article class="txtcard pop" style="--i:{i % 3}"><span class="num">{i + 1 + start:02d}</span><h2>{e(s["h"])}</h2>{ps}</article>'
    return f'<div class="txtgrid">{out}</div>'


def faq_html(items, h="h3"):
    out = ""
    for i, f in enumerate(items):
        out += (f'<details class="acc pop" style="--i:{i % 4}"><summary><{h} class="acc__q">{e(f["q"])}</{h}>'
                f'<span class="acc__ic" aria-hidden="true"></span></summary><div class="acc__a"><p>{e(f["a"])}</p></div></details>')
    return f'<div class="accs">{out}</div>'


def masonry(items):
    out = ""
    for i, g in enumerate(items):
        out += (f'<figure class="mz__it pop" style="--i:{i % 4}">{img(g["image"], "(min-width: 1100px) 30vw, (min-width: 640px) 45vw, 100vw")}'
                f'<figcaption>{e(g["caption"])}</figcaption></figure>')
    return f'<div class="mz">{out}</div>'


def cta_band():
    return f"""<section class="band wrap pop"><div class="band__in">
<div><p class="eyebrow eyebrow--light">Medlemskap</p><h2>Bli medlem för {e(C['membership']['price'])}</h2>
<p>{e(C['membership']['price_note'])} Medlemmar är försäkrade på föreningens aktiviteter.</p></div>
<div class="band__btns"><a class="btn btn--accent btn--lg" href="{u('bli-medlem')}">Bli medlem</a><a class="btn btn--light" href="{u('vanliga-fragor')}">Vanliga frågor</a></div>
</div></section>"""


CONSENT = (f'<label class="check"><input type="checkbox" name="samtycke" required><span>Jag godkänner att föreningen '
           f'behandlar mina uppgifter enligt <a href="{P}integritetspolicy/">integritetspolicyn</a>.</span></label>')


def join_form():
    return f"""<form class="form pop" data-mail="{ORG['email']}" data-subject="Medlemsansökan Uppsala Crew IF" action="mailto:{ORG['email']}" method="post" enctype="text/plain">
<h2>Medlemsansökan</h2>
<p class="muted">Formuläret öppnar ett förifyllt mejl som du skickar själv.</p>
<div class="field"><label for="m-namn">Namn</label><input id="m-namn" name="namn" data-label="Namn" autocomplete="name" required></div>
<div class="field"><label for="m-epost">E-post</label><input id="m-epost" name="epost" type="email" data-label="E-post" autocomplete="email" required></div>
<div class="field"><label for="m-sport">Vad åker du?</label><select id="m-sport" name="sport" data-label="Sport"><option value="">Välj</option><option>Skateboard</option><option>Snowboard</option><option>Freeski</option><option>Flera av dem</option></select></div>
<div class="field"><label for="m-belopp">Medlemsavgift</label><select id="m-belopp" name="belopp" data-label="Avgift"><option>50 kr</option><option>75 kr</option><option selected>100 kr</option></select></div>
{CONSENT}
<button class="btn btn--accent btn--lg" type="submit">Skicka ansökan</button>
<p class="form__status" role="status" aria-live="polite"></p>
</form>"""


def contact_form():
    return f"""<form class="form pop" data-mail="{ORG['email']}" data-subject="Fråga till Uppsala Crew IF" action="mailto:{ORG['email']}" method="post" enctype="text/plain">
<h2>Skriv till oss</h2>
<p class="muted">Formuläret öppnar ett förifyllt mejl som du skickar själv.</p>
<div class="field"><label for="k-namn">Namn</label><input id="k-namn" name="namn" data-label="Namn" autocomplete="name" required></div>
<div class="field"><label for="k-epost">E-post</label><input id="k-epost" name="epost" type="email" data-label="E-post" autocomplete="email" required></div>
<div class="field"><label for="k-amne">Ämne</label><select id="k-amne" name="amne" data-label="Ämne"><option>Träning</option><option>Medlemskap</option><option>Tävlingar</option><option>Samarbete eller sponsring</option><option>Annat</option></select></div>
<div class="field"><label for="k-msg">Meddelande</label><textarea id="k-msg" name="meddelande" rows="5" data-label="Meddelande" required></textarea></div>
{CONSENT}
<button class="btn btn--accent btn--lg" type="submit">Skicka meddelande</button>
<p class="form__status" role="status" aria-live="polite"></p>
</form>"""


# ---------------------------------------------------------------- pages
ARROW = ('<svg class="scrawl pop" style="--i:5" viewBox="0 0 160 90" aria-hidden="true"><path d="M8 70c30 8 70 4 98-22 10-9 16-20 20-32" fill="none" stroke="#111" stroke-width="3" stroke-linecap="round"/>'
         '<path d="M112 22l15-8 3 17" fill="none" stroke="#111" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>')
MARQ_ITEMS = " ".join(f"<span>{w}</span><b aria-hidden='true'>✶</b>" for w in ["Skateboard", "Snowboard", "Freeski", "Skateskola", "Miniramp Madness", "Uppsala Rail Jam", "Sunnersta", "Allis", "KAP-rampen"])
MARQ = f'<div class="marq" aria-hidden="true"><div class="marq__track">{MARQ_ITEMS}{MARQ_ITEMS}</div></div>'


def build_home():
    facts = C["facts"]
    pos = ["f1", "f2", "f3", "f4"]
    bubbles = "".join(f'<div class="bubble bubble--{pos[i]} pop" style="--i:{i + 3}"><span>{e(f["label"])}</span><b>{e(f["value"])}</b></div>'
                      for i, f in enumerate(facts))
    s = C["sports"]
    bento = f"""<div class="bento">
<a class="tile tile--big pop" style="--i:0" href="{u(s[0]['slug'])}">{img(s[0]['hero'], '(min-width: 900px) 58vw, 100vw')}<div class="tile__txt"><p class="chip">{e(s[0]['when'])}</p><h3>{e(s[0]['title'])}</h3><p>{e(s[0]['short'])}</p></div></a>
<a class="tile tile--tall pop" style="--i:1" href="{u(s[1]['slug'])}">{img('instruktorer', '(min-width: 900px) 38vw, 100vw')}<div class="tile__txt"><p class="chip">{e(s[1]['when'])}</p><h3>{e(s[1]['title'])}</h3><p>{e(s[1]['short'])}</p></div></a>
<a class="tile tile--ice pop" style="--i:2" href="{u(s[2]['slug'])}"><p class="chip chip--dark">{e(s[2]['when'])}</p><h3>{e(s[2]['title'])}</h3><p>{e(s[2]['short'])}</p><span class="arrow" aria-hidden="true">→</span></a>
<a class="tile tile--orange pop" style="--i:3" href="{u('tavlingar')}"><p class="chip chip--light">Två återkommande</p><h3>Tävlingar</h3><p>Miniramp Madness och Uppsala Rail Jam, öppna för alla nivåer, åldrar och kön.</p><span class="arrow" aria-hidden="true">→</span></a>
<a class="tile tile--img pop" style="--i:4" href="{u('tjejer')}">{img('tjejer-skate', '(min-width: 900px) 40vw, 100vw')}<div class="tile__txt"><h3>Tjejsatsning</h3><p>{e(C['girls']['lead'])}</p></div></a>
</div>"""
    places = "".join(
        f'<a class="place pop" style="--i:{i}" href="{u("platser/" + p["slug"])}"><span class="place__dot" aria-hidden="true"></span><span><b>{e(p["title"])}</b><small>{e(p["short"])}</small></span></a>'
        for i, p in enumerate(C["places"]))
    body = f"""<section class="hero wrap"><span class="pageno" aria-hidden="true">01</span>
<div class="hero__txt"><p class="eyebrow pop" style="--i:0">{e(ORG['name'])} · Uppsala</p>
<h1 class="pop" style="--i:1">{e(C['intro']['headline'])}</h1>
<p class="lead pop" style="--i:2">{e(C['intro']['lead'])}</p>
<div class="btnrow pop" style="--i:3"><a class="btn btn--accent btn--lg" href="{u('bli-medlem')}">Bli medlem</a><a class="btn btn--ghost btn--lg" href="{u('skateskola')}">Skateskolan</a></div></div>
<div class="hero__art"><div class="hero__pill pop" style="--i:1">{img('snowboard-hopp', '(min-width: 900px) 50vw, 100vw', lazy=False)}<span class="tape tape--tl"></span></div>
<div class="hero__pill2 pop" style="--i:2">{img('skate-luft-inne', '(min-width: 900px) 30vw, 60vw', lazy=False)}<span class="tape tape--tr"></span></div>
<span class="sticker pop" style="--i:4">Sedan {e(ORG['founded'])}</span>{ARROW}{bubbles}</div>
</section>
{MARQ}
<section class="sec wrap" aria-labelledby="sport-h"><span class="pageno" aria-hidden="true">02</span><div class="sechead"><p class="eyebrow pop">Sporter</p><h2 id="sport-h" class="pop">Tre sporter, en förening</h2></div>{bento}</section>
<section class="sec wrap" aria-labelledby="plats-h"><span class="pageno" aria-hidden="true">03</span><div class="split">
<div class="sechead"><p class="eyebrow pop">Platser</p><h2 id="plats-h" class="pop">Här åker vi</h2><p class="pop">{e(C['about']['lead'])}</p><p class="pop"><a class="btn btn--ghost" href="{u('platser')}">Alla platser</a></p></div>
<div class="places">{places}</div></div></section>
<section class="sec wrap" aria-labelledby="gal-h"><span class="pageno" aria-hidden="true">04</span><div class="sechead sechead--row"><div><p class="eyebrow pop">Galleri</p><h2 id="gal-h" class="pop">Från backen och rampen</h2></div><a class="btn btn--ghost pop" href="{u('galleri')}">Hela galleriet</a></div>{masonry(C['gallery'][:6])}</section>
<section class="sec wrap" aria-labelledby="faq-h"><span class="pageno" aria-hidden="true">05</span><div class="split">
<div class="sechead"><p class="eyebrow pop">Frågor</p><h2 id="faq-h" class="pop">Det här undrar många</h2><p class="pop"><a class="btn btn--ghost" href="{u('vanliga-fragor')}">Alla frågor</a></p></div>
{faq_html(C['faq'][:4])}</div></section>
{cta_band()}"""
    page("", "Skateboard, snowboard och freeski i Uppsala",
         "Uppsala Crew IF är en ideell förening för skateboard, snowboard och freeski i Uppsala. Skateskola, parkåkning i Sunnerstabacken och tävlingar för alla nivåer.",
         body, preload="snowboard-hopp")


def build_about():
    a = C["about"]
    tl = "".join(f'<li class="tl__it pop" style="--i:{i}"><span class="tl__yr">{e(t["year"])}</span><p>{e(t["text"])}</p></li>' for i, t in enumerate(a["timeline"]))
    body = f"""{head('Föreningen', 'Om föreningen', a['lead'], 'graffiti')}
<section class="sec wrap" aria-labelledby="hist-h"><div class="sechead"><p class="eyebrow pop">Historik</p><h2 id="hist-h" class="pop">Sedan {e(ORG['founded'])}</h2></div><ol class="tl">{tl}</ol></section>
<section class="sec wrap"><div class="duo">
<article class="txtcard txtcard--ice pop"><h2>Vision</h2><p>{e(a['vision'])}</p></article>
<article class="txtcard pop" style="--i:1"><h2>Organisation</h2><p>{e(a['org_text'])}</p><p>Org.nr {ORG['orgnr']}.</p></article>
</div></section>
{cta_band()}"""
    page("om-foreningen", "Om föreningen", a["meta_description"], body, og="graffiti", preload="graffiti")


def build_sport(sl):
    s = SPORTS[sl]
    info = f'<dl class="facts pop" style="--i:3"><div><dt>Var</dt><dd>{e(s["where"])}</dd></div><div><dt>När</dt><dd>{e(s["when"])}</dd></div></dl>'
    sched = ""
    if s.get("schedule"):
        rows = "".join(f'<div class="sched__row"><dt>{e(r["k"])}</dt><dd>{e(r["v"])}</dd></div>' for r in s["schedule"])
        sched = f'<section class="sec wrap" aria-labelledby="sch-h"><div class="sched pop"><h2 id="sch-h">Schema</h2><dl>{rows}</dl></div></section>'
    gal = masonry([{"image": i, "caption": M[i]["alt"]} for i in s["images"]])
    body = f"""{head('Sport', s['title'], s['short'], s['hero'], info)}
{sched}
<section class="sec wrap">{sections_html(s['sections'])}</section>
<section class="sec wrap" aria-labelledby="bild-h"><div class="sechead"><p class="eyebrow pop">Bilder</p><h2 id="bild-h" class="pop">{e(s['title'])} i Uppsala</h2></div>{gal}</section>
{cta_band()}"""
    ld = [{"@context": "https://schema.org", "@type": "Service", "name": s["title"], "description": s["meta_description"],
           "serviceType": s["title"], "areaServed": {"@type": "City", "name": "Uppsala"},
           "provider": {"@type": "SportsOrganization", "name": ORG["name"], "url": SITE + "/"},
           "url": f"{SITE}/{sl}/"}]
    page(sl, s["title"], s["meta_description"], body, ld=ld, og=s["hero"], preload=s["hero"])


def build_girls():
    g = C["girls"]
    body = f"""{head('Föreningen', g['title'], g['lead'], g['image'])}
<section class="sec wrap">{sections_html(g['sections'])}</section>
<section class="sec wrap"><div class="duo">
<a class="tile tile--ice pop" href="{u('skateskola')}"><h2 class="h3">Skateskolan</h2><p>{e(SPORTS['skateskola']['short'])}</p><span class="arrow" aria-hidden="true">→</span></a>
<a class="tile tile--orange pop" style="--i:1" href="{u('tavlingar')}"><h2 class="h3">Tävlingar med tjejklass</h2><p>Tjejklass med prispengar på Miniramp Madness.</p><span class="arrow" aria-hidden="true">→</span></a>
</div></section>
{cta_band()}"""
    page("tjejer", g["title"], g["meta_description"], body, og=g["image"], preload=g["image"])


def place_card(p, i):
    pic = img(p["image"], "(min-width: 900px) 30vw, 100vw") if p["image"] else '<div class="noimg" aria-hidden="true"><span>Miniramp</span></div>'
    return (f'<a class="pcard pop" style="--i:{i}" href="{u("platser/" + p["slug"])}"><div class="pcard__pic">{pic}</div>'
            f'<div class="pcard__txt"><p class="chip chip--dark">{e(p["address"])}</p><h2 class="h3">{e(p["title"])}</h2><p>{e(p["short"])}</p></div></a>')


def build_places():
    cards = "".join(place_card(p, i) for i, p in enumerate(C["places"]))
    body = f"""{head('Platser', 'Platser', 'Skateboard på KAP-rampen, Kapellgärdet och inomhus på Allis Uppsala. Snowboard och freeski i Sunnerstabacken under vintern.')}
<section class="sec wrap"><div class="pcards">{cards}</div></section>
{cta_band()}"""
    page("platser", "Platser", "Här åker Uppsala Crew IF: Sunnerstabacken, Allis Uppsala och KAP-rampen vid Kapellgärdet.", body)


def build_place(p):
    sl = "platser/" + p["slug"]
    ps = "".join(f'<p class="pop" style="--i:{i % 3}">{e(t)}</p>' for i, t in enumerate(p["body"]))
    others = "".join(place_card(o, i) for i, o in enumerate(x for x in C["places"] if x["slug"] != p["slug"]))
    extra = f'<dl class="facts pop" style="--i:3"><div><dt>Adress</dt><dd>{e(p["address"])}</dd></div></dl>'
    body = f"""{head('Plats', p['title'], p['short'], p['image'], extra)}
<section class="sec wrap"><div class="prose txtcard">{ps}</div></section>
<section class="sec wrap" aria-labelledby="fler-h"><div class="sechead"><h2 id="fler-h" class="pop">Fler platser</h2></div><div class="pcards pcards--two">{others}</div></section>
{cta_band()}"""
    ld = [{"@context": "https://schema.org", "@type": "SportsActivityLocation", "name": p["title"], "description": p["short"],
           "address": {"@type": "PostalAddress", "streetAddress": p["address"], "addressLocality": "Uppsala", "addressCountry": "SE"},
           "url": f"{SITE}/{sl}/"}]
    if p["image"]:
        ld[0]["image"] = f"{SITE}/media/{p['image']}-{[w for w in M[p['image']]['widths'] if w <= 960][-1]}.webp"
    page(sl, p["title"], f"{p['title']}: {p['short']} {p['address']}.", body, ld=ld, og=p["image"], preload=p["image"])


def build_comps():
    cp = C["competitions"]
    items = ""
    for i, c in enumerate(cp["items"]):
        cl = "".join(f'<li class="chip chip--dark">{e(x)}</li>' for x in c["classes"])
        items += f"""<article class="comp pop" style="--i:{i}"><div class="comp__pic">{img(c['image'], '(min-width: 900px) 45vw, 100vw')}</div>
<div class="comp__txt"><p class="eyebrow">{e(c['sport'])} · {e(c['place'])}</p><h2>{e(c['title'])}</h2><p>{e(c['text'])}</p><h3 class="mini">Klasser</h3><ul class="chips">{cl}</ul></div></article>"""
    body = f"""{head('Tävlingar', 'Tävlingar', cp['lead'])}
<section class="sec wrap"><div class="comps">{items}</div></section>
<section class="sec wrap"><div class="txtcard txtcard--ice pop"><h2>Datum och anmälan</h2><p>Datum för kommande tävlingar publiceras på Instagram, <a href="{ORG['instagram']}" rel="noopener">{ORG['instagram_handle']}</a>. Vill du hjälpa till som funktionär? Läs mer under <a href="{u('engagera-dig')}">Engagera dig</a>.</p></div></section>
{cta_band()}"""
    page("tavlingar", "Tävlingar", cp["meta_description"], body, og="skate-luft-inne")


def build_gallery():
    body = f"""{head('Galleri', 'Galleri', 'Bilder från Sunnerstabacken, Allis, KAP-rampen och skateskolan.')}
<section class="sec wrap">{masonry(C['gallery'])}</section>
{cta_band()}"""
    page("galleri", "Galleri", "Bilder från Uppsala Crew IF: snowboard och freeski i Sunnerstabacken, skateboard på Allis och KAP-rampen, skateskolan.", body)


def build_engage():
    en = C["engage"]
    roles = "".join(f'<article class="txtcard{" txtcard--ice" if i % 3 == 0 else ""} pop" style="--i:{i}"><span class="num">{i + 1:02d}</span><h2 class="h3">{e(r["title"])}</h2><p>{e(r["text"])}</p></article>'
                    for i, r in enumerate(en["roles"]))
    body = f"""{head('Föreningen', 'Engagera dig', en['lead'], 'instruktorer', f'<div class="btnrow pop" style="--i:3"><a class="btn btn--accent btn--lg" href="{u("kontakt")}">Hör av dig</a></div>')}
<section class="sec wrap"><div class="txtgrid txtgrid--two">{roles}</div></section>
{cta_band()}"""
    page("engagera-dig", "Engagera dig", en["meta_description"], body, og="instruktorer", preload="instruktorer")


def build_partners():
    pa = C["partners"]
    fed = "".join(f'<li class="pop" style="--i:{i % 4}"><a class="pillink" href="{f["url"]}" rel="noopener">{e(f["name"])}<span aria-hidden="true">↗</span></a></li>' for i, f in enumerate(pa["federations"]))
    sp = "".join(f'<li class="sponsor pop" style="--i:{i % 4}">{e(x)}</li>' for i, x in enumerate(pa["sponsors"]))
    body = f"""{head('Föreningen', 'Partners och förbund', pa['lead'])}
<section class="sec wrap" aria-labelledby="fb-h"><div class="sechead"><h2 id="fb-h" class="pop">Förbund och samarbeten</h2></div><ul class="pillinks">{fed}</ul></section>
<section class="sec wrap" aria-labelledby="sp-h"><div class="sechead"><h2 id="sp-h" class="pop">Sponsorer</h2><p class="pop">{e(pa['sponsors_note'])}</p></div><ul class="sponsors">{sp}</ul></section>
<section class="sec wrap"><div class="txtcard txtcard--ice pop"><h2>Vill ni stötta?</h2><p>{e(en_role('Sponsor eller samarbete'))}</p><p><a class="btn btn--accent" href="{u('kontakt')}">Kontakta oss</a></p></div></section>"""
    page("partners", "Partners och förbund", pa["meta_description"], body)


def en_role(t):
    return next(r["text"] for r in C["engage"]["roles"] if r["title"] == t)


def build_join():
    ms = C["membership"]
    ben = "".join(f'<li class="pop" style="--i:{i}">{e(b)}</li>' for i, b in enumerate(ms["benefits"]))
    st = "".join(f'<li class="pop" style="--i:{i}"><span class="step">{i + 1}</span><span>{e(x)}</span></li>' for i, x in enumerate(ms["steps"]))
    body = f"""{head('Medlemskap', 'Bli medlem', f"{ms['price']}. {ms['price_note']}")}
<section class="sec wrap"><div class="joingrid">
<div><div class="txtcard txtcard--ice pop"><h2>Det här ingår</h2><ul class="ticks">{ben}</ul></div>
<div class="txtcard pop" style="--i:1"><h2>Så går det till</h2><ol class="steps">{st}</ol></div></div>
{join_form()}</div></section>"""
    page("bli-medlem", "Bli medlem", ms["meta_description"], body)


def build_faq():
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in C["faq"]]}]
    body = f"""{head('Frågor', 'Vanliga frågor', 'Svar om medlemskap, försäkring, utrustning och träning. Hittar du inte svaret, mejla oss.')}
<section class="sec wrap narrow">{faq_html(C['faq'], 'h2')}</section>
{cta_band()}"""
    page("vanliga-fragor", "Vanliga frågor", "Vanliga frågor om Uppsala Crew IF: medlemsavgift, försäkring, utrustning, träningstider och skateskolan.", body, ld=ld)


def build_contact():
    body = f"""{head('Kontakt', 'Kontakt', 'Frågor om träning, medlemskap eller samarbete. Ändringar och inställda pass läggs ut på Instagram.')}
<section class="sec wrap"><div class="joingrid">
<div class="contactcards">
<a class="ccard ccard--orange pop" href="mailto:{ORG['email']}"><span>E-post</span><b>{ORG['email']}</b></a>
<a class="ccard ccard--ice pop" style="--i:1" href="tel:{ORG['phone_href']}"><span>Telefon</span><b>{ORG['phone']}</b></a>
<a class="ccard pop" style="--i:2" href="{ORG['instagram']}" rel="noopener"><span>Instagram</span><b>{ORG['instagram_handle']}</b></a>
<div class="ccard pop" style="--i:3"><span>Postadress</span><b>{ORG['legal']}<br>{ORG['street']}<br>{ORG['zip']} {ORG['city']}</b></div>
<p class="muted pop">Alternativ e-post: <a href="mailto:{ORG['email_alt']}">{ORG['email_alt']}</a> · <a href="{ORG['facebook']}" rel="noopener">Facebook</a> · Org.nr {ORG['orgnr']}</p>
</div>
{contact_form()}</div></section>"""
    page("kontakt", "Kontakt", "Kontakta Uppsala Crew IF om träning, medlemskap, tävlingar eller samarbete. E-post, telefon och Instagram.", body)


def build_privacy():
    secs = "".join(f'<section class="pop"><h2>{e(s["h"])}</h2><p>{e(s["p"])}</p></section>' for s in C["privacy"])
    body = f"""{head('Information', 'Integritetspolicy', 'Så behandlar Uppsala Crew IF dina personuppgifter.')}
<div class="sec wrap narrow"><div class="txtcard prose">{secs}</div></div>"""
    page("integritetspolicy", "Integritetspolicy", "Uppsala Crew IF:s integritetspolicy: vilka personuppgifter vi behandlar, varför, hur länge och dina rättigheter.", body)


def build_404():
    body = f"""<section class="phero wrap"><div class="phero__txt"><p class="eyebrow">Fel 404</p><h1>Sidan finns inte</h1>
<p class="lead">Länken kan vara gammal eller felstavad.</p><div class="btnrow"><a class="btn btn--accent btn--lg" href="{u('')}">Till startsidan</a><a class="btn btn--ghost btn--lg" href="{u('kontakt')}">Kontakt</a></div></div></section>"""
    page("404", "Sidan finns inte", "Sidan kunde inte hittas.", body)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    src = Path(__file__).parent / "assets"
    for f in src.iterdir():
        shutil.copy(f, OUT / "assets" / f.name)
    build_home(); build_about()
    for sl in SPORTS:
        build_sport(sl)
    build_girls(); build_places()
    for p in C["places"]:
        build_place(p)
    build_comps(); build_gallery(); build_engage(); build_partners()
    build_join(); build_faq(); build_contact(); build_privacy(); build_404()
    n = len(list(OUT.rglob("*.html")))
    print(f"{V}: {n} html-filer i {OUT}")


if __name__ == "__main__":
    main()
