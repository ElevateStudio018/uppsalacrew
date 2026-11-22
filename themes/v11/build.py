#!/usr/bin/env python3
"""v11 Förbund – clean koncernstil med avrundade knappar. Kör: python3 themes/v11/build.py"""
import json, html, shutil, os
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
C = json.loads((ROOT / "content/content.json").read_text())
M = json.loads((ROOT / "docs/media/manifest.json").read_text())
OUT = ROOT / "docs/v11"
BASE = os.environ.get("BASE", "/uppsalacrew/v11")
MEDIA = os.environ.get("MEDIA", "/uppsalacrew/media")
SITE = C["org"]["site"]
O = C["org"]
e = lambda s: html.escape(s, quote=True)

def u(slug):
    return f"{BASE}/{slug}/" if slug else f"{BASE}/"

def img(name, sizes="100vw", lazy=True, alt=None):
    m = M[name]
    ss = ", ".join(f"{MEDIA}/{name}-{w}.webp {w}w" for w in m["widths"])
    src = f"{MEDIA}/{name}-{m['widths'][min(1, len(m['widths'])-1)]}.webp"
    la = 'loading="lazy" decoding="async"' if lazy else 'fetchpriority="high"'
    return f'<img src="{src}" srcset="{ss}" sizes="{sizes}" width="{m["w"]}" height="{m["h"]}" alt="{e(alt or m["alt"])}" {la}>'

CHEV = '<svg class="chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M2 4l4 4 4-4" fill="none" stroke="currentColor" stroke-width="2"/></svg>'
ARR = '<span class="arrow" aria-hidden="true"><svg width="16" height="16" viewBox="0 0 16 16"><path d="M3 8h9M8 4l4 4-4 4" fill="none" stroke="currentColor" stroke-width="2"/></svg></span>'
CHECK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="2.4"/></svg>'

NAV = [
    ("Start", "", None),
    ("Sporter", None, [("Skateboard", "skateboard"), ("Snowboard och freeski", "snowboard-och-freeski"), ("Skateskola", "skateskola"), ("Tjejsatsning", "tjejer")]),
    ("Platser", None, [("Alla platser", "platser")] + [(p["title"], f"platser/{p['slug']}") for p in C["places"]]),
    ("Tävlingar", "tavlingar", None),
    ("Föreningen", None, [("Om föreningen", "om-foreningen"), ("Engagera dig", "engagera-dig"), ("Partners och förbund", "partners"), ("Galleri", "galleri"), ("Vanliga frågor", "vanliga-fragor")]),
    ("Kontakt", "kontakt", None),
]
SUB = [("Skateboard", "skateboard"), ("Snowboard", "snowboard-och-freeski"), ("Freeski", "snowboard-och-freeski"), ("Skateskola", "skateskola"), ("Tjejsatsning", "tjejer"), ("Tävlingar", "tavlingar"), ("Bli medlem", "bli-medlem")]

def header(slug):
    items = []
    for i, (label, s, sub) in enumerate(NAV):
        if sub:
            cur = ' aria-current="page"' if any(slug == x[1] for x in sub) else ""
            links = "".join(f'<a href="{u(x[1])}">{e(x[0])}</a>' for x in sub)
            items.append(f'<li class="has-drop"><button class="navlink" aria-expanded="false"{cur}>{label}{CHEV}</button><div class="drop">{links}</div></li>')
        else:
            cur = ' aria-current="page"' if slug == s else ""
            items.append(f'<li><a class="navlink" href="{u(s)}"{cur}>{label}</a></li>')
    subl = "".join(f'<a href="{u(s)}"{" aria-current=\"page\"" if slug == s and l != "Freeski" else ""}>{l}</a>' for l, s in SUB)
    return f"""<a class="skip" href="#innehall">Hoppa till innehållet</a>
<div class="top"><div class="wrap">
<a class="brand" href="{u('')}"><img src="{MEDIA}/logo-ljus-192.png" width="56" height="56" alt=""><span><b>Uppsala Crew IF</b><small>Skateboard · Snowboard · Freeski</small></span></a>
<div class="top__links"><a href="{O['instagram']}" rel="noopener">Instagram</a><a href="tel:{O['phone_href']}">{O['phone']}</a><a class="btn btn--accent btn--sm" href="{u('bli-medlem')}">Bli medlem</a></div>
</div></div>
<nav class="mainnav" aria-label="Huvudmeny"><div class="wrap">
<button class="menu-btn" aria-expanded="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2"/></svg><span>Meny</span></button>
<ul class="mainnav__list">{''.join(items)}</ul>
</div></nav>
<div class="subnav"><div class="wrap">{subl}</div></div>"""

def footer():
    sp = "".join(f'<li><a href="{u(s["slug"])}">{e(s["title"])}</a></li>' for s in C["sports"])
    pl = "".join(f'<li><a href="{u("platser/"+p["slug"])}">{e(p["title"])}</a></li>' for p in C["places"])
    return f"""<footer class="foot"><div class="wrap"><div class="foot__grid">
<div class="foot__brand"><a class="brand" href="{u('')}"><img src="{MEDIA}/logo-rund-192.png" width="56" height="56" alt="Uppsala Crew IF" loading="lazy" style="border-radius:50%"><span><b>Uppsala Crew IF</b><small>Ideell idrottsförening sedan {O['founded']}</small></span></a>
<p style="margin-top:1rem;max-width:34ch">Vi skapar bättre förutsättningar för skateboard, snowboard och freeski i Uppsala.</p></div>
<div><h2>Sporter</h2><ul>{sp}<li><a href="{u('tjejer')}">Tjejsatsning</a></li></ul></div>
<div><h2>Platser</h2><ul>{pl}</ul></div>
<div><h2>Föreningen</h2><ul><li><a href="{u('om-foreningen')}">Om föreningen</a></li><li><a href="{u('tavlingar')}">Tävlingar</a></li><li><a href="{u('engagera-dig')}">Engagera dig</a></li><li><a href="{u('partners')}">Partners och förbund</a></li><li><a href="{u('vanliga-fragor')}">Vanliga frågor</a></li></ul></div>
<div><h2>Kontakt</h2><ul><li><a href="mailto:{O['email']}">{O['email']}</a></li><li><a href="tel:{O['phone_href']}">{O['phone']}</a></li><li style="padding:.28rem 0">{O['street']}, {O['zip']} {O['city']}</li><li><a href="{O['instagram']}" rel="noopener">Instagram</a> · <a href="{O['facebook']}" rel="noopener">Facebook</a></li></ul></div>
</div><div class="foot__legal"><span>© {O['legal']} · Org.nr {O['orgnr']}</span><a href="{u('integritetspolicy')}">Integritetspolicy</a></div></div></footer>"""

def org_ld():
    return {"@context": "https://schema.org", "@type": "SportsOrganization", "@id": SITE + "/#org", "name": O["name"], "legalName": O["legal"],
            "url": SITE + "/", "logo": SITE + "/media/logo-rund-512.png", "foundingDate": O["founded"], "email": O["email"], "telephone": O["phone_href"],
            "identifier": {"@type": "PropertyValue", "propertyID": "Organisationsnummer", "value": O["orgnr"]},
            "address": {"@type": "PostalAddress", "streetAddress": O["street"], "postalCode": O["zip"].replace(" ", ""), "addressLocality": O["city"], "addressCountry": "SE"},
            "sport": ["Skateboarding", "Snowboarding", "Freestyle skiing"], "sameAs": [O["instagram"], O["facebook"]]}

COUNT = [0]
def page(slug, title, desc, body, ld=(), trail=None):
    lds = [org_ld()] + list(ld)
    if trail:
        lds.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{SITE}/{s}/" if s else SITE + "/"} for i, (n, s) in enumerate(trail)]})
    t = title if not slug else f"{title} – Uppsala Crew IF"
    doc = f"""<!doctype html>
<html lang="sv" class="no-js"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(t)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}/{slug + '/' if slug else ''}">
<meta property="og:type" content="website"><meta property="og:locale" content="sv_SE"><meta property="og:site_name" content="Uppsala Crew IF">
<meta property="og:title" content="{e(t)}"><meta property="og:description" content="{e(desc)}"><meta property="og:image" content="{SITE}/media/snowboard-hopp-1600.webp">
<meta name="theme-color" content="#0c2b4b">
<link rel="icon" href="{MEDIA}/logo-rund-64.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=Barlow:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{BASE}/assets/site.css">
<script type="application/ld+json">{json.dumps(lds, ensure_ascii=False)}</script>
</head><body>
{header(slug)}
<main id="innehall">{body}</main>
{footer()}
<script src="{BASE}/assets/site.js" defer></script>
</body></html>"""
    p = OUT / "404.html" if slug == "404" else OUT / (slug + "/index.html" if slug else "index.html")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(doc)
    COUNT[0] += 1

def pagehead(trail, h1, lead, banner=None):
    cr = "".join(f'<li><a href="{u(s)}">{e(n)}</a></li>' if i < len(trail) - 1 else f'<li aria-current="page">{e(n)}</li>' for i, (n, s) in enumerate(trail))
    b = f'<div class="banner">{img(banner, "(min-width:1280px) 1200px, 100vw", lazy=False)}</div>' if banner else ""
    return f"""<section class="pagehead"><div class="wrap"><nav class="crumbs" aria-label="Brödsmulor"><ol>{cr}</ol></nav>
<h1>{e(h1)}</h1><p class="lead">{e(lead)}</p>{b}</div></section>"""

def join_box():
    return f"""<aside class="box box--navy"><h2>Bli medlem</h2><p>{C['membership']['price']}. {C['membership']['price_note']}</p><a class="btn btn--accent" href="{u('bli-medlem')}">Bli medlem</a></aside>"""

def contact_box():
    return f"""<aside class="box"><h2>Frågor</h2><dl><dt>E-post</dt><dd><a href="mailto:{O['email']}">{O['email']}</a></dd><dt>Telefon</dt><dd><a href="tel:{O['phone_href']}">{O['phone']}</a></dd><dt>Nyheter</dt><dd><a href="{O['instagram']}" rel="noopener">{O['instagram_handle']}</a></dd></dl></aside>"""

def mailform(kind):
    if kind == "join":
        fields = f"""<div class="field"><label for="f-n">Namn</label><input id="f-n" data-label="Namn" autocomplete="name" required></div>
<div class="field"><label for="f-e">E-post</label><input id="f-e" type="email" data-label="E-post" autocomplete="email" required></div>
<div class="field"><label for="f-s">Vad åker du?</label><select id="f-s" data-label="Sport"><option value="">Välj</option><option>Skateboard</option><option>Snowboard</option><option>Freeski</option><option>Flera</option></select></div>
<div class="field"><label for="f-a">Medlemsavgift</label><select id="f-a" data-label="Avgift"><option>50 kr</option><option>75 kr</option><option selected>100 kr</option></select></div>"""
        h, subj, btn = "Medlemsansökan", "Medlemsansökan Uppsala Crew IF", "Skicka ansökan"
    else:
        fields = f"""<div class="field"><label for="f-n">Namn</label><input id="f-n" data-label="Namn" autocomplete="name" required></div>
<div class="field"><label for="f-e">E-post</label><input id="f-e" type="email" data-label="E-post" autocomplete="email" required></div>
<div class="field"><label for="f-t">Ärende</label><select id="f-t" data-label="Ärende"><option>Medlemskap</option><option>Skateskola</option><option>Tävlingar</option><option>Engagera mig</option><option>Samarbete och sponsring</option><option>Annat</option></select></div>
<div class="field"><label for="f-m">Meddelande</label><textarea id="f-m" data-label="Meddelande" required></textarea></div>"""
        h, subj, btn = "Skicka ett meddelande", "Meddelande via uppsalacrew.se", "Skicka meddelande"
    return f"""<form class="form" data-mail="{O['email']}" data-subject="{subj}" action="mailto:{O['email']}" method="post" enctype="text/plain">
<h2>{h}</h2>{fields}
<label class="check"><input type="checkbox" required><span>Jag godkänner att föreningen sparar mina uppgifter enligt <a href="{u('integritetspolicy')}">integritetspolicyn</a>.</span></label>
<button class="btn btn--accent" type="submit">{btn}</button><p class="status" role="status" aria-live="polite"></p></form>"""

def sport_card(s, tag):
    return f"""<a class="card rv" href="{u(s['slug'])}">{img(s['hero'], '(min-width:1024px) 400px, (min-width:700px) 50vw, 100vw')}
<div class="card__body"><span class="card__tag">{tag}</span><h3>{e(s['title'])}</h3><p>{e(s['short'])}</p>
<dl><dt>Var</dt><dd>{e(s['where'])}</dd><dt>När</dt><dd>{e(s['when'])}</dd></dl><span class="more">Läs mer →</span></div></a>"""

# ------------------------------------------------------------------ sidor
def home():
    f = "".join(f'<div><dt>{e(x["label"])}</dt><dd>{e(x["value"])}</dd></div>' for x in C["facts"])
    f = f.replace("Skateboard, snowboard, freeski", "Skate · Snow · Freeski").replace("Ingår på föreningens aktiviteter", "Ingår för medlemmar")
    promos = [
        ("Skateskola", "Måndagar 18.00–19.00 på KAP-rampen, inomhus på Allis när det blir kallt.", "allis-hall-2", "skateskola", "Om skateskolan"),
        ("Sunnerstabacken", "Funpark, utrustning att låna och coachning av våra instruktörer.", "kvallshopp", "platser/sunnerstabacken", "Om backen"),
        ("Fler tjejer i parken", C["girls"]["lead"], "tjejer-skate", "tjejer", "Om tjejsatsningen"),
    ]
    pr = "".join(f"""<article class="promo rv">{img(i, '(min-width:800px) 33vw, 100vw')}<div class="promo__body"><h3>{t}</h3><p>{e(d)}</p><a class="btn btn--white btn--sm" href="{u(s)}">{b}</a></div></article>""" for t, d, i, s, b in promos)
    cards = "".join(sport_card(s, t) for s, t in zip(C["sports"], ["Året runt", "Vinter", "Barn och unga"]))
    comps = "".join(f"""<a class="card rv" href="{u('tavlingar')}">{img(c['image'], '(min-width:700px) 50vw, 100vw')}<div class="card__body"><span class="card__tag">{e(c['sport'])}</span><h3>{e(c['title'])}</h3><p>{e(c['text'])}</p><dl><dt>Plats</dt><dd>{e(c['place'])}</dd><dt>Klasser</dt><dd>{e(', '.join(c['classes']))}</dd></dl></div></a>""" for c in C["competitions"]["items"])
    pl = "".join(f'<li><a href="{u("platser/"+p["slug"])}"><div><h3>{e(p["title"])}</h3><p>{e(p["short"])}</p></div>{ARR}</a></li>' for p in C["places"])
    faq = "".join(f'<details><summary>{e(q["q"])}</summary><p>{e(q["a"])}</p></details>' for q in C["faq"][:5])
    ben = "".join(f"<li>{CHECK}<span>{e(b)}</span></li>" for b in C["membership"]["benefits"])
    fed = "".join(f'<a href="{x["url"]}" rel="noopener">{e(x["name"])}</a>' for x in C["partners"]["federations"])
    body = f"""
<section class="hero"><div class="wrap">
<div class="hero__box">{img('snowboard-hopp', '(min-width:1280px) 1200px, 100vw', lazy=False)}
<div class="hero__plate"><p class="kicker">Ideell idrottsförening i Uppsala</p><h1>{e(C['intro']['headline'])}</h1><p>{e(C['intro']['lead'])}</p>
<div class="hero__actions"><a class="btn btn--accent" href="{u('bli-medlem')}">Bli medlem</a><a class="btn btn--white" href="{u('om-foreningen')}">Om föreningen</a></div></div></div>
<dl class="facts">{f}</dl></div></section>

<section class="sec sec--tight"><div class="wrap"><div class="promos">{pr}</div></div></section>

<section class="sec"><div class="wrap"><div class="sechead"><h2>Våra sporter</h2></div><div class="cards cards--3">{cards}</div></div></section>

<section class="sec sec--ice"><div class="wrap"><div class="sechead"><h2>Tävlingar</h2><a href="{u('tavlingar')}">Alla tävlingar</a></div>
<p style="max-width:62ch;margin-bottom:2rem">{e(C['competitions']['lead'])}</p><div class="cards">{comps}</div></div></section>

<section class="sec"><div class="wrap"><div class="two">
<div><div class="sechead"><h2>Platser</h2><a href="{u('platser')}">Alla platser</a></div><ul class="list">{pl}</ul></div>
<div><div class="sechead"><h2>Vanliga frågor</h2><a href="{u('vanliga-fragor')}">Fler frågor</a></div><div class="faq">{faq}</div></div>
</div></div></section>

<section class="sec sec--tight"><div class="wrap"><div class="join rv">
<div><h2>Bli medlem i Uppsala Crew IF</h2><p class="price">50–100 kr</p><p style="color:#d7e2ee;margin:0 0 1.5rem">per år. {C['membership']['price_note']}</p><a class="btn btn--accent" href="{u('bli-medlem')}">Bli medlem</a></div>
<ul>{ben}</ul></div></div></section>

<section class="sec"><div class="wrap"><div class="sechead"><h2>Förbund och samarbeten</h2><a href="{u('partners')}">Alla partners</a></div><div class="partners">{fed}</div></div></section>"""
    page("", "Uppsala Crew IF – skateboard, snowboard och freeski i Uppsala",
         "Uppsala Crew IF är Uppsalas ideella förening för skateboard, snowboard och freeski. Skateskola, tävlingar och åkning på Allis, KAP-rampen och i Sunnerstabacken. Bli medlem för 50–100 kr per år.", body)

def sport_pages():
    for s in C["sports"]:
        tr = [("Start", ""), (s["title"], s["slug"])]
        secs = "".join(f'<h2>{e(x["h"])}</h2>' + "".join(f"<p>{e(p)}</p>" for p in x["p"]) for x in s["sections"])
        imgs = [i for i in s.get("images", []) if i in M][:2]
        duo = f'<div class="duo">{"".join(img(i, "(min-width:700px) 40vw, 100vw") for i in imgs)}</div>' if len(imgs) == 2 else ""
        facts = s.get("schedule") or [{"k": "Var", "v": s["where"]}, {"k": "När", "v": s["when"]}]
        fl = "".join(f"<dt>{e(x['k'])}</dt><dd>{e(x['v'])}</dd>" for x in facts)
        body = pagehead(tr, s["title"], s["short"], s["hero"]) + f"""<section class="sec"><div class="wrap"><div class="two two--main">
<div class="prose">{secs}{duo}</div><div class="side"><aside class="box"><h2>Fakta</h2><dl>{fl}</dl><a class="btn btn--navy" href="{u('kontakt')}">Kontakta oss</a></aside>{join_box()}</div></div></div></section>"""
        page(s["slug"], s["title"] + " i Uppsala", s["meta_description"], body, trail=tr,
             ld=[{"@context": "https://schema.org", "@type": "Service", "name": s["title"], "provider": {"@id": SITE + "/#org"}, "areaServed": "Uppsala"}])

def girls():
    g = C["girls"]; tr = [("Start", ""), (g["title"], "tjejer")]
    secs = "".join(f'<h2>{e(x["h"])}</h2>' + "".join(f"<p>{e(p)}</p>" for p in x["p"]) for x in g["sections"])
    body = pagehead(tr, g["title"], g["lead"]) + f"""<section class="sec"><div class="wrap"><div class="two two--main">
<div class="prose">{secs}<div class="duo">{img('tjejer-skate','(min-width:700px) 40vw, 100vw')}{img('freeski-hopp','(min-width:700px) 40vw, 100vw')}</div></div>
<div class="side"><aside class="box"><h2>Vill du vara med?</h2><p>Som ledare, förebild eller deltagare. Hör av dig så berättar vi mer.</p><a class="btn btn--navy" href="{u('kontakt')}">Kontakta oss</a></aside>{join_box()}</div></div></div></section>"""
    page("tjejer", g["title"], g["meta_description"], body, trail=tr)

def places():
    tr = [("Start", ""), ("Platser", "platser")]
    cards = ""
    for p in C["places"]:
        im = img(p["image"], "(min-width:700px) 50vw, 100vw") if p["image"] else ""
        cards += f'<a class="card rv" href="{u("platser/"+p["slug"])}">{im}<div class="card__body"><span class="card__tag">{e(p["address"])}</span><h3>{e(p["title"])}</h3><p>{e(p["short"])}</p><span class="more">Läs mer →</span></div></a>'
    cards += '<div class="card"><div class="card__body"><span class="card__tag">Uppsala</span><h3>Kapellgärdet</h3><p>Området vid KAP-rampen där vi också håller till under skateboardsäsongen.</p></div></div>'
    body = pagehead(tr, "Platser", "Här åker vi i Uppsala. Utomhus på sommaren, inomhus när det blir kallt och i backen på vintern.") + f'<section class="sec"><div class="wrap"><div class="cards">{cards}</div></div></section>'
    page("platser", "Platser", "Var Uppsala Crew IF åker: Sunnerstabacken, Allis Uppsala, KAP-rampen och Kapellgärdet.", body, trail=tr)
    for p in C["places"]:
        t2 = tr + [(p["title"], "platser/" + p["slug"])]
        prose = "".join(f"<p>{e(x)}</p>" for x in p["body"])
        q = p["address"].replace(" ", "+")
        body = pagehead(t2, p["title"], p["short"], p["image"]) + f"""<section class="sec"><div class="wrap"><div class="two two--main"><div class="prose">{prose}</div>
<div class="side"><aside class="box"><h2>Hitta hit</h2><dl><dt>Adress</dt><dd>{e(p['address'])}</dd></dl><a class="btn btn--navy" href="https://www.google.com/maps/search/?api=1&amp;query={e(q)}" rel="noopener">Visa på karta</a></aside>{join_box()}</div></div></div></section>"""
        page("platser/" + p["slug"], p["title"] + ", Uppsala", f"{p['title']}: {p['short']}", body, trail=t2,
             ld=[{"@context": "https://schema.org", "@type": "SportsActivityLocation", "name": p["title"], "address": {"@type": "PostalAddress", "streetAddress": p["address"], "addressLocality": "Uppsala", "addressCountry": "SE"}}])

def competitions():
    c = C["competitions"]; tr = [("Start", ""), ("Tävlingar", "tavlingar")]
    cards = "".join(f"""<article class="card rv">{img(x['image'], '(min-width:700px) 50vw, 100vw')}<div class="card__body"><span class="card__tag">{e(x['sport'])}</span><h2 style="font-size:1.8rem;color:var(--navy);margin:.25rem 0 .5rem">{e(x['title'])}</h2><p>{e(x['text'])}</p><dl><dt>Plats</dt><dd>{e(x['place'])}</dd><dt>Klasser</dt><dd>{e(', '.join(x['classes']))}</dd></dl></div></article>""" for x in c["items"])
    body = pagehead(tr, "Tävlingar", c["lead"]) + f"""<section class="sec"><div class="wrap"><div class="cards">{cards}</div>
<div class="box" style="margin-top:2rem;display:flex;flex-wrap:wrap;gap:1rem;align-items:center;justify-content:space-between"><p style="margin:0;max-width:60ch">Datum för kommande tävlingar och anmälan publiceras på Instagram. Medlemmar har fritt tillträde.</p><a class="btn btn--navy" href="{O['instagram']}" rel="noopener">Följ {O['instagram_handle']}</a></div></div></section>"""
    page("tavlingar", "Tävlingar", c["meta_description"], body, trail=tr)

def about():
    a = C["about"]; tr = [("Start", ""), ("Om föreningen", "om-foreningen")]
    tl = "".join(f'<li><b>{x["year"]}</b>{e(x["text"])}</li>' for x in a["timeline"])
    body = pagehead(tr, "Om föreningen", a["lead"], "instruktorer") + f"""<section class="sec"><div class="wrap"><div class="two two--main">
<div class="prose"><h2>Vision</h2><p>{e(a['vision'])}</p><h2>Historik</h2><ol class="timeline">{tl}</ol><h2>Organisation</h2><p>{e(a['org_text'])}</p><p>Vill du hjälpa till? <a href="{u('engagera-dig')}">Läs om hur du kan engagera dig</a>.</p></div>
<div class="side"><aside class="box"><h2>Föreningsfakta</h2><dl><dt>Namn</dt><dd>{O['legal']}</dd><dt>Org.nr</dt><dd>{O['orgnr']}</dd><dt>Grundad</dt><dd>{O['founded']}</dd><dt>Säte</dt><dd>Uppsala</dd></dl></aside>{join_box()}</div></div></div></section>"""
    page("om-foreningen", "Om föreningen", a["meta_description"], body, trail=tr)

def gallery():
    tr = [("Start", ""), ("Galleri", "galleri")]
    g = "".join(f'<figure class="rv">{img(x["image"], "(min-width:900px) 33vw, 50vw")}<figcaption>{e(x["caption"])}</figcaption></figure>' for x in C["gallery"] if x["image"] in M)
    body = pagehead(tr, "Galleri", "Bilder från backen, rampen och hallen. Fler bilder finns på Instagram.") + f'<section class="sec"><div class="wrap"><div class="gallery">{g}</div><p style="margin-top:2rem"><a class="btn btn--navy" href="{O["instagram"]}" rel="noopener">Fler bilder på Instagram</a></p></div></section>'
    page("galleri", "Galleri", "Bilder från Uppsala Crew IF: skateboard, snowboard och freeski i Uppsala.", body, trail=tr)

def engage():
    g = C["engage"]; tr = [("Start", ""), ("Engagera dig", "engagera-dig")]
    r = "".join(f'<div class="role rv"><h2 style="font-size:1.4rem;color:var(--navy);margin-bottom:.4rem">{e(x["title"])}</h2><p>{e(x["text"])}</p></div>' for x in g["roles"])
    body = pagehead(tr, "Engagera dig", g["lead"]) + f"""<section class="sec"><div class="wrap"><div class="two two--main"><div class="roles">{r}</div><div class="side">{contact_box()}</div></div></div></section>"""
    page("engagera-dig", "Engagera dig", g["meta_description"], body, trail=tr)

def partners():
    p = C["partners"]; tr = [("Start", ""), ("Partners och förbund", "partners")]
    fed = "".join(f'<a href="{x["url"]}" rel="noopener">{e(x["name"])}</a>' for x in p["federations"])
    sp = "".join(f"<span>{e(x)}</span>" for x in p["sponsors"])
    body = pagehead(tr, "Partners och förbund", p["lead"]) + f"""<section class="sec"><div class="wrap"><div class="two two--main"><div>
<div class="sechead"><h2>Förbund och samarbeten</h2></div><div class="partners" style="margin-bottom:3rem">{fed}</div>
<div class="sechead"><h2>Sponsorer</h2></div><p class="muted">{e(p['sponsors_note'])}</p><div class="partners">{sp}</div></div>
<div class="side"><aside class="box"><h2>Bli partner</h2><p>Företag som vill stötta skate-, snow- och freeskiåkning i Uppsala är välkomna att kontakta oss.</p><a class="btn btn--navy" href="{u('kontakt')}">Kontakta oss</a></aside></div></div></div></section>"""
    page("partners", "Partners och förbund", p["meta_description"], body, trail=tr)

def membership():
    m = C["membership"]; tr = [("Start", ""), ("Bli medlem", "bli-medlem")]
    ben = "".join(f"<li>{CHECK}<span>{e(b)}</span></li>" for b in m["benefits"])
    st = "".join(f"<li><span>{e(s)}</span></li>" for s in m["steps"])
    body = pagehead(tr, "Bli medlem", f"Medlemsavgiften är {m['price']}. {m['price_note']}") + f"""<section class="sec"><div class="wrap"><div class="two">
<div class="prose"><h2>Det här ingår</h2><ul class="checks">{ben}</ul><h2>Så går det till</h2><ol class="steps">{st}</ol></div>
<div>{mailform('join')}</div></div></div></section>"""
    page("bli-medlem", "Bli medlem", m["meta_description"], body, trail=tr)

def faq():
    tr = [("Start", ""), ("Vanliga frågor", "vanliga-fragor")]
    f = "".join(f'<details><summary>{e(q["q"])}</summary><p>{e(q["a"])}</p></details>' for q in C["faq"])
    body = pagehead(tr, "Vanliga frågor", "Svar på det vi oftast får frågor om. Hittar du inte svaret, mejla oss.") + f'<section class="sec"><div class="wrap"><div class="two two--main"><div class="faq">{f}</div><div class="side">{contact_box()}{join_box()}</div></div></div></section>'
    page("vanliga-fragor", "Vanliga frågor", "Vanliga frågor om medlemskap, försäkring, utrustning och träning i Uppsala Crew IF.", body, trail=tr,
         ld=[{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in C["faq"]]}])

def contact():
    tr = [("Start", ""), ("Kontakt", "kontakt")]
    body = pagehead(tr, "Kontakt", "Du når oss enklast via e-post. För senaste nytt om träningar och tävlingar, följ oss på Instagram.") + f"""<section class="sec"><div class="wrap"><div class="two">
<div>{mailform('contact')}</div>
<div class="side"><aside class="box box--navy"><h2>Kontaktuppgifter</h2><dl><dt>E-post</dt><dd><a href="mailto:{O['email']}" style="color:#fff">{O['email']}</a></dd><dt>Telefon</dt><dd><a href="tel:{O['phone_href']}" style="color:#fff">{O['phone']}</a></dd><dt>Post</dt><dd>{O['street']}<br>{O['zip']} {O['city']}</dd><dt>Org.nr</dt><dd>{O['orgnr']}</dd></dl></aside>
<aside class="box"><h2>Sociala medier</h2><dl><dt>Instagram</dt><dd><a href="{O['instagram']}" rel="noopener">{O['instagram_handle']}</a></dd><dt>Facebook</dt><dd><a href="{O['facebook']}" rel="noopener">Uppsala Crew IF</a></dd></dl></aside></div></div></div></section>"""
    page("kontakt", "Kontakt", f"Kontakta Uppsala Crew IF på {O['email']} eller {O['phone']}. Org.nr {O['orgnr']}.", body, trail=tr)

def privacy():
    tr = [("Start", ""), ("Integritetspolicy", "integritetspolicy")]
    p = "".join(f'<h2>{e(x["h"])}</h2><p>{e(x["p"])}</p>' for x in C["privacy"])
    body = pagehead(tr, "Integritetspolicy", "Så hanterar Uppsala Crew IF personuppgifter enligt dataskyddsförordningen.") + f'<section class="sec"><div class="wrap"><div class="prose">{p}</div></div></section>'
    page("integritetspolicy", "Integritetspolicy", "Så hanterar Uppsala Crew IF dina personuppgifter enligt GDPR.", body, trail=tr)

if __name__ == "__main__":
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    shutil.copy(HERE / "site.css", OUT / "assets/site.css")
    shutil.copy(HERE / "site.js", OUT / "assets/site.js")
    home(); sport_pages(); girls(); places(); competitions(); about(); gallery(); engage(); partners(); membership(); faq(); contact(); privacy()
    page("404", "Sidan finns inte", "Sidan kunde inte hittas.", pagehead([("Start", ""), ("Sidan finns inte", "404")], "Sidan finns inte", "Sidan kan ha flyttats när webbplatsen gjordes om.") + f'<section class="sec"><div class="wrap"><a class="btn btn--accent" href="{u("")}">Till startsidan</a></div></section>')
    print(f"v11: {COUNT[0]} sidor")
