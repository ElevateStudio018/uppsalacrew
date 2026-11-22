#!/usr/bin/env python3
"""v07 Retro 90 – Uppsala Crew IF. Kör: python3 themes/v07/build.py"""
import json, html, shutil
from pathlib import Path

V = "v07"
ROOT = Path(__file__).resolve().parents[2]
C = json.loads((ROOT / "content/content.json").read_text(encoding="utf-8"))
M = json.loads((ROOT / "docs/media/manifest.json").read_text(encoding="utf-8"))
# diy-spot innehåller en daterad affisch (årsmöte) och visas därför inte
for _s in C["sports"]:
    _s["images"] = [x for x in _s["images"] if x != "diy-spot"]
C["gallery"] = [g for g in C["gallery"] if g["image"] != "diy-spot"]
OUT = ROOT / "docs" / V
B = f"/uppsalacrew/{V}"
MEDIA = "/uppsalacrew/media"
SITE = "https://www.uppsalacrew.se"
O = C["org"]
PAGES = {p["slug"]: p for p in C["pages"]}
FONTS = "https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;800&family=Bungee&display=swap"


def e(s):
    return html.escape(str(s), quote=True)


def u(slug):
    return f"{B}/{slug}/" if slug else f"{B}/"


def img(name, sizes="100vw", lazy=True, cls="", alt=None):
    m = M[name]
    srcset = ", ".join(f"{MEDIA}/{name}-{w}.webp {min(w, m['w'])}w" for w in m["widths"])
    src = f"{MEDIA}/{name}-{m['widths'][min(1, len(m['widths']) - 1)]}.webp"
    la = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{src}" srcset="{srcset}" sizes="{sizes}" width="{m["w"]}" height="{m["h"]}"'
            f' alt="{e(alt if alt is not None else m["alt"])}"{la}>')


def P(ps):
    return "".join(f"<p>{e(p)}</p>" for p in ps)


# ---------- dekor ----------
SHAPES = {
    "tri": '<svg viewBox="0 0 100 100" aria-hidden="true" focusable="false"><path d="M50 8 94 88H6Z" fill="var(--teal)" stroke="var(--ink)" stroke-width="5" stroke-linejoin="round"/></svg>',
    "circ": '<svg viewBox="0 0 100 100" aria-hidden="true" focusable="false"><circle cx="50" cy="50" r="40" fill="none" stroke="var(--teal)" stroke-width="14"/><circle cx="50" cy="50" r="40" fill="none" stroke="var(--ink)" stroke-width="3" stroke-dasharray="6 10"/></svg>',
    "zig": '<svg viewBox="0 0 200 40" aria-hidden="true" focusable="false"><path d="M4 30 24 10 44 30 64 10 84 30 104 10 124 30 144 10 164 30 184 10 196 22" fill="none" stroke="var(--teal)" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "dot": '<svg viewBox="0 0 100 100" aria-hidden="true" focusable="false"><circle cx="50" cy="50" r="30" fill="var(--teal)" stroke="var(--ink)" stroke-width="5"/></svg>',
    "sq": '<svg viewBox="0 0 100 100" aria-hidden="true" focusable="false"><rect x="18" y="18" width="64" height="64" fill="none" stroke="var(--ink)" stroke-width="5"/><rect x="30" y="30" width="64" height="64" fill="var(--teal)" opacity=".9"/></svg>',
}


def shape(kind, cls):
    return f'<span class="shape {cls}">{SHAPES[kind]}</span>'


ZIG = f'<div class="zigline" aria-hidden="true">{SHAPES["zig"]}{SHAPES["zig"]}{SHAPES["zig"]}</div>'

# ---------- nav ----------
GROUPS = [
    ("Sporter", ["skateboard", "snowboard-och-freeski", "skateskola"]),
    ("Platser", ["platser", "platser/sunnerstabacken", "platser/allis-uppsala", "platser/kap-rampen"]),
    ("Föreningen", ["om-foreningen", "tjejer", "tavlingar", "galleri", "engagera-dig", "partners", "vanliga-fragor"]),
    ("Kontakt", ["kontakt", "bli-medlem"]),
]
TOP = [("skateboard", "Skate"), ("snowboard-och-freeski", "Snö"), ("platser", "Platser"), ("tavlingar", "Tävlingar"), ("kontakt", "Kontakt")]


def header(slug):
    top = "".join(f'<li><a href="{u(s)}"{" aria-current=\"page\"" if s == slug else ""}>{t}</a></li>' for s, t in TOP)
    groups = ""
    for g, items in GROUPS:
        li = "".join(f'<li><a href="{u(s)}"{" aria-current=\"page\"" if s == slug else ""}>{e(PAGES[s]["title"])}</a></li>' for s in items)
        groups += f'<div class="menu__g"><p class="menu__h">{g}</p><ul>{li}</ul></div>'
    return f"""<a class="skip" href="#main">Hoppa till innehållet</a>
<header class="hd"><div class="wrap hd__in">
<a class="brand" href="{u('')}"><img src="{MEDIA}/logo-ljus-192.png" width="192" height="192" alt=""><span>Uppsala Crew</span></a>
<nav aria-label="Huvudmeny" class="hd__nav"><ul>{top}</ul></nav>
<a class="btn btn--sm hd__cta" href="{u('bli-medlem')}">Bli medlem</a>
<button class="menubtn" type="button" aria-expanded="false" aria-controls="menu"><span class="menubtn__bars" aria-hidden="true"></span><span class="menubtn__t">Meny</span></button>
</div>
<div class="menu" id="menu" hidden><div class="wrap menu__in">{shape('tri','menu__s1')}{shape('circ','menu__s2')}<div class="menu__grid">{groups}</div></div></div>
</header>"""


def footer():
    sp = " · ".join(e(PAGES[s]["title"]) for s in [])
    links = "".join(f'<li><a href="{u(s)}">{e(PAGES[s]["title"])}</a></li>' for s in ["om-foreningen", "bli-medlem", "vanliga-fragor", "partners", "integritetspolicy"])
    return f"""<footer class="ft"><div class="ft__zig" aria-hidden="true"></div><div class="wrap ft__grid">
<div><img class="ft__logo" src="{MEDIA}/logo-rund-192.png" width="96" height="96" alt="Uppsala Crew IF logotyp" loading="lazy"><p class="ft__name">{e(O['legal'])}</p><p>{e(O['tagline'])}.</p><p>Org.nr {e(O['orgnr'])}</p></div>
<div><p class="ft__h">Kontakt</p><ul><li><a href="mailto:{O['email']}">{O['email']}</a></li><li><a href="tel:{O['phone_href']}">{O['phone']}</a></li><li>{e(O['street'])}, {e(O['zip'])} {e(O['city'])}</li></ul></div>
<div><p class="ft__h">Följ oss</p><ul><li><a href="{O['instagram']}" rel="noopener">Instagram {e(O['instagram_handle'])}</a></li><li><a href="{O['facebook']}" rel="noopener">Facebook</a></li></ul></div>
<div><p class="ft__h">Föreningen</p><ul>{links}</ul></div>
</div><div class="wrap ft__base"><p>Förhandsvisning, tema v07 Retro 90.</p></div></footer>"""


# ---------- JSON-LD ----------
ORG_LD = {
    "@context": "https://schema.org", "@type": "SportsOrganization", "@id": SITE + "/#org",
    "name": O["name"], "legalName": O["legal"], "url": SITE + "/", "logo": SITE + "/media/logo-rund-512.png",
    "email": O["email"], "telephone": O["phone_href"], "foundingDate": O["founded"],
    "sport": ["Skateboarding", "Snowboarding", "Freestyle skiing"],
    "address": {"@type": "PostalAddress", "streetAddress": O["street"], "postalCode": O["zip"], "addressLocality": O["city"], "addressCountry": "SE"},
    "sameAs": [O["instagram"], O["facebook"]],
}


def crumbs_ld(slug):
    items = [("Start", SITE + "/")]
    parts = slug.split("/")
    for i in range(len(parts)):
        s = "/".join(parts[: i + 1])
        items.append((PAGES[s]["title"], f"{SITE}/{s}/"))
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": url} for i, (n, url) in enumerate(items)]}


def crumbs_html(slug):
    if not slug:
        return ""
    parts = slug.split("/")
    out = [f'<li><a href="{u("")}">Start</a></li>']
    for i in range(len(parts)):
        s = "/".join(parts[: i + 1])
        if i == len(parts) - 1:
            out.append(f'<li aria-current="page">{e(PAGES[s]["title"])}</li>')
        else:
            out.append(f'<li><a href="{u(s)}">{e(PAGES[s]["title"])}</a></li>')
    return f'<nav class="crumbs" aria-label="Brödsmulor"><ol>{"".join(out)}</ol></nav>'


# ---------- sida ----------
def write(slug, title, desc, body, ld=None, og_img="snowboard-hopp"):
    lds = [ORG_LD] + ([crumbs_ld(slug)] if slug and slug != "404" else []) + (ld or [])
    canon = f"{SITE}/{slug}/" if slug and slug != "404" else SITE + "/"
    full_title = f"{title} | {O['name']}" if slug else f"{O['name']} – {C['intro']['headline']}"
    ogi = f"{SITE}/media/{og_img}-960.webp"
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    doc = f"""<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:locale" content="sv_SE"><meta property="og:site_name" content="{e(O['name'])}">
<meta property="og:title" content="{e(full_title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canon}"><meta property="og:image" content="{ogi}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FFF7EA">
<link rel="icon" href="{MEDIA}/logo-rund-64.png" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{B}/assets/site.css">
{ld_html}
</head>
<body>
{header(slug)}
<main id="main" tabindex="-1">
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


def pagehead(slug, kicker, h1, lead, image=None, shapes=("tri", "circ")):
    pic = f'<figure class="ph__img frame pop" style="--r:2deg">{img(image, "(min-width: 900px) 44vw, 100vw", lazy=False)}</figure>' if image else ""
    return f"""<section class="ph{' ph--img' if image else ''}"><div class="wrap">{crumbs_html(slug)}
<div class="ph__grid"><div class="ph__txt">{shape(shapes[0],'ph__s1')}{shape(shapes[1],'ph__s2')}<p class="kicker">{e(kicker)}</p><h1>{e(h1)}</h1><p class="lead">{e(lead)}</p></div>{pic}</div></div></section>"""


def btn(href, text, ghost=False):
    return f'<a class="btn{" btn--ghost" if ghost else ""}" href="{href}">{e(text)}</a>'


def join_band():
    m = C["membership"]
    return f"""<section class="band"><div class="wrap band__in">{shape('dot','band__s1')}{shape('tri','band__s2')}
<div><p class="kicker kicker--inv">Medlemskap</p><h2>{e(m['price'])}</h2><p>{e(m['price_note'])} Olycksfallsförsäkring och fritt tillträde till föreningens evenemang ingår.</p></div>
<p class="band__cta">{btn(u('bli-medlem'), 'Bli medlem')}</p></div></section>"""


def form(kind):
    if kind == "join":
        subj, idp = "Medlemsansökan Uppsala Crew IF", "m"
        fields = f"""<div class="field"><label for="m-namn">Namn</label><input id="m-namn" name="namn" data-label="Namn" autocomplete="name" required></div>
<div class="field"><label for="m-epost">E-post</label><input id="m-epost" name="epost" type="email" data-label="E-post" autocomplete="email" required></div>
<div class="field"><label for="m-sport">Vad åker du?</label><select id="m-sport" name="sport" data-label="Sport"><option value="">Välj</option><option>Skateboard</option><option>Snowboard</option><option>Freeski</option><option>Flera av dem</option></select></div>
<div class="field"><label for="m-belopp">Medlemsavgift</label><select id="m-belopp" name="belopp" data-label="Avgift"><option>50 kr</option><option>75 kr</option><option selected>100 kr</option></select></div>"""
        label = "Skicka ansökan"
    else:
        subj, idp = "Meddelande via uppsalacrew.se", "k"
        fields = """<div class="field"><label for="k-namn">Namn</label><input id="k-namn" name="namn" data-label="Namn" autocomplete="name" required></div>
<div class="field"><label for="k-epost">E-post</label><input id="k-epost" name="epost" type="email" data-label="E-post" autocomplete="email" required></div>
<div class="field field--wide"><label for="k-msg">Meddelande</label><textarea id="k-msg" name="meddelande" rows="5" data-label="Meddelande" required></textarea></div>"""
        label = "Skicka meddelande"
    return f"""<form class="form card" data-mail="{O['email']}" data-subject="{subj}" action="mailto:{O['email']}" method="post" enctype="text/plain" novalidate>
{fields}
<label class="check"><input type="checkbox" id="{idp}-ok" required><span>Jag godkänner att föreningen sparar mina uppgifter enligt <a href="{u('integritetspolicy')}">integritetspolicyn</a>.</span></label>
<button class="btn" type="submit">{label}</button>
<p class="form__status" role="status" aria-live="polite"></p>
<p class="form__note">Formuläret öppnar ditt e-postprogram med uppgifterna ifyllda.</p>
</form>"""


# ---------- sidor ----------
def home():
    i = C["intro"]
    rot = ["-2deg", "1.5deg", "-1deg"]
    sports = ""
    for n, s in enumerate(C["sports"]):
        sports += f"""<li class="scard pop" style="--r:{rot[n]}"><a href="{u(s['slug'])}">
<span class="scard__img frame">{img(s['hero'], '(min-width: 900px) 30vw, 100vw')}</span>
<span class="scard__no" aria-hidden="true">0{n+1}</span><span class="scard__t">{e(s['title'])}</span>
<span class="scard__p">{e(s['short'])}</span><span class="scard__meta">{e(s['when'])}</span></a></li>"""
    places = ""
    for n, p in enumerate(C["places"]):
        places += f"""<li class="pl pop" style="--r:{['1deg','-1.5deg','1deg'][n]}"><a href="{u('platser/' + p['slug'])}"><span class="pl__n" aria-hidden="true">{chr(65+n)}</span><span><span class="pl__t">{e(p['title'])}</span><span class="pl__p">{e(p['short'])}</span></span></a></li>"""
    facts = "".join(f'<li class="fact pop" style="--r:{["-3deg","2deg","-1deg","3deg"][n]}"><span class="fact__l">{e(f["label"])}</span><span class="fact__v">{e(f["value"])}</span></li>' for n, f in enumerate(C["facts"]))
    comps = ""
    for n, c in enumerate(C["competitions"]["items"]):
        comps += f"""<article class="comp pop" style="--r:{['-1deg','1deg'][n]}"><div class="comp__img frame">{img(c['image'], '(min-width: 900px) 40vw, 100vw')}</div>
<div class="comp__b"><p class="kicker">{e(c['sport'])} · {e(c['place'])}</p><h3>{e(c['title'])}</h3><p>{e(c['text'])}</p><ul class="tags">{''.join(f'<li>{e(x)}</li>' for x in c['classes'])}</ul></div></article>"""
    gal = "".join(f'<li class="gi pop" style="--r:{["-2deg","1deg","2deg","-1deg"][n % 4]}"><figure class="frame">{img(g["image"], "(min-width: 900px) 25vw, 50vw")}</figure></li>' for n, g in enumerate(C["gallery"][:4]))
    body = f"""<section class="hero"><div class="wrap hero__grid">
<div class="hero__txt">{shape('tri','hero__s1')}{shape('zig','hero__s3')}
<p class="kicker">{e(O['name'])} · sedan {e(O['founded'])}</p>
<h1>Skate, snow <span>och freeski</span> i Uppsala</h1>
<p class="lead">{e(i['lead'])}</p>
<p class="actions">{btn(u('bli-medlem'), 'Bli medlem')}{btn(u('skateskola'), 'Skateskolan', ghost=True)}</p></div>
<div class="hero__pic">{shape('circ','hero__s2')}{shape('dot','hero__s4')}<figure class="frame frame--big pop" style="--r:-2deg">{img('snowboard-hopp', '(min-width: 900px) 52vw, 100vw', lazy=False)}</figure>
<figure class="frame hero__small pop" style="--r:4deg">{img('skate-luft-inne', '(min-width: 900px) 22vw, 50vw', lazy=False)}</figure></div>
</div></section>
<section class="facts"><div class="wrap"><h2 class="vh">Snabbfakta</h2><ul class="facts__list">{facts}</ul></div></section>
<section class="sec"><div class="wrap"><div class="sec__head"><p class="kicker">Tre sporter</p><h2>Välj din bräda</h2></div><ul class="scards">{sports}</ul></div></section>
{ZIG}
<section class="sec"><div class="wrap split"><div class="sec__head">{shape('sq','sec__s')}<p class="kicker">Platser</p><h2>Här åker vi</h2><p>Sommar på rampen, vinter i backen och inomhus när det är kallt.</p><p>{btn(u('platser'), 'Alla platser', ghost=True)}</p></div><ol class="pls">{places}</ol></div></section>
<section class="sec sec--tint"><div class="wrap"><div class="sec__head"><p class="kicker">Tävlingar</p><h2>Öppet för alla nivåer</h2><p>{e(C['competitions']['lead'])}</p></div><div class="comps">{comps}</div></div></section>
<section class="sec"><div class="wrap split split--rev"><div class="sec__head"><p class="kicker">Tjejsatsning</p><h2>Fler tjejer i parken</h2><p>{e(C['girls']['lead'])}</p><p>{btn(u('tjejer'), 'Läs om satsningen', ghost=True)}</p></div>
<figure class="frame pop" style="--r:2deg">{img(C['girls']['image'], '(min-width: 900px) 50vw, 100vw')}</figure></div></section>
{join_band()}
<section class="sec"><div class="wrap"><div class="sec__head sec__head--row"><div><p class="kicker">Galleri</p><h2>Från backen och rampen</h2></div><p>{btn(u('galleri'), 'Hela galleriet', ghost=True)}</p></div><ul class="gal gal--4">{gal}</ul></div></section>"""
    write("", "Start", "Uppsala Crew IF är Uppsalas förening för skateboard, snowboard och freeski. Skateskola, tävlingar och parkåkning på Allis, KAP-rampen och i Sunnerstabacken.", body)


def sport_page(s):
    secs = ""
    for n, sec in enumerate(s["sections"]):
        secs += f'<section class="txtblock pop" style="--r:{["-0.6deg","0.6deg"][n % 2]}"><span class="txtblock__n" aria-hidden="true">0{n+1}</span><h2>{e(sec["h"])}</h2>{P(sec["p"])}</section>'
    sched = ""
    if s.get("schedule"):
        sched = '<dl class="sched card">' + "".join(f'<div><dt>{e(r["k"])}</dt><dd>{e(r["v"])}</dd></div>' for r in s["schedule"]) + "</dl>"
    gal = "".join(f'<li class="gi pop" style="--r:{["-2deg","1.5deg","-1deg","2deg","-1.5deg"][n % 5]}"><figure class="frame">{img(x, "(min-width: 900px) 30vw, 50vw")}</figure></li>' for n, x in enumerate(s["images"]))
    info = f'<dl class="info card"><div><dt>Var</dt><dd>{e(s["where"])}</dd></div><div><dt>När</dt><dd>{e(s["when"])}</dd></div></dl>'
    body = pagehead(s["slug"], "Sport", s["title"], s["short"], s["hero"]) + f"""
<section class="sec"><div class="wrap article"><aside class="article__side">{info}{sched}<p>{btn(u('bli-medlem'), 'Bli medlem')}</p></aside><div class="article__main">{secs}</div></div></section>
{ZIG}<section class="sec"><div class="wrap"><h2 class="sec__h">Bilder</h2><ul class="gal">{gal}</ul></div></section>{join_band()}"""
    ld = [{"@context": "https://schema.org", "@type": "Service", "name": f"{s['title']} med {O['name']}", "serviceType": s["title"],
           "description": s["meta_description"], "provider": {"@id": SITE + "/#org"}, "areaServed": {"@type": "City", "name": "Uppsala"}, "url": f"{SITE}/{s['slug']}/"}]
    write(s["slug"], s["title"], s["meta_description"], body, ld, s["hero"])


def places_page():
    cards = ""
    for n, p in enumerate(C["places"]):
        pic = img(p["image"], "(min-width: 900px) 40vw, 100vw") if p["image"] else f'<span class="noimg" aria-hidden="true">{SHAPES["tri"]}{SHAPES["circ"]}</span>'
        cards += f"""<article class="comp pop" style="--r:{['-1deg','1deg','-0.5deg'][n]}"><div class="comp__img frame">{pic}</div><div class="comp__b"><p class="kicker">{e(p['address'])}</p><h2 class="h3">{e(p['title'])}</h2><p>{e(p['short'])}</p><p>{btn(u('platser/' + p['slug']), 'Om ' + p['title'], ghost=True)}</p></div></article>"""
    body = pagehead("platser", "Platser", "Här åker vi", "Uppsala Crew finns på Allis Uppsala, Kapellgärdet, KAP-rampen och i Sunnerstabacken.") + f'<section class="sec"><div class="wrap comps comps--stack">{cards}</div></section>{join_band()}'
    write("platser", "Platser", "Här åker Uppsala Crew IF: Sunnerstabacken, Allis Uppsala och KAP-rampen vid Kapellgärdet.", body)


def place_page(p):
    slug = "platser/" + p["slug"]
    others = "".join(f'<li><a href="{u("platser/" + o["slug"])}">{e(o["title"])}</a></li>' for o in C["places"] if o is not p)
    body = pagehead(slug, p["address"], p["title"], p["short"], p["image"], ("dot", "tri")) + f"""
<section class="sec"><div class="wrap article"><aside class="article__side"><dl class="info card"><div><dt>Adress</dt><dd>{e(p['address'])}</dd></div><div><dt>Uppdateringar</dt><dd><a href="{O['instagram']}" rel="noopener">{e(O['instagram_handle'])}</a></dd></div></dl>
<div class="card"><p class="ft__h">Andra platser</p><ul class="linklist">{others}</ul></div></aside>
<div class="article__main"><section class="txtblock pop" style="--r:-0.5deg"><h2>Om platsen</h2>{P(p['body'])}</section></div></div></section>{join_band()}"""
    ld = [{"@context": "https://schema.org", "@type": "SportsActivityLocation", "name": p["title"], "description": p["short"],
           "address": {"@type": "PostalAddress", "streetAddress": p["address"], "addressLocality": "Uppsala", "addressCountry": "SE"},
           "url": f"{SITE}/{slug}/", "parentOrganization": {"@id": SITE + "/#org"}}]
    desc = f"{p['title']}, {p['address']}. {p['short']}"[:158]
    write(slug, p["title"], desc, body, ld, p["image"] or "skate-luft-inne")


def about_page():
    a = C["about"]
    tl = "".join(f'<li class="tl__i pop" style="--r:{["-1deg","1deg"][n%2]}"><span class="tl__y">{e(t["year"])}</span><p>{e(t["text"])}</p></li>' for n, t in enumerate(a["timeline"]))
    body = pagehead("om-foreningen", "Föreningen", "Om Uppsala Crew", a["lead"], "graffiti") + f"""
<section class="sec"><div class="wrap"><h2 class="sec__h">Tidslinje</h2><ol class="tl">{tl}</ol></div></section>{ZIG}
<section class="sec"><div class="wrap split"><section class="txtblock pop" style="--r:-1deg"><h2>Vision</h2><p>{e(a['vision'])}</p></section><section class="txtblock pop" style="--r:1deg"><h2>Organisation</h2><p>{e(a['org_text'])}</p><p>Org.nr {e(O['orgnr'])}</p></section></div></section>{join_band()}"""
    write("om-foreningen", "Om föreningen", a["meta_description"], body, og_img="graffiti")


def girls_page():
    g = C["girls"]
    secs = "".join(f'<section class="txtblock pop" style="--r:{["-0.8deg","0.8deg"][n%2]}"><h2>{e(s["h"])}</h2>{P(s["p"])}</section>' for n, s in enumerate(g["sections"]))
    body = pagehead("tjejer", "Föreningen", g["title"], g["lead"], g["image"]) + f'<section class="sec"><div class="wrap split">{secs}</div></section><section class="sec"><div class="wrap center">{btn(u("kontakt"), "Hör av dig")}</div></section>{join_band()}'
    write("tjejer", g["title"], g["meta_description"], body, og_img=g["image"])


def comps_page():
    c = C["competitions"]
    items = ""
    for n, x in enumerate(c["items"]):
        items += f"""<article class="comp pop" style="--r:{['-1deg','1deg'][n]}"><div class="comp__img frame">{img(x['image'], '(min-width: 900px) 40vw, 100vw')}</div>
<div class="comp__b"><p class="kicker">{e(x['sport'])} · {e(x['place'])}</p><h2 class="h3">{e(x['title'])}</h2><p>{e(x['text'])}</p><h3 class="mini">Klasser</h3><ul class="tags">{''.join(f'<li>{e(k)}</li>' for k in x['classes'])}</ul></div></article>"""
    body = pagehead("tavlingar", "Tävlingar", "Tävlingar", c["lead"]) + f'<section class="sec"><div class="wrap comps comps--stack">{items}</div></section><section class="sec"><div class="wrap center"><p>Kommande datum publiceras på Instagram.</p><p>{btn(O["instagram"], "Följ " + O["instagram_handle"])}</p></div></section>'
    write("tavlingar", "Tävlingar", c["meta_description"], body, og_img="skate-luft-inne")


def gallery_page():
    gal = "".join(f'<li class="gi pop" style="--r:{["-2deg","1deg","2deg","-1deg","1.5deg"][n % 5]}"><figure class="frame">{img(g["image"], "(min-width: 900px) 30vw, 50vw")}<figcaption>{e(g["caption"])}</figcaption></figure></li>' for n, g in enumerate(C["gallery"]))
    body = pagehead("galleri", "Galleri", "Galleri", "Bilder från backen, rampen och hallen.") + f'<section class="sec"><div class="wrap"><ul class="gal gal--full">{gal}</ul></div></section>'
    write("galleri", "Galleri", "Bilder från Uppsala Crew IF: snowboard och freeski i Sunnerstabacken, skateboard på Allis och KAP-rampen.", body)


def engage_page():
    g = C["engage"]
    roles = "".join(f'<li class="role pop" style="--r:{["-1.5deg","1deg","-1deg","1.5deg"][n]}"><span class="role__n" aria-hidden="true">{n+1}</span><h2 class="h3">{e(r["title"])}</h2><p>{e(r["text"])}</p></li>' for n, r in enumerate(g["roles"]))
    body = pagehead("engagera-dig", "Föreningen", "Engagera dig", g["lead"], "instruktorer") + f'<section class="sec"><div class="wrap"><ul class="roles">{roles}</ul></div></section><section class="sec"><div class="wrap center">{btn(u("kontakt"), "Kontakta oss")}</div></section>'
    write("engagera-dig", "Engagera dig", g["meta_description"], body, og_img="instruktorer")


def partners_page():
    p = C["partners"]
    fed = "".join(f'<li><a href="{x["url"]}" rel="noopener">{e(x["name"])}</a></li>' for x in p["federations"])
    sp = "".join(f'<li class="sticker pop" style="--r:{["-3deg","2deg","-1deg","3deg","-2deg","1deg"][n%6]}">{e(x)}</li>' for n, x in enumerate(p["sponsors"]))
    body = pagehead("partners", "Föreningen", "Partners och förbund", p["lead"]) + f"""
<section class="sec"><div class="wrap split"><div class="card"><h2>Förbund och samarbeten</h2><ul class="linklist">{fed}</ul></div>
<div><h2>Sponsorer</h2><p>{e(p['sponsors_note'])}</p><ul class="stickers">{sp}</ul></div></div></section>"""
    write("partners", "Partners och förbund", p["meta_description"], body)


def join_page():
    m = C["membership"]
    ben = "".join(f"<li>{e(b)}</li>" for b in m["benefits"])
    steps = "".join(f'<li class="pop" style="--r:{["-1deg","1deg","-1deg"][n]}"><span aria-hidden="true">{n+1}</span>{e(s)}</li>' for n, s in enumerate(m["steps"]))
    body = pagehead("bli-medlem", "Medlemskap", "Bli medlem", f"{m['price']}. {m['price_note']}") + f"""
<section class="sec"><div class="wrap split"><div><h2>Det ingår</h2><ul class="checks">{ben}</ul><h2>Så går det till</h2><ol class="steps">{steps}</ol></div>
<div><h2 id="ansokan">Medlemsansökan</h2>{form('join')}</div></div></section>"""
    write("bli-medlem", "Bli medlem", m["meta_description"], body)


def faq_page():
    q = "".join(f'<details class="faq pop" style="--r:{["-0.5deg","0.5deg"][n%2]}"><summary><h2 class="faq__q">{e(f["q"])}</h2></summary><p>{e(f["a"])}</p></details>' for n, f in enumerate(C["faq"]))
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in C["faq"]]}]
    body = pagehead("vanliga-fragor", "Hjälp", "Vanliga frågor", "Svar om medlemskap, försäkring, utrustning och träning.") + f'<section class="sec"><div class="wrap narrow">{q}</div></section>'
    write("vanliga-fragor", "Vanliga frågor", "Vanliga frågor om Uppsala Crew IF: medlemsavgift, försäkring, utrustning, skateskola och var vi tränar.", body, ld)


def contact_page():
    body = pagehead("kontakt", "Kontakt", "Kontakt", "Frågor om träning, medlemskap eller samarbete. Mejla, ring eller skriv i formuläret.") + f"""
<section class="sec"><div class="wrap split"><div><dl class="info card info--big">
<div><dt>E-post</dt><dd><a href="mailto:{O['email']}">{O['email']}</a><br><a href="mailto:{O['email_alt']}">{O['email_alt']}</a></dd></div>
<div><dt>Telefon</dt><dd><a href="tel:{O['phone_href']}">{O['phone']}</a></dd></div>
<div><dt>Postadress</dt><dd>{e(O['legal'])}<br>{e(O['street'])}<br>{e(O['zip'])} {e(O['city'])}</dd></div>
<div><dt>Org.nr</dt><dd>{e(O['orgnr'])}</dd></div>
<div><dt>Sociala medier</dt><dd><a href="{O['instagram']}" rel="noopener">Instagram {e(O['instagram_handle'])}</a><br><a href="{O['facebook']}" rel="noopener">Facebook</a></dd></div></dl></div>
<div><h2>Skriv till oss</h2>{form('contact')}</div></div></section>"""
    write("kontakt", "Kontakt", f"Kontakta Uppsala Crew IF: {O['email']}, {O['phone']}. {O['street']}, {O['zip']} {O['city']}.", body)


def privacy_page():
    s = "".join(f'<section class="txtblock"><h2>{e(x["h"])}</h2><p>{e(x["p"])}</p></section>' for x in C["privacy"])
    body = pagehead("integritetspolicy", "Föreningen", "Integritetspolicy", "Så hanterar Uppsala Crew IF dina personuppgifter.") + f'<section class="sec"><div class="wrap narrow">{s}</div></section>'
    write("integritetspolicy", "Integritetspolicy", "Integritetspolicy för Uppsala Crew IF: vilka personuppgifter föreningen sparar, varför och hur länge.", body)


def notfound():
    body = f"""<section class="ph"><div class="wrap center">{shape('tri','ph__s1')}{shape('circ','ph__s2')}<p class="kicker">Fel 404</p><h1>Sidan finns inte</h1><p class="lead">Länken kan vara gammal eller felstavad.</p><p class="actions">{btn(u(''), 'Till startsidan')}{btn(u('kontakt'), 'Kontakt', ghost=True)}</p></div></section>"""
    write("404", "Sidan finns inte", "Sidan kunde inte hittas.", body)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    here = Path(__file__).parent
    for f in ("site.css", "site.js"):
        shutil.copy(here / f, OUT / "assets" / f)
    home()
    for s in C["sports"]:
        sport_page(s)
    places_page()
    for p in C["places"]:
        place_page(p)
    about_page(); girls_page(); comps_page(); gallery_page(); engage_page(); partners_page()
    join_page(); faq_page(); contact_page(); privacy_page(); notfound()
    n = len(list(OUT.rglob("*.html")))
    print(f"{V}: {n} html-filer i {OUT}")


if __name__ == "__main__":
    main()
