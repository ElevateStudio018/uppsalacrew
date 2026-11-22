#!/usr/bin/env python3
"""v03 Nattpark – mörkt tema för Uppsala Crew IF. Kör: python3 themes/v03/build.py"""
import json, html, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V = "v03"
OUT = ROOT / "docs" / V
B = f"/uppsalacrew/{V}"
M = "/uppsalacrew/media"
SITE = "https://www.uppsalacrew.se"
PREVIEW = "https://elevatestudio018.github.io/uppsalacrew"

C = json.loads((ROOT / "content/content.json").read_text(encoding="utf-8"))
MAN = json.loads((ROOT / "docs/media/manifest.json").read_text(encoding="utf-8"))
ORG = C["org"]
PAGES = {p["slug"]: p for p in C["pages"]}
SPORTS = {s["slug"]: s for s in C["sports"]}
PLACES = {p["slug"]: p for p in C["places"]}


def e(s):
    return html.escape(str(s), quote=True)


def url(slug):
    return f"{B}/{slug}/" if slug else f"{B}/"


def img(name, sizes="100vw", lazy=True, cls="", alt=None):
    m = MAN[name]
    ws = m["widths"]
    srcset = ", ".join(f"{M}/{name}-{w}.webp {w}w" for w in ws)
    mid = next((w for w in ws if w >= 960), ws[-1])
    la = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img src="{M}/{name}-{mid}.webp" srcset="{srcset}" sizes="{sizes}" width="{m["w"]}" height="{m["h"]}"'
            f' alt="{e(alt or m["alt"])}"{la}{c}>')


def og_img(name):
    w = MAN[name]["widths"]
    return f"{PREVIEW}/media/{name}-{w[min(2, len(w) - 1)]}.webp"


def split(text, tag="h2", cls=""):
    """Rubrik som glider upp rad för rad (orden grupperas till rader i JS)."""
    words = "".join(f'<span class="w"><span>{e(w)}</span></span> ' for w in str(text).split())
    c = f' class="split {cls}"'.replace(" \"", "\"")
    return f'<{tag}{c} aria-label="{e(text)}"><span aria-hidden="true">{words.strip()}</span></{tag}>'


# ---------- JSON-LD ----------
def org_ld():
    return {
        "@context": "https://schema.org", "@type": "SportsOrganization", "@id": SITE + "/#org",
        "name": ORG["name"], "legalName": ORG["legal"], "url": SITE + "/",
        "logo": f"{PREVIEW}/media/logo-rund-512.png", "description": ORG["tagline"],
        "foundingDate": ORG["founded"], "email": ORG["email"], "telephone": ORG["phone_href"],
        "identifier": {"@type": "PropertyValue", "propertyID": "Organisationsnummer", "value": ORG["orgnr"]},
        "address": {"@type": "PostalAddress", "streetAddress": ORG["street"], "postalCode": ORG["zip"].replace(" ", ""),
                    "addressLocality": ORG["city"], "addressCountry": "SE"},
        "areaServed": {"@type": "City", "name": "Uppsala"},
        "sport": ["Skateboarding", "Snowboarding", "Freestyle skiing"],
        "sameAs": [ORG["instagram"], ORG["facebook"]],
    }


def crumbs_ld(slug):
    trail = [("Start", "")]
    parts = slug.split("/")
    for i in range(len(parts)):
        s = "/".join(parts[:i + 1])
        trail.append((PAGES[s]["title"], s))
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{SITE}/{s}/" if s else SITE + "/"}
        for i, (n, s) in enumerate(trail)]}, trail


def service_ld(s):
    return {"@context": "https://schema.org", "@type": "Service", "name": s["title"], "description": s["short"],
            "provider": {"@id": SITE + "/#org"}, "areaServed": "Uppsala"}


def place_ld(p):
    return {"@context": "https://schema.org", "@type": "SportsActivityLocation", "name": p["title"], "description": p["short"],
            "address": {"@type": "PostalAddress", "streetAddress": p["address"], "addressLocality": "Uppsala", "addressCountry": "SE"}}


def faq_ld():
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in C["faq"]]}


# ---------- Ramverk ----------
NAV = [
    ("Sporter", ["skateboard", "snowboard-och-freeski", "skateskola"]),
    ("Platser", ["platser", "platser/sunnerstabacken", "platser/allis-uppsala", "platser/kap-rampen"]),
    ("Föreningen", ["om-foreningen", "tjejer", "tavlingar", "galleri", "engagera-dig", "partners", "vanliga-fragor"]),
]


def header(slug):
    cols = ""
    for g, slugs in NAV:
        lis = "".join(
            f'<li><a href="{url(s)}"{" aria-current=\"page\"" if s == slug else ""}>{e(PAGES[s]["title"])}</a></li>' for s in slugs)
        cols += f'<div class="menu__col"><p class="menu__h">{g}</p><ul>{lis}</ul></div>'
    return f"""<a class="skip" href="#innehall">Hoppa till innehållet</a>
<div class="progress" aria-hidden="true"><span></span></div>
<header class="top">
  <a class="brand" href="{url('')}"><img src="{M}/logo-rund-64.png" width="40" height="40" alt=""><span>Uppsala Crew</span></a>
  <div class="top__r">
    <a class="btn btn--sm top__cta" href="{url('bli-medlem')}">Bli medlem</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu"><span class="menu-btn__t">Meny</span><span class="menu-btn__i" aria-hidden="true"></span></button>
  </div>
</header>
<nav class="menu" id="menu" aria-label="Huvudmeny" hidden>
  <div class="menu__in">{cols}
    <div class="menu__col menu__col--x"><p class="menu__h">Direkt</p><ul>
      <li><a href="{url('bli-medlem')}">Bli medlem</a></li><li><a href="{url('kontakt')}">Kontakt</a></li>
      <li><a href="{ORG['instagram']}" rel="noopener">Instagram</a></li></ul></div>
  </div>
</nav>"""


def marquee(items):
    t = "".join(f"<span>{e(x)}</span><i aria-hidden=\"true\">/</i>" for x in items)
    return f'<div class="band" aria-hidden="true"><div class="band__track"><div>{t}</div><div>{t}</div></div></div>'


def footer():
    f = C["facts"]
    return f"""<footer class="foot">
{marquee(["Skateboard", "Snowboard", "Freeski", "Uppsala", "Sunnersta", "KAP-rampen", "Allis"])}
<div class="foot__in wrap">
  <div class="foot__big"><p class="foot__claim">{e(ORG['tagline'])}.</p>
  <a class="btn" href="{url('bli-medlem')}">Bli medlem <span aria-hidden="true">→</span></a></div>
  <div class="foot__cols">
    <div><h2 class="foot__h">Kontakt</h2><ul>
      <li><a href="mailto:{ORG['email']}">{ORG['email']}</a></li>
      <li><a href="tel:{ORG['phone_href']}">{ORG['phone']}</a></li>
      <li>{e(ORG['street'])}, {e(ORG['zip'])} {e(ORG['city'])}</li></ul></div>
    <div><h2 class="foot__h">Följ</h2><ul>
      <li><a href="{ORG['instagram']}" rel="noopener">Instagram {e(ORG['instagram_handle'])}</a></li>
      <li><a href="{ORG['facebook']}" rel="noopener">Facebook</a></li></ul></div>
    <div><h2 class="foot__h">Föreningen</h2><ul>
      <li><a href="{url('om-foreningen')}">Om föreningen</a></li><li><a href="{url('vanliga-fragor')}">Vanliga frågor</a></li>
      <li><a href="{url('partners')}">Partners och förbund</a></li><li><a href="{url('integritetspolicy')}">Integritetspolicy</a></li></ul></div>
  </div>
  <p class="foot__legal">{e(ORG['legal'])} · Org.nr {e(ORG['orgnr'])} · Grundad {e(ORG['founded'])}</p>
</div></footer>"""


def page(slug, title, desc, body, ld=(), og="snowboard-hopp", preload=None):
    lds = [org_ld()] + list(ld)
    if slug and slug != "404":
        bl, _ = crumbs_ld(slug)
        lds.append(bl)
    full = f"{ORG['name']} – {ORG['tagline']}" if slug == "" else f"{title} – {ORG['name']}"
    canon = f"{SITE}/{slug}/" if slug else SITE + "/"
    pre = ""
    if preload:
        m = MAN[preload]
        pre = (f'<link rel="preload" as="image" imagesrcset="{", ".join(f"{M}/{preload}-{w}.webp {w}w" for w in m["widths"])}" imagesizes="100vw">')
    doc = f"""<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#0A0B0D">
<meta property="og:type" content="website">
<meta property="og:locale" content="sv_SE">
<meta property="og:site_name" content="{e(ORG['name'])}">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og_img(og)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{M}/logo-rund-64.png" type="image/png">
<link rel="apple-touch-icon" href="{M}/logo-rund-192.png">
<link rel="preconnect" href="https://api.fontshare.com">
<link rel="preconnect" href="https://cdn.fontshare.com" crossorigin>
<link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=clash-display@600,700&amp;f[]=satoshi@400,500,700&amp;display=swap">
{pre}
<link rel="stylesheet" href="{B}/assets/site.css">
<script>document.documentElement.classList.add('js')</script>
<script type="application/ld+json">{json.dumps(lds, ensure_ascii=False)}</script>
</head>
<body>
{header(slug)}
<main id="innehall">
{body}
</main>
{footer()}
<script src="{B}/assets/site.js" defer></script>
</body>
</html>
"""
    target = OUT / "404.html" if slug == "404" else (OUT / slug / "index.html" if slug else OUT / "index.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")


def crumbs(slug):
    _, trail = crumbs_ld(slug)
    lis = "".join(f'<li><a href="{url(s)}">{e(n)}</a></li>' for n, s in trail[:-1])
    return f'<nav class="crumbs" aria-label="Brödsmulor"><ol>{lis}<li aria-current="page">{e(trail[-1][0])}</li></ol></nav>'


def hero(slug, h1, lead, image=None, kicker=""):
    """Undersidor: helbild med rubrik nertill vänster, eller typografisk utan bild."""
    k = f'<p class="kicker">{e(kicker)}</p>' if kicker else ""
    if image:
        return f"""<section class="hero hero--sub">
<div class="hero__media zoom is-in">{img(image, lazy=False)}</div>
<div class="hero__txt wrap">{crumbs(slug)}{k}{split(h1, "h1", "xl")}<p class="lead rv">{e(lead)}</p></div></section>"""
    return f"""<section class="hero hero--type"><div class="wrap">{crumbs(slug)}{k}{split(h1, "h1", "xl")}<p class="lead rv">{e(lead)}</p></div></section>"""


def prose(sections, start=1):
    out = ""
    for i, s in enumerate(sections, start):
        ps = "".join(f"<p>{e(p)}</p>" for p in s["p"])
        out += f"""<section class="chap wrap"><p class="chap__n" aria-hidden="true">{i:02d}</p>
<div class="chap__b">{split(s['h'])}<div class="chap__p rv">{ps}</div></div></section>"""
    return out


def cta(h="Bli en del av crewet", text=None, href="bli-medlem", label="Bli medlem"):
    text = text or f"{C['membership']['price']}. {C['membership']['price_note']}"
    return f"""<section class="cta"><div class="wrap">{split(h, "h2", "xl")}<p class="lead rv">{e(text)}</p>
<a class="btn btn--lg rv" href="{url(href)}">{e(label)} <span aria-hidden="true">→</span></a></div></section>"""


def bleed(name, caption=None, cls=""):
    cap = f'<figcaption>{e(caption)}</figcaption>' if caption else ""
    return f'<figure class="bleed zoom {cls}">{img(name)}{cap}</figure>'


def consent(idp):
    return f"""<div class="check"><input type="checkbox" id="{idp}-ok" required>
<label for="{idp}-ok">Jag godkänner att föreningen behandlar mina uppgifter enligt <a href="{url('integritetspolicy')}">integritetspolicyn</a>.</label></div>"""


# ---------- Sidor ----------
def build_home():
    sp = "".join(f"""<li class="srow">
<a class="srow__a" href="{url(s['slug'])}">
<span class="srow__n" aria-hidden="true">{i:02d}</span>
<span class="srow__t">{e(s['title'])}</span>
<span class="srow__m">{e(s['when'])} · {e(s['where'])}</span>
<span class="srow__img zoom">{img(s['hero'], "(min-width: 900px) 40vw, 100vw")}</span>
</a></li>""" for i, s in enumerate(C["sports"], 1))
    facts = "".join(f'<li><span class="num">{e(f["value"])}</span><span class="num__l">{e(f["label"])}</span></li>'
                    for f in C["facts"] if f["label"] in ("Grundad", "Medlemsavgift"))
    places = "".join(f"""<li><a href="{url('platser/' + p['slug'])}"><span class="pl__t">{e(p['title'])}</span>
<span class="pl__s">{e(p['short'])}</span><span class="pl__go" aria-hidden="true">→</span></a></li>""" for p in C["places"])
    comps = "".join(f"""<article class="comp"><div class="comp__img zoom">{img(c['image'], "(min-width: 900px) 50vw, 100vw")}</div>
<div class="comp__b"><p class="kicker">{e(c['sport'])} · {e(c['place'])}</p><h3>{e(c['title'])}</h3><p>{e(c['text'])}</p></div></article>"""
                    for c in C["competitions"]["items"])
    gal = "".join(f'<figure class="strip__i zoom">{img(g["image"], "(min-width: 900px) 30vw, 80vw")}<figcaption>{e(g["caption"])}</figcaption></figure>'
                  for g in C["gallery"][:6])
    body = f"""<section class="hero hero--home">
<div class="hero__media zoom is-in">{img("kvallshopp", lazy=False)}</div>
<div class="hero__txt wrap">
<p class="kicker">{e(ORG['name'])} · sedan {e(ORG['founded'])}</p>
{split(C['intro']['headline'], "h1", "xxl")}
<div class="hero__row"><p class="lead rv">{e(C['intro']['lead'])}</p>
<div class="hero__btns rv"><a class="btn" href="{url('bli-medlem')}">Bli medlem <span aria-hidden="true">→</span></a>
<a class="btn btn--ghost" href="{url('skateskola')}">Skateskolan</a></div></div>
</div></section>
{marquee([s['title'] for s in C['sports']] + ["Uppsala"])}
<section class="sec wrap"><div class="sec__head"><p class="kicker">Sporterna</p>{split("Tre sätt att åka")}</div>
<ul class="srows">{sp}</ul></section>
<section class="nums wrap"><ul>{facts}
<li><span class="num">18.00</span><span class="num__l">Skateskola varje måndag</span></li></ul></section>
{bleed("snowboard-hopp", "Sunnerstabacken", "bleed--wide")}
<section class="sec wrap"><div class="sec__head"><p class="kicker">Platserna</p>{split("Här håller vi till")}</div>
<ul class="pl">{places}</ul></section>
<section class="sec wrap"><div class="sec__head"><p class="kicker">Tävlingar</p>{split("Öppet för alla nivåer")}
<p class="lead rv">{e(C['competitions']['lead'])}</p></div>
<div class="comps">{comps}</div>
<p class="rv"><a class="link" href="{url('tavlingar')}">Om tävlingarna <span aria-hidden="true">→</span></a></p></section>
<section class="split2 wrap"><div class="split2__img zoom">{img(C['girls']['image'], "(min-width: 900px) 50vw, 100vw")}</div>
<div><p class="kicker">{e(C['girls']['title'])}</p>{split("Fler tjejer i parken")}<p class="lead rv">{e(C['girls']['lead'])}</p>
<p class="rv"><a class="link" href="{url('tjejer')}">Läs om satsningen <span aria-hidden="true">→</span></a></p></div></section>
<section class="sec"><div class="wrap sec__head"><p class="kicker">Galleri</p>{split("Kvällar i backen, dagar i hallen")}</div>
<div class="strip">{gal}</div><p class="wrap rv"><a class="link" href="{url('galleri')}">Hela galleriet <span aria-hidden="true">→</span></a></p></section>
{cta()}"""
    page("", "Start", C["intro"]["lead"][:155].rsplit(" ", 1)[0] + ".", body, preload="kvallshopp",
         ld=[{"@context": "https://schema.org", "@type": "WebSite", "name": ORG["name"], "url": SITE + "/", "inLanguage": "sv-SE"}])


def build_about():
    a = C["about"]
    tl = "".join(f'<li class="tl__i"><span class="tl__y num">{e(t["year"])}</span><p>{e(t["text"])}</p></li>' for t in a["timeline"])
    facts = "".join(f'<div><dt>{e(f["label"])}</dt><dd>{e(f["value"])}</dd></div>' for f in C["facts"])
    body = f"""{hero("om-foreningen", "Föreningen bakom åkningen", a['lead'], "graffiti", "Om föreningen")}
<section class="sec wrap"><div class="sec__head"><p class="kicker">Historik</p>{split("År för år")}</div><ol class="tl">{tl}</ol></section>
<section class="quote wrap"><p class="kicker">Vision</p><p class="quote__t rv">{e(a['vision'])}</p></section>
<section class="split2 wrap"><div><p class="kicker">Organisation</p>{split("Ideellt i grunden")}<p class="lead rv">{e(a['org_text'])}</p>
<p class="rv"><a class="link" href="{url('engagera-dig')}">Engagera dig <span aria-hidden="true">→</span></a></p></div>
<dl class="facts rv">{facts}</dl></section>
{bleed("instruktorer", "Instruktörer i Uppsala Crew-jackor", "bleed--tall")}
{cta()}"""
    page("om-foreningen", "Om föreningen", a["meta_description"], body, og="graffiti")


def build_sport(slug):
    s = SPORTS[slug]
    sched = ""
    if s.get("schedule"):
        rows = "".join(f'<div><dt>{e(r["k"])}</dt><dd>{e(r["v"])}</dd></div>' for r in s["schedule"])
        sched = f"""<section class="sched wrap"><div><p class="kicker">Schema</p>{split("Måndagar")}<p class="num num--xl rv">18.00</p></div>
<dl class="facts rv">{rows}</dl></section>"""
    meta = f"""<section class="meta wrap"><dl class="meta__dl rv"><div><dt>Var</dt><dd>{e(s['where'])}</dd></div>
<div><dt>När</dt><dd>{e(s['when'])}</dd></div></dl></section>"""
    imgs = s["images"]
    gal = "".join(f'<figure class="mosaic__i zoom">{img(n, "(min-width: 900px) 50vw, 100vw")}</figure>' for n in imgs[1:])
    secs = s["sections"]
    half = (len(secs) + 1) // 2
    related = {"skateboard": ["platser/allis-uppsala", "platser/kap-rampen", "skateskola"],
               "snowboard-och-freeski": ["platser/sunnerstabacken", "tavlingar", "tjejer"],
               "skateskola": ["platser/kap-rampen", "platser/allis-uppsala", "bli-medlem"]}[slug]
    rel = "".join(f'<li><a href="{url(r)}"><span>{e(PAGES[r]["title"])}</span><span aria-hidden="true">→</span></a></li>' for r in related)
    body = f"""{hero(slug, s['title'], s['short'], s['hero'], "Sport" if slug != "skateskola" else "Barn och unga")}
{meta}{sched}
{marquee([s['title'], s['when'], *s['where'].split(', ')])}
{prose(secs[:half])}
{bleed(imgs[0])}
{prose(secs[half:], half + 1)}
{f'<section class="mosaic wrap">{gal}</section>' if gal else ''}
<section class="sec wrap"><div class="sec__head"><p class="kicker">Vidare</p><h2 class="h2">Fortsätt här</h2></div><ul class="rel">{rel}</ul></section>
{cta()}"""
    page(slug, s["title"], s["meta_description"], body, ld=[service_ld(s)], og=s["hero"], preload=s["hero"])


def build_girls():
    g = C["girls"]
    body = f"""{hero("tjejer", g['title'], g['lead'], g['image'], "Föreningen")}
{prose(g['sections'])}
{bleed("allis-bowl", "Bowlen på Allis")}
{cta("Vill du vara med och bygga satsningen", "Hör av dig om du vill vara ledare, förebild eller bara börja åka.", "kontakt", "Kontakta oss")}"""
    page("tjejer", g["title"], g["meta_description"], body, og=g["image"])


def build_places():
    lis = ""
    for i, p in enumerate(C["places"], 1):
        media = (f'<span class="pcard__img zoom">{img(p["image"], "(min-width: 900px) 50vw, 100vw")}</span>' if p["image"]
                 else f'<span class="pcard__img pcard__img--type" aria-hidden="true"><span>KAP</span></span>')
        lis += f"""<li class="pcard"><a href="{url('platser/' + p['slug'])}">{media}
<span class="pcard__b"><span class="pcard__n" aria-hidden="true">{i:02d}</span><h2 class="pcard__t">{e(p['title'])}</h2>
<span class="pcard__a">{e(p['address'])}</span><span class="pcard__s">{e(p['short'])}</span></span></a></li>"""
    body = f"""{hero("platser", "Platser", "Tre platser i Uppsala där föreningen åker, tränar och arrangerar tävlingar.", None, "Kartan")}
<section class="wrap"><ul class="pcards">{lis}</ul></section>{cta()}"""
    page("platser", "Platser", "Platserna där Uppsala Crew IF åker: Sunnerstabacken, Allis Uppsala och KAP-rampen vid Kapellgärdet.", body,
         og="allis-hall-1")
    for p in C["places"]:
        slug = "platser/" + p["slug"]
        ps = "".join(f"<p>{e(x)}</p>" for x in p["body"])
        others = "".join(f'<li><a href="{url("platser/" + o["slug"])}"><span>{e(o["title"])}</span><span aria-hidden="true">→</span></a></li>'
                         for o in C["places"] if o is not p)
        body = f"""{hero(slug, p['title'], p['short'], p['image'], "Plats")}
<section class="meta wrap"><dl class="meta__dl rv"><div><dt>Adress</dt><dd>{e(p['address'])}</dd></div></dl></section>
<section class="chap wrap"><p class="chap__n" aria-hidden="true">01</p><div class="chap__b">{split("Om platsen")}<div class="chap__p rv">{ps}</div></div></section>
<section class="sec wrap"><div class="sec__head"><p class="kicker">Fler platser</p><h2 class="h2">Åk vidare</h2></div><ul class="rel">{others}</ul></section>
{cta()}"""
        desc = f"{p['title']}, {p['address']}. {p['short']}"
        page(slug, p["title"], desc, body, ld=[place_ld(p)], og=p["image"] or "skate-luft-inne",
             preload=p["image"])


def build_comps():
    cs = C["competitions"]
    items = ""
    for i, c in enumerate(cs["items"], 1):
        cl = "".join(f"<li>{e(x)}</li>" for x in c["classes"])
        items += f"""<article class="cbig">{bleed(c['image'])}
<div class="cbig__b wrap"><p class="chap__n" aria-hidden="true">{i:02d}</p><div>
<p class="kicker">{e(c['sport'])} · {e(c['place'])}</p>{split(c['title'], "h2", "xl")}
<p class="lead rv">{e(c['text'])}</p><h3 class="h3">Klasser</h3><ul class="tags rv">{cl}</ul></div></div></article>"""
    body = f"""{hero("tavlingar", "Tävlingar", cs['lead'], None, "Föreningen")}{items}
{cta("Följ datumen på Instagram", "Datum för kommande tävlingar publiceras på Instagram.", "kontakt", "Kontakt")}"""
    page("tavlingar", "Tävlingar", cs["meta_description"], body, og="snowboard-box")


def build_gallery():
    figs = "".join(f'<figure class="gal__i gal__i--{i % 5} zoom">{img(g["image"], "(min-width: 900px) 50vw, 100vw")}<figcaption>{e(g["caption"])}</figcaption></figure>'
                   for i, g in enumerate(C["gallery"]))
    body = f"""{hero("galleri", "Galleri", "Bilder från backen, hallen och rampen.", None, "Föreningen")}
<section class="gal">{figs}</section>{cta()}"""
    page("galleri", "Galleri", "Bilder från Uppsala Crew IF: snowboard och freeski i Sunnerstabacken, skateboard på Allis och KAP-rampen.", body)


def build_engage():
    en = C["engage"]
    roles = "".join(f'<li class="role"><span class="role__n num" aria-hidden="true">{i:02d}</span><div><h2 class="role__t">{e(r["title"])}</h2><p>{e(r["text"])}</p></div></li>'
                    for i, r in enumerate(en["roles"], 1))
    body = f"""{hero("engagera-dig", "Engagera dig", en['lead'], "instruktorer", "Föreningen")}
<section class="wrap"><ul class="roles">{roles}</ul></section>
{cta("Hör av dig", "Berätta vad du vill göra, så hittar vi en plats för dig.", "kontakt", "Kontakta oss")}"""
    page("engagera-dig", "Engagera dig", en["meta_description"], body, og="instruktorer")


def build_partners():
    pa = C["partners"]
    fed = "".join(f'<li><a href="{f["url"]}" rel="noopener"><span>{e(f["name"])}</span><span aria-hidden="true">↗</span></a></li>' for f in pa["federations"])
    sp = "".join(f"<li>{e(s)}</li>" for s in pa["sponsors"])
    body = f"""{hero("partners", "Partners och förbund", pa['lead'], None, "Föreningen")}
<section class="sec wrap"><div class="sec__head"><p class="kicker">Förbund och samarbeten</p><h2 class="h2">Anslutna till</h2></div><ul class="rel">{fed}</ul></section>
<section class="sec wrap"><div class="sec__head"><p class="kicker">Sponsorer</p><h2 class="h2">{e(pa['sponsors_note'])}</h2></div><ul class="spons rv">{sp}</ul></section>
{cta("Stötta åkningen i Uppsala", C['engage']['roles'][3]['text'], "kontakt", "Kontakta oss")}"""
    page("partners", "Partners och förbund", pa["meta_description"], body)


def build_join():
    me = C["membership"]
    ben = "".join(f'<li><span class="num">{i:02d}</span><p>{e(b)}</p></li>' for i, b in enumerate(me["benefits"], 1))
    steps = "".join(f"<li>{e(s)}</li>" for s in me["steps"])
    body = f"""{hero("bli-medlem", "Bli medlem", me['price_note'], None, "Medlemskap")}
<section class="nums wrap"><ul><li><span class="num num--xl">{e(me['price'].replace(' per år', ''))}</span><span class="num__l">per år</span></li></ul></section>
<section class="sec wrap"><div class="sec__head"><p class="kicker">Det här ingår</p>{split("Vad du får")}</div><ul class="bens">{ben}</ul></section>
<section class="split2 wrap" id="ansok"><div><p class="kicker">Så går det till</p>{split("Tre steg")}<ol class="steps rv">{steps}</ol></div>
<form class="form" data-mail="{ORG['email']}" data-subject="Medlemsansökan Uppsala Crew IF" action="mailto:{ORG['email']}" method="post" enctype="text/plain">
<h2 class="h3">Medlemsansökan</h2>
<div class="field"><label for="m-namn">Namn</label><input id="m-namn" data-label="Namn" autocomplete="name" required></div>
<div class="field"><label for="m-epost">E-post</label><input id="m-epost" type="email" data-label="E-post" autocomplete="email" required></div>
<div class="field"><label for="m-sport">Vad åker du?</label><select id="m-sport" data-label="Sport"><option value="">Välj</option><option>Skateboard</option><option>Snowboard</option><option>Freeski</option><option>Flera av dem</option></select></div>
<div class="field"><label for="m-belopp">Medlemsavgift</label><select id="m-belopp" data-label="Avgift"><option>50 kr</option><option>75 kr</option><option selected>100 kr</option></select></div>
{consent("m")}
<button class="btn" type="submit">Skicka ansökan <span aria-hidden="true">→</span></button>
<p class="form-status" role="status" aria-live="polite"></p></form></section>"""
    page("bli-medlem", "Bli medlem", me["meta_description"], body)


def build_faq():
    qs = "".join(f'<details class="qa"><summary><span>{e(f["q"])}</span><span class="qa__i" aria-hidden="true"></span></summary><p>{e(f["a"])}</p></details>' for f in C["faq"])
    body = f"""{hero("vanliga-fragor", "Vanliga frågor", "Om medlemskap, försäkring, utrustning och var vi tränar.", None, "Föreningen")}
<section class="wrap faq">{qs}</section>
{cta("Hittar du inte svaret", "Mejla oss så svarar vi.", "kontakt", "Kontakta oss")}"""
    page("vanliga-fragor", "Vanliga frågor", "Svar på vanliga frågor om Uppsala Crew IF: medlemsavgift, försäkring, utrustning, skateskola och träningsplatser.", body, ld=[faq_ld()])


def build_contact():
    body = f"""{hero("kontakt", "Kontakt", "Mejla, ring eller skriv till oss via formuläret.", None, "Hör av dig")}
<section class="wrap contact"><div class="contact__big rv">
<a href="mailto:{ORG['email']}">{ORG['email']}</a><a href="tel:{ORG['phone_href']}">{ORG['phone']}</a></div>
<div class="split2">
<dl class="facts rv"><div><dt>E-post</dt><dd><a href="mailto:{ORG['email']}">{ORG['email']}</a><br><a href="mailto:{ORG['email_alt']}">{ORG['email_alt']}</a></dd></div>
<div><dt>Telefon</dt><dd><a href="tel:{ORG['phone_href']}">{ORG['phone']}</a></dd></div>
<div><dt>Postadress</dt><dd>{e(ORG['legal'])}<br>{e(ORG['street'])}<br>{e(ORG['zip'])} {e(ORG['city'])}</dd></div>
<div><dt>Org.nr</dt><dd>{e(ORG['orgnr'])}</dd></div>
<div><dt>Sociala medier</dt><dd><a href="{ORG['instagram']}" rel="noopener">Instagram</a> · <a href="{ORG['facebook']}" rel="noopener">Facebook</a></dd></div></dl>
<form class="form" data-mail="{ORG['email']}" data-subject="Meddelande via uppsalacrew.se" action="mailto:{ORG['email']}" method="post" enctype="text/plain">
<h2 class="h3">Skriv till oss</h2>
<div class="field"><label for="k-namn">Namn</label><input id="k-namn" data-label="Namn" autocomplete="name" required></div>
<div class="field"><label for="k-epost">E-post</label><input id="k-epost" type="email" data-label="E-post" autocomplete="email" required></div>
<div class="field"><label for="k-amne">Ärende</label><select id="k-amne" data-label="Ärende"><option>Medlemskap</option><option>Skateskola</option><option>Tävlingar</option><option>Engagemang</option><option>Samarbete och sponsring</option><option>Annat</option></select></div>
<div class="field"><label for="k-msg">Meddelande</label><textarea id="k-msg" data-label="Meddelande" rows="5" required></textarea></div>
{consent("k")}
<button class="btn" type="submit">Skicka <span aria-hidden="true">→</span></button>
<p class="form-status" role="status" aria-live="polite"></p></form></div></section>"""
    page("kontakt", "Kontakt", f"Kontakta Uppsala Crew IF på {ORG['email']} eller {ORG['phone']}. Postadress {ORG['street']}, {ORG['zip']} {ORG['city']}.", body,
         ld=[{"@context": "https://schema.org", "@type": "ContactPage", "name": "Kontakt", "about": {"@id": SITE + "/#org"}}])


def build_privacy():
    secs = "".join(f'<section class="pol"><h2 class="h3">{e(p["h"])}</h2><p>{e(p["p"])}</p></section>' for p in C["privacy"])
    body = f"""{hero("integritetspolicy", "Integritetspolicy", "Så behandlar Uppsala Crew IF dina personuppgifter.", None, "Juridik")}
<div class="wrap pols">{secs}</div>"""
    page("integritetspolicy", "Integritetspolicy", "Så behandlar Uppsala Crew IF personuppgifter: vilka uppgifter, varför, hur länge och dina rättigheter.", body)


def build_404():
    body = f"""<section class="hero hero--type hero--404"><div class="wrap"><p class="num num--xl" aria-hidden="true">404</p>
<h1 class="xl">Sidan finns inte</h1><p class="lead">Länken kan vara gammal eller felstavad.</p>
<p><a class="btn" href="{url('')}">Till startsidan <span aria-hidden="true">→</span></a></p></div></section>"""
    page("404", "Sidan hittades inte", "Sidan finns inte.", body)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    here = Path(__file__).parent
    for f in ("site.css", "site.js"):
        shutil.copy(here / f, OUT / "assets" / f)
    build_home(); build_about()
    for s in SPORTS:
        build_sport(s)
    build_girls(); build_places(); build_comps(); build_gallery(); build_engage(); build_partners()
    build_join(); build_faq(); build_contact(); build_privacy(); build_404()
    n = len(list(OUT.rglob("*.html")))
    print(f"{V}: {n} html-filer i {OUT}")


if __name__ == "__main__":
    main()
