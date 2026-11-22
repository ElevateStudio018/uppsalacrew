#!/usr/bin/env python3
"""v08 Magasin – Uppsala Crew IF. Kör: python3 themes/v07/build.py"""
import json, html, shutil
from pathlib import Path

V = "v08"
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
FONTS = "https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600&family=Instrument+Serif:ital@0;1&display=swap"


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



# ---------- magasin: navigation ----------
GROUPS = [
    ("Sporterna", ["skateboard", "snowboard-och-freeski", "skateskola"]),
    ("Platserna", ["platser", "platser/sunnerstabacken", "platser/allis-uppsala", "platser/kap-rampen"]),
    ("Föreningen", ["om-foreningen", "tjejer", "tavlingar", "galleri", "engagera-dig", "partners"]),
    ("Service", ["bli-medlem", "vanliga-fragor", "kontakt", "integritetspolicy"]),
]
TOP = [("skateboard", "Skateboard"), ("snowboard-och-freeski", "Snö"), ("platser", "Platser"), ("tavlingar", "Tävlingar"), ("om-foreningen", "Föreningen"), ("kontakt", "Kontakt")]


def cur(s, slug):
    return ' aria-current="page"' if s == slug else ""


def header(slug):
    top = "".join(f'<li><a href="{u(s)}"{cur(s, slug)}>{t}</a></li>' for s, t in TOP)
    groups = ""
    n = 0
    for g, items in GROUPS:
        li = ""
        for s in items:
            n += 1
            li += f'<li><a href="{u(s)}"{cur(s, slug)}><span class="toc__n">{n:02d}</span>{e(PAGES[s]["title"])}</a></li>'
        groups += f'<div class="menu__g"><p class="menu__h">{g}</p><ul>{li}</ul></div>'
    return f"""<a class="skip" href="#main">Hoppa till innehållet</a>
<header class="hd"><div class="wrap hd__in">
<a class="brand" href="{u('')}"><img src="{MEDIA}/logo-ljus-192.png" width="192" height="192" alt=""><span>Uppsala Crew</span></a>
<nav aria-label="Huvudmeny" class="hd__nav"><ul>{top}</ul></nav>
<a class="hd__cta" href="{u('bli-medlem')}">Bli medlem</a>
<button class="menubtn" type="button" aria-expanded="false" aria-controls="menu">Innehåll</button>
</div>
<div class="menu" id="menu" hidden><div class="wrap"><p class="menu__title">Innehåll</p><div class="menu__grid">{groups}</div></div></div>
</header>"""


def footer():
    return f"""<footer class="ft"><div class="wrap">
<p class="ft__mast">Uppsala Crew</p>
<div class="ft__grid">
<div><p class="ft__h">Utgivare</p><p>{e(O['legal'])}<br>Org.nr {e(O['orgnr'])}<br>{e(O['street'])}<br>{e(O['zip'])} {e(O['city'])}</p></div>
<div><p class="ft__h">Redaktionen</p><ul><li><a href="mailto:{O['email']}">{O['email']}</a></li><li><a href="tel:{O['phone_href']}">{O['phone']}</a></li></ul></div>
<div><p class="ft__h">Följ</p><ul><li><a href="{O['instagram']}" rel="noopener">Instagram {e(O['instagram_handle'])}</a></li><li><a href="{O['facebook']}" rel="noopener">Facebook</a></li></ul></div>
<div><p class="ft__h">Mer</p><ul><li><a href="{u('bli-medlem')}">Bli medlem</a></li><li><a href="{u('vanliga-fragor')}">Vanliga frågor</a></li><li><a href="{u('partners')}">Partners och förbund</a></li><li><a href="{u('integritetspolicy')}">Integritetspolicy</a></li></ul></div>
</div>
<p class="ft__base"><img src="{MEDIA}/logo-ljus-192.png" width="40" height="40" alt="Uppsala Crew IF logotyp" loading="lazy">{e(O['tagline'])}. Förhandsvisning, tema v08 Magasin.</p>
</div></footer>"""


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
<meta name="theme-color" content="#FBFAF7">
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



def pagehead(slug, kicker, h1, lead, image=None):
    pic = f'<figure class="bleed rv">{img(image, "100vw", lazy=False)}</figure>' if image else ""
    return f"""<header class="ph"><div class="wrap">{crumbs_html(slug)}
<p class="rubric">{e(kicker)}</p><h1 class="split-words">{e(h1)}</h1><p class="dek">{e(lead)}</p></div></header>{pic}"""


def btn(href, text, ghost=False):
    return f'<a class="btn{" btn--ghost" if ghost else ""}" href="{href}">{e(text)}</a>'


def body_cols(paras, drop=True):
    """Tvåspaltig brödtext, första stycket med anfang."""
    out = ""
    for i, p in enumerate(paras):
        out += f'<p{" class=\"dropcap\"" if drop and i == 0 else ""}>{e(p)}</p>'
    return f'<div class="cols">{out}</div>'


def quote(text, src=""):
    s = f"<figcaption>{e(src)}</figcaption>" if src else ""
    return f'<figure class="pull"><blockquote><p>{e(text)}</p></blockquote>{s}</figure>'


def first_sentence(t):
    i = t.find(". ")
    return t if i < 0 else t[: i + 1]


def suite(images, caption=""):
    """Bildsvit: en vid, två i bredd, en detalj."""
    ims = list(images)
    if not ims:
        return ""
    h = f'<figure class="su__wide rv">{img(ims[0], "(min-width: 1000px) 1200px, 100vw")}</figure>'
    if len(ims) >= 3:
        h += f'<div class="su__pair"><figure class="rv">{img(ims[1], "(min-width: 1000px) 600px, 100vw")}</figure><figure class="rv">{img(ims[2], "(min-width: 1000px) 600px, 100vw")}</figure></div>'
    elif len(ims) == 2:
        h += f'<div class="su__pair su__pair--one"><figure class="rv">{img(ims[1], "(min-width: 1000px) 800px, 100vw")}</figure></div>'
    if len(ims) >= 4:
        h += f'<figure class="su__detail rv">{img(ims[3], "(min-width: 1000px) 420px, 70vw")}</figure>'
    cap = f'<p class="su__cap">{e(caption)}</p>' if caption else ""
    return f'<section class="suite"><div class="wrap"><h2 class="vh">Bilder</h2>{h}{cap}</div></section>'


def join_band():
    m = C["membership"]
    return f"""<section class="sub"><div class="wrap sub__in"><p class="rubric">Prenumerera på föreningen</p>
<h2 class="sub__h">Medlem för {e(m['price'])}</h2><p class="dek">{e(m['price_note'])}</p><p>{btn(u('bli-medlem'), 'Bli medlem')}</p></div></section>"""


# ---------- sidor ----------
def home():
    i = C["intro"]
    toc = [
        ("Sporterna", [(s["slug"], s["title"], s["short"]) for s in C["sports"]]),
        ("Platserna", [("platser/" + p["slug"], p["title"], p["short"]) for p in C["places"]]),
        ("Föreningen", [("tavlingar", "Tävlingar", "Miniramp Madness och Uppsala Rail Jam."), ("tjejer", "Tjejsatsning", "Fler tjejer i parken och på rampen."),
                        ("om-foreningen", "Om föreningen", "Historik, vision och organisation."), ("bli-medlem", "Bli medlem", C["membership"]["price"] + ".")]),
    ]
    n = 0
    tochtml = ""
    for g, items in toc:
        li = ""
        for s, t, d in items:
            n += 1
            li += f'<li><a href="{u(s)}"><span class="toc__n">{n:02d}</span><span class="toc__t">{e(t)}</span><span class="toc__d">{e(d)}</span></a></li>'
        tochtml += f'<div class="toc__g"><h3 class="toc__h">{g}</h3><ol>{li}</ol></div>'
    a = C["about"]
    sports = ""
    for k, s in enumerate(C["sports"]):
        sports += f"""<article class="feat{' feat--flip' if k % 2 else ''}"><figure class="feat__img rv">{img(s['hero'], '(min-width: 1000px) 55vw, 100vw')}</figure>
<div class="feat__txt"><p class="rubric">Sport {k+1:02d} · {e(s['when'])}</p><h3 class="feat__h"><a href="{u(s['slug'])}">{e(s['title'])}</a></h3><p class="dek">{e(s['short'])}</p><p class="byline">{e(s['where'])}</p></div></article>"""
    places = "".join(f'<li><a href="{u("platser/" + p["slug"])}"><span class="pl__t">{e(p["title"])}</span><span class="pl__a">{e(p["address"])}</span><span class="pl__d">{e(p["short"])}</span></a></li>' for p in C["places"])
    body = f"""<section class="cover"><div class="cover__img">{img('snowboard-hopp', '100vw', lazy=False)}</div>
<div class="wrap cover__in"><p class="cover__issue"><span>Nr 07</span><span>{e(O['tagline'])}</span><span>Sedan {e(O['founded'])}</span></p>
<h1 class="cover__h split-words">Skate, snö och freeski i Uppsala</h1>
<p class="cover__dek">{e(i['lead'])}</p></div></section>
<section class="issue"><div class="wrap issue__grid"><div><p class="rubric">Innehåll</p><h2 class="big">I det här numret</h2></div><div class="toc">{tochtml}</div></div></section>
<section class="essay"><div class="wrap"><p class="rubric">Ledare</p><h2 class="big split-words">En förening för alla brädor</h2>{body_cols([i['lead'], a['lead'], a['org_text']])}
{quote(a['vision'], 'Föreningens vision')}</div></section>
<figure class="bleed rv">{img('freeski-hopp', '100vw')}</figure>
<section class="sec"><div class="wrap"><p class="rubric">Sporterna</p><h2 class="big split-words">Tre sätt att åka</h2>{sports}</div></section>
<section class="sec sec--rule"><div class="wrap two"><div><p class="rubric">Platserna</p><h2 class="big split-words">Kartan</h2><p class="dek">Rampen på sommaren, hallen när det är kallt och backen på vintern.</p></div><ol class="pls">{places}</ol></div></section>
{suite(['allis-hall-1', 'kvallshopp', 'snowboard-box', 'allis-bowl'], 'Allis Uppsala, kvällsåkning och funparken i Sunnersta.')}
<section class="sec"><div class="wrap"><p class="rubric">Tjejsatsning</p><h2 class="big split-words">Fler tjejer i parken</h2>{body_cols([C['girls']['lead']] + C['girls']['sections'][0]['p'])}<p class="more"><a href="{u('tjejer')}">Läs hela reportaget om tjejsatsningen</a></p></div></section>
{join_band()}"""
    write("", "Start", "Uppsala Crew IF är Uppsalas förening för skateboard, snowboard och freeski. Skateskola, tävlingar och parkåkning på Allis, KAP-rampen och i Sunnerstabacken.", body)


def sport_page(s):
    secs = s["sections"]
    out = ""
    for n, sec in enumerate(secs):
        out += f'<section class="art__sec"><h2 class="h2">{e(sec["h"])}</h2>{body_cols(sec["p"], drop=(n == 0))}</section>'
        if n == 0:
            out += quote(first_sentence(secs[-1]["p"][0]))
    facts = f'<dl class="facts"><div><dt>Var</dt><dd>{e(s["where"])}</dd></div><div><dt>När</dt><dd>{e(s["when"])}</dd></div>'
    for r in s.get("schedule", []):
        facts += f'<div><dt>{e(r["k"])}</dt><dd>{e(r["v"])}</dd></div>'
    facts += "</dl>"
    body = pagehead(s["slug"], "Sporterna", s["title"], s["short"], s["hero"]) + f"""
<article class="sec"><div class="wrap">{facts}{out}</div></article>{suite(s['images'])}{join_band()}"""
    ld = [{"@context": "https://schema.org", "@type": "Service", "name": f"{s['title']} med {O['name']}", "serviceType": s["title"],
           "description": s["meta_description"], "provider": {"@id": SITE + "/#org"}, "areaServed": {"@type": "City", "name": "Uppsala"}, "url": f"{SITE}/{s['slug']}/"}]
    write(s["slug"], s["title"], s["meta_description"], body, ld, s["hero"])


def places_page():
    items = ""
    for n, p in enumerate(C["places"]):
        pic = f'<figure class="feat__img rv">{img(p["image"], "(min-width: 1000px) 55vw, 100vw")}</figure>' if p["image"] else f'<div class="feat__img feat__img--type" aria-hidden="true"><span>{e(p["title"])}</span></div>'
        items += f"""<article class="feat{' feat--flip' if n % 2 else ''}">{pic}<div class="feat__txt"><p class="rubric">{e(p['address'])}</p><h2 class="feat__h"><a href="{u('platser/' + p['slug'])}">{e(p['title'])}</a></h2><p class="dek">{e(p['short'])}</p></div></article>"""
    body = pagehead("platser", "Platserna", "Här åker vi", "Uppsala Crew finns på Allis Uppsala, Kapellgärdet, KAP-rampen och i Sunnerstabacken.") + f'<section class="sec"><div class="wrap">{items}</div></section>{join_band()}'
    write("platser", "Platser", "Här åker Uppsala Crew IF: Sunnerstabacken, Allis Uppsala och KAP-rampen vid Kapellgärdet.", body)


def place_page(p):
    slug = "platser/" + p["slug"]
    others = "".join(f'<li><a href="{u("platser/" + o["slug"])}">{e(o["title"])}</a></li>' for o in C["places"] if o is not p)
    q = quote(p["body"][1]) if len(p["body"]) > 2 else ""
    body = pagehead(slug, "Platserna", p["title"], p["short"], p["image"]) + f"""
<article class="sec"><div class="wrap"><dl class="facts"><div><dt>Adress</dt><dd>{e(p['address'])}</dd></div><div><dt>Uppdateringar</dt><dd><a href="{O['instagram']}" rel="noopener">{e(O['instagram_handle'])}</a></dd></div></dl>
{body_cols(p['body'][:2])}{q}{body_cols(p['body'][2:], drop=False) if len(p['body']) > 2 else ''}
<nav class="also" aria-label="Andra platser"><p class="rubric">Fler platser</p><ul>{others}</ul></nav></div></article>{join_band()}"""
    ld = [{"@context": "https://schema.org", "@type": "SportsActivityLocation", "name": p["title"], "description": p["short"],
           "address": {"@type": "PostalAddress", "streetAddress": p["address"], "addressLocality": "Uppsala", "addressCountry": "SE"},
           "url": f"{SITE}/{slug}/", "parentOrganization": {"@id": SITE + "/#org"}}]
    write(slug, p["title"], f"{p['title']}, {p['address']}. {p['short']}"[:158], body, ld, p["image"] or "skate-luft-inne")


def about_page():
    a = C["about"]
    tl = "".join(f'<li><span class="tl__y">{e(t["year"])}</span><p>{e(t["text"])}</p></li>' for t in a["timeline"])
    body = pagehead("om-foreningen", "Föreningen", "Om Uppsala Crew", a["lead"], "graffiti") + f"""
<section class="sec"><div class="wrap"><h2 class="h2">Organisation</h2>{body_cols([a['org_text'], f"Org.nr {O['orgnr']}. Postadress {O['street']}, {O['zip']} {O['city']}."])}{quote(a['vision'], 'Föreningens vision')}
<h2 class="h2">Tidslinje</h2><ol class="tl">{tl}</ol></div></section>{join_band()}"""
    write("om-foreningen", "Om föreningen", a["meta_description"], body, og_img="graffiti")


def girls_page():
    g = C["girls"]
    out = "".join(f'<section class="art__sec"><h2 class="h2">{e(s["h"])}</h2>{body_cols(s["p"], drop=(n == 0))}</section>' for n, s in enumerate(g["sections"]))
    body = pagehead("tjejer", "Föreningen", g["title"], g["lead"], g["image"]) + f'<article class="sec"><div class="wrap">{out}{quote(g["sections"][0]["p"][0])}<p class="more"><a href="{u("kontakt")}">Hör av dig till föreningen</a></p></div></article>{join_band()}'
    write("tjejer", g["title"], g["meta_description"], body, og_img=g["image"])


def comps_page():
    c = C["competitions"]
    items = ""
    for n, x in enumerate(c["items"]):
        items += f"""<article class="feat{' feat--flip' if n % 2 else ''}"><figure class="feat__img rv">{img(x['image'], '(min-width: 1000px) 55vw, 100vw')}</figure>
<div class="feat__txt"><p class="rubric">{e(x['sport'])} · {e(x['place'])}</p><h2 class="feat__h">{e(x['title'])}</h2><p>{e(x['text'])}</p><p class="byline">Klasser: {e(', '.join(x['classes']))}</p></div></article>"""
    body = pagehead("tavlingar", "Föreningen", "Tävlingar", c["lead"]) + f'<section class="sec"><div class="wrap">{items}{quote(c["items"][1]["text"].split(". ")[1].rstrip(".") + ".")}<p class="more"><a href="{O["instagram"]}" rel="noopener">Kommande datum publiceras på Instagram {e(O["instagram_handle"])}</a></p></div></section>'
    write("tavlingar", "Tävlingar", c["meta_description"], body, og_img="skate-luft-inne")


def gallery_page():
    gal = "".join(f'<figure class="gal__i rv">{img(g["image"], "(min-width: 1000px) 33vw, 100vw")}<figcaption><span>{n+1:02d}</span> {e(g["caption"])}</figcaption></figure>' for n, g in enumerate(C["gallery"]))
    body = pagehead("galleri", "Bildreportage", "Galleri", "Bilder från backen, rampen och hallen.") + f'<section class="sec"><div class="wrap gal">{gal}</div></section>'
    write("galleri", "Galleri", "Bilder från Uppsala Crew IF: snowboard och freeski i Sunnerstabacken, skateboard på Allis och KAP-rampen.", body)


def engage_page():
    g = C["engage"]
    roles = "".join(f'<li><span class="toc__n">{n+1:02d}</span><h2 class="h3">{e(r["title"])}</h2><p>{e(r["text"])}</p></li>' for n, r in enumerate(g["roles"]))
    body = pagehead("engagera-dig", "Föreningen", "Engagera dig", g["lead"], "instruktorer") + f'<section class="sec"><div class="wrap"><ol class="roles">{roles}</ol><p class="more"><a href="{u("kontakt")}">Kontakta oss</a></p></div></section>'
    write("engagera-dig", "Engagera dig", g["meta_description"], body, og_img="instruktorer")


def partners_page():
    p = C["partners"]
    fed = "".join(f'<li><a href="{x["url"]}" rel="noopener">{e(x["name"])}</a></li>' for x in p["federations"])
    sp = "".join(f"<li>{e(x)}</li>" for x in p["sponsors"])
    body = pagehead("partners", "Föreningen", "Partners och förbund", p["lead"]) + f"""
<section class="sec"><div class="wrap two"><div><h2 class="h2">Förbund och samarbeten</h2><ul class="list">{fed}</ul></div><div><h2 class="h2">Sponsorer</h2><p class="byline">{e(p['sponsors_note'])}</p><ul class="sponsors">{sp}</ul></div></div></section>"""
    write("partners", "Partners och förbund", p["meta_description"], body)


def join_page():
    m = C["membership"]
    ben = "".join(f"<li>{e(b)}</li>" for b in m["benefits"])
    steps = "".join(f"<li>{e(s)}</li>" for s in m["steps"])
    body = pagehead("bli-medlem", "Medlemskap", "Bli medlem", f"{m['price']}. {m['price_note']}") + f"""
<section class="sec"><div class="wrap two"><div><h2 class="h2">Det ingår</h2><ul class="list list--plain">{ben}</ul><h2 class="h2">Så går det till</h2><ol class="steps">{steps}</ol></div>
<div><h2 class="h2">Medlemsansökan</h2>{form('join')}</div></div></section>"""
    write("bli-medlem", "Bli medlem", m["meta_description"], body)


def faq_page():
    q = "".join(f'<details class="faq"><summary><h2 class="faq__q"><span class="toc__n">{n+1:02d}</span>{e(f["q"])}</h2></summary><p>{e(f["a"])}</p></details>' for n, f in enumerate(C["faq"]))
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in C["faq"]]}]
    body = pagehead("vanliga-fragor", "Service", "Vanliga frågor", "Svar om medlemskap, försäkring, utrustning och träning.") + f'<section class="sec"><div class="wrap narrow">{q}</div></section>'
    write("vanliga-fragor", "Vanliga frågor", "Vanliga frågor om Uppsala Crew IF: medlemsavgift, försäkring, utrustning, skateskola och var vi tränar.", body, ld)


def contact_page():
    body = pagehead("kontakt", "Service", "Kontakt", "Frågor om träning, medlemskap eller samarbete. Mejla, ring eller skriv i formuläret.") + f"""
<section class="sec"><div class="wrap two"><dl class="facts facts--stack">
<div><dt>E-post</dt><dd><a href="mailto:{O['email']}">{O['email']}</a><br><a href="mailto:{O['email_alt']}">{O['email_alt']}</a></dd></div>
<div><dt>Telefon</dt><dd><a href="tel:{O['phone_href']}">{O['phone']}</a></dd></div>
<div><dt>Postadress</dt><dd>{e(O['legal'])}<br>{e(O['street'])}<br>{e(O['zip'])} {e(O['city'])}</dd></div>
<div><dt>Org.nr</dt><dd>{e(O['orgnr'])}</dd></div>
<div><dt>Sociala medier</dt><dd><a href="{O['instagram']}" rel="noopener">Instagram {e(O['instagram_handle'])}</a><br><a href="{O['facebook']}" rel="noopener">Facebook</a></dd></div></dl>
<div><h2 class="h2">Skriv till oss</h2>{form('contact')}</div></div></section>"""
    write("kontakt", "Kontakt", f"Kontakta Uppsala Crew IF: {O['email']}, {O['phone']}. {O['street']}, {O['zip']} {O['city']}.", body)


def privacy_page():
    s = "".join(f'<section class="art__sec"><h2 class="h2">{e(x["h"])}</h2><p>{e(x["p"])}</p></section>' for x in C["privacy"])
    body = pagehead("integritetspolicy", "Service", "Integritetspolicy", "Så hanterar Uppsala Crew IF dina personuppgifter.") + f'<section class="sec"><div class="wrap narrow">{s}</div></section>'
    write("integritetspolicy", "Integritetspolicy", "Integritetspolicy för Uppsala Crew IF: vilka personuppgifter föreningen sparar, varför och hur länge.", body)


def notfound():
    body = f"""<header class="ph"><div class="wrap"><p class="rubric">Fel 404</p><h1>Sidan finns inte</h1><p class="dek">Länken kan vara gammal eller felstavad.</p><p class="more"><a href="{u('')}">Till startsidan</a></p></div></header>"""
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
