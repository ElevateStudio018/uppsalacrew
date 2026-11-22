#!/usr/bin/env python3
"""v09 "Graffiti" – Uppsala Crew IF. Kör: python3 themes/v09/build.py"""
import json, html, shutil
from pathlib import Path
from datetime import date

V = "v09"
ROOT = Path(__file__).resolve().parents[2]
C = json.loads((ROOT / "content/content.json").read_text(encoding="utf-8"))
M = json.loads((ROOT / "docs/media/manifest.json").read_text(encoding="utf-8"))
OUT = ROOT / "docs" / V
SRC = Path(__file__).parent
SITE = "https://www.uppsalacrew.se"
B = f"/uppsalacrew/{V}"
MED = "/uppsalacrew/media"
ORG = C["org"]
PAGES = {p["slug"]: p for p in C["pages"]}
# diy-spot-filen visar en datumsatt årsmötesaffisch, inte en DIY-spot: används inte
SKIP = {"diy-spot"}
C["gallery"] = [g for g in C["gallery"] if g["image"] not in SKIP]
for _s in C["sports"]:
    _s["images"] = [x for x in _s["images"] if x not in SKIP]


def e(s):
    return html.escape(str(s), quote=True)


def u(slug):
    return f"{B}/{slug}/" if slug else f"{B}/"


def img(name, sizes="100vw", lazy=True, cls="", alt=None):
    m = M[name]
    srcset = ", ".join(f"{MED}/{name}-{w}.webp {min(w, m['w'])}w" for w in m["widths"])
    src = f"{MED}/{name}-{m['widths'][min(1, len(m['widths']) - 1)]}.webp"
    la = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{src}" srcset="{srcset}" sizes="{sizes}" width="{m["w"]}" height="{m["h"]}"'
            f' alt="{e(alt or m["alt"])}"{la}>')


def polaroid(name, caption=None, tilt=0, sizes="(min-width: 900px) 40vw, 90vw"):
    cap = f"<figcaption>{e(caption)}</figcaption>" if caption else ""
    return f'<figure class="pol" style="--t:{tilt}deg">{img(name, sizes)}{cap}</figure>'


def sticker(text, r=-3, cls=""):
    return f'<span class="sticker {cls}" style="--r:{r}deg">{e(text)}</span>'


def drip(top, bottom, seed=0):
    """SVG-avdelare: färgen ovanför rinner ner i nästa sektion."""
    drips = [(60, 14, 46), (190, 10, 30), (330, 18, 58), (520, 12, 36), (700, 16, 50),
             (880, 10, 28), (1040, 20, 62), (1230, 12, 40), (1370, 14, 34)]
    drips = [(x + (seed * 37) % 60, w, h) for x, w, h in drips]
    d = "M0 0 H1440 V14 "
    for x, w, h in sorted(drips, reverse=True):
        r = w / 2
        d += f"L{x + w} 14 L{x + w} {h - r} A{r} {r} 0 0 1 {x} {h - r} L{x} 14 "
    d += "L0 14 Z"
    return (f'<div class="drip" aria-hidden="true" style="background:var(--{bottom})">'
            f'<svg viewBox="0 0 1440 64" preserveAspectRatio="none" width="100%" height="64" focusable="false">'
            f'<path d="{d}" fill="var(--{top})"/></svg></div>')


def org_ld():
    return {"@context": "https://schema.org", "@type": "SportsOrganization", "@id": SITE + "/#org",
            "name": ORG["name"], "legalName": ORG["legal"], "url": SITE + "/", "logo": SITE + "/media/logo-rund-512.png",
            "email": ORG["email"], "telephone": ORG["phone_href"], "foundingDate": ORG["founded"],
            "taxID": ORG["orgnr"], "sport": ["Skateboard", "Snowboard", "Freeski"],
            "address": {"@type": "PostalAddress", "streetAddress": ORG["street"], "postalCode": ORG["zip"],
                        "addressLocality": ORG["city"], "addressCountry": "SE"},
            "sameAs": [ORG["instagram"], ORG["facebook"]]}


def crumbs_ld(trail):
    items = [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + (f"/{s}/" if s else "/")}
             for i, (n, s) in enumerate(trail)]
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


# ---------- Ramverk ----------
NAV_MAIN = [("skateboard", "Skate"), ("snowboard-och-freeski", "Snow &amp; ski"), ("skateskola", "Skateskola"),
            ("platser", "Platser"), ("tavlingar", "Tävlingar"), ("om-foreningen", "Föreningen")]
MENU = [("Sporter", ["skateboard", "snowboard-och-freeski", "skateskola", "tjejer"]),
        ("Platser", ["platser", "platser/sunnerstabacken", "platser/allis-uppsala", "platser/kap-rampen"]),
        ("Föreningen", ["om-foreningen", "tavlingar", "galleri", "engagera-dig", "partners", "vanliga-fragor", "kontakt"])]


def header(slug):
    links = "".join(
        f'<li><a href="{u(s)}"{" aria-current=\"page\"" if slug == s or slug.startswith(s + "/") else ""}>{t}</a></li>'
        for s, t in NAV_MAIN)
    groups = "".join(
        f'<div class="menu__g"><p class="menu__h">{g}</p><ul>' +
        "".join(f'<li><a href="{u(s)}">{e(PAGES[s]["title"])}</a></li>' for s in ss) + "</ul></div>"
        for g, ss in MENU)
    return f"""<a class="skip" href="#main">Hoppa till innehållet</a>
<header class="hd"><div class="hd__in">
<a class="hd__logo" href="{u('')}"><img src="{MED}/logo-rund-64.png" width="44" height="44" alt=""><span>Uppsala Crew</span></a>
<nav class="hd__nav" aria-label="Huvudmeny"><ul>{links}</ul></nav>
<a class="btn btn--o hd__cta" href="{u('bli-medlem')}">Bli medlem</a>
<button class="hd__menu" type="button" aria-expanded="false" aria-controls="menu"><span class="bars" aria-hidden="true"></span><span>Meny</span></button>
</div>
<div class="menu" id="menu" hidden><div class="menu__in">{groups}
<p class="menu__cta"><a class="btn btn--o" href="{u('bli-medlem')}">Bli medlem</a> <a class="btn btn--line" href="{u('integritetspolicy')}">Integritetspolicy</a></p></div></div>
</header>"""


def footer():
    fed = "".join(f'<li><a href="{e(f["url"])}" rel="noopener">{e(f["name"])}</a></li>' for f in C["partners"]["federations"])
    return f"""{drip('cream', 'ink', 3)}<footer class="ft"><div class="wrap ft__grid">
<div><img src="{MED}/logo-rund-192.png" width="96" height="96" alt="Uppsala Crew IF logotyp" loading="lazy">
<p class="ft__tag">{e(ORG['tagline'])}.</p></div>
<div><h2 class="ft__h">Kontakt</h2><ul class="ft__l">
<li><a href="mailto:{ORG['email']}">{ORG['email']}</a></li><li><a href="tel:{ORG['phone_href']}">{ORG['phone']}</a></li>
<li>{ORG['street']}, {ORG['zip']} {ORG['city']}</li>
<li><a href="{ORG['instagram']}" rel="noopener">Instagram {ORG['instagram_handle']}</a></li><li><a href="{ORG['facebook']}" rel="noopener">Facebook</a></li></ul></div>
<div><h2 class="ft__h">Ansluten till</h2><ul class="ft__l">{fed}</ul></div>
</div><div class="wrap ft__legal"><span>© {date.today().year} {ORG['legal']} · Org.nr {ORG['orgnr']}</span>
<a href="{u('integritetspolicy')}">Integritetspolicy</a><a href="{u('vanliga-fragor')}">Vanliga frågor</a></div></footer>"""


def page(slug, title, desc, body, trail=None, ld=None, out=None):
    canon = SITE + (f"/{slug}/" if slug else "/")
    lds = [org_ld()] + ([crumbs_ld(trail)] if trail else []) + (ld or [])
    ldh = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    full = title if slug == "" else f"{title} | Uppsala Crew IF"
    crumb = ""
    if trail and len(trail) > 1:
        crumb = '<nav class="crumbs wrap" aria-label="Brödsmulor"><ol>' + "".join(
            (f'<li><a href="{u(s)}">{e(n)}</a></li>' if i < len(trail) - 1 else f'<li aria-current="page">{e(n)}</li>')
            for i, (n, s) in enumerate(trail)) + "</ol></nav>"
    doc = f"""<!doctype html>
<html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full)}</title><meta name="description" content="{e(desc)}"><meta name="robots" content="noindex">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:locale" content="sv_SE"><meta property="og:site_name" content="Uppsala Crew IF">
<meta property="og:title" content="{e(full)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/media/graffiti-960.webp"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#121212"><link rel="icon" href="{MED}/logo-rund-64.png" type="image/png"><link rel="apple-touch-icon" href="{MED}/logo-rund-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Permanent+Marker&family=Work+Sans:wght@400;500;700&display=swap">
<link rel="stylesheet" href="{B}/assets/site.css"><script>document.documentElement.classList.add('js')</script>
{ldh}</head><body>
{header(slug)}
<main id="main">{crumb}{body}</main>
{footer()}
<script src="{B}/assets/site.js" defer></script></body></html>"""
    p = OUT / (out or (f"{slug}/index.html" if slug else "index.html"))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(doc, encoding="utf-8")


def T(slug):
    return PAGES[slug]["title"]


def trail_for(slug):
    t = [("Start", "")]
    if slug.startswith("platser/"):
        t.append(("Platser", "platser"))
    t.append((T(slug), slug))
    return t


def phero(kicker, h1, lead, image=None, label=None):
    pic = f'<div class="phero__img">{polaroid(image, None, 2, "(min-width: 900px) 40vw, 90vw").replace(" loading=\"lazy\" decoding=\"async\"", " fetchpriority=\"high\"")}</div>' if image else ""
    lab = f'<p class="marker">{e(label)}</p>' if label else ""
    return f"""<section class="phero{' phero--img' if image else ''}"><div class="wrap phero__grid"><div>
<p class="kicker">{e(kicker)}</p><h1>{e(h1)}</h1>{f'<p class="lead">{e(lead)}</p>' if lead else ''}{lab}</div>{pic}</div></section>{drip('ink', 'cream', 7)}"""


def cta_band():
    m = C["membership"]
    return f"""{drip('cream', 'orange', 1)}<section class="band"><div class="wrap band__in">
<div><h2>Bli medlem för {e(m['price'])}</h2><p>{e(m['price_note'])} Försäkring på föreningens aktiviteter ingår.</p></div>
<a class="btn btn--ink" href="{u('bli-medlem')}">Till medlemsformuläret</a></div></section>{drip('orange', 'cream', 2)}"""


def paras(ps):
    return "".join(f"<p>{e(p)}</p>" for p in ps)


def member_form():
    return f"""<form class="form" data-mail="{ORG['email']}" data-subject="Medlemsansökan Uppsala Crew IF" action="mailto:{ORG['email']}" method="post" enctype="text/plain">
<h2 class="h3">Medlemsansökan</h2>
<div class="field"><label for="m-namn">Namn</label><input id="m-namn" name="namn" data-label="Namn" autocomplete="name" required></div>
<div class="field"><label for="m-epost">E-post</label><input id="m-epost" name="epost" type="email" data-label="E-post" autocomplete="email" required></div>
<div class="field"><label for="m-sport">Vad åker du?</label><select id="m-sport" name="sport" data-label="Sport"><option value="">Välj</option><option>Skateboard</option><option>Snowboard</option><option>Freeski</option><option>Flera av dem</option></select></div>
<div class="field"><label for="m-belopp">Medlemsavgift</label><select id="m-belopp" name="belopp" data-label="Avgift"><option>50 kr</option><option>75 kr</option><option selected>100 kr</option></select></div>
<label class="check"><input type="checkbox" required><span>Jag godkänner att föreningen sparar mina uppgifter enligt <a href="{u('integritetspolicy')}">integritetspolicyn</a>.</span></label>
<button class="btn btn--o" type="submit">Skicka ansökan</button>
<p class="form-status" role="status" aria-live="polite"></p></form>"""


def contact_form():
    return f"""<form class="form" data-mail="{ORG['email']}" data-subject="Meddelande via uppsalacrew.se" action="mailto:{ORG['email']}" method="post" enctype="text/plain">
<h2 class="h3">Skriv till oss</h2>
<div class="field"><label for="k-namn">Namn</label><input id="k-namn" name="namn" data-label="Namn" autocomplete="name" required></div>
<div class="field"><label for="k-epost">E-post</label><input id="k-epost" name="epost" type="email" data-label="E-post" autocomplete="email" required></div>
<div class="field"><label for="k-msg">Meddelande</label><textarea id="k-msg" name="meddelande" rows="5" data-label="Meddelande" required></textarea></div>
<label class="check"><input type="checkbox" required><span>Jag godkänner att föreningen sparar mina uppgifter enligt <a href="{u('integritetspolicy')}">integritetspolicyn</a>.</span></label>
<button class="btn btn--o" type="submit">Skicka meddelande</button>
<p class="form-status" role="status" aria-live="polite"></p></form>"""


# ---------- Sidor ----------
def home():
    i = C["intro"]
    facts = "".join(f'<li style="--r:{r}deg" class="sticker sticker--fact"><b>{e(f["value"])}</b><span>{e(f["label"])}</span></li>'
                    for f, r in zip(C["facts"], (-4, 3, -2, 4)))
    sports = ""
    for n, s in enumerate(C["sports"]):
        sports += f"""<article class="row{' row--flip' if n % 2 else ''}">
<div class="row__img">{polaroid(s['hero'], s['where'], (-2, 2, -1.5)[n])}</div>
<div class="row__txt"><p class="num">0{n + 1}</p><h3 class="h2"><a href="{u(s['slug'])}">{e(s['title'])}</a></h3><p>{e(s['short'])}</p>
<p class="tags">{sticker(s['when'], -2)}{sticker(s['where'].split(',')[0], 2, 'sticker--o')}</p>
<a class="more" href="{u(s['slug'])}">Läs om {e(s['title'].lower())}</a></div></article>"""
    comps = "".join(f"""<li><h3>{e(c['title'])}</h3><p class="meta">{e(c['sport'])} · {e(c['place'])}</p><p>{e(c['text'])}</p></li>"""
                    for c in C["competitions"]["items"])
    places = "".join(f'<li><a href="{u("platser/" + p["slug"])}"><span class="pl__n">0{k + 1}</span><span class="pl__t">{e(p["title"])}</span><span class="pl__s">{e(p["short"])}</span></a></li>'
                     for k, p in enumerate(C["places"]))
    gal = "".join(polaroid(g["image"], g["caption"], t, "(min-width: 900px) 25vw, 45vw")
                  for g, t in zip(C["gallery"][:4], (-3, 2, -1, 3)))
    g = C["girls"]
    body = f"""<section class="hero">{img('graffiti', '100vw', False, 'hero__bg')}
<div class="wrap hero__in"><div class="plate"><p class="kicker">Uppsala Crew IF · sedan {ORG['founded']}</p>
<h1>{e(i['headline'])}</h1><p class="lead">{e(i['lead'])}</p>
<p class="btns"><a class="btn btn--o" href="{u('bli-medlem')}">Bli medlem</a><a class="btn btn--line" href="{u('skateskola')}">Skateskolan</a></p></div>
<p class="marker hero__tag">Målad av Gijs Weijer</p></div></section>
{drip('ink', 'cream')}
<section class="sec"><div class="wrap"><ul class="facts">{facts}</ul></div></section>
<section class="sec sec--tight"><div class="wrap"><h2 class="h1">Tre sätt att åka</h2>{sports}</div></section>
{drip('cream', 'ink', 4)}
<section class="sec sec--ink"><div class="wrap split"><div><p class="kicker">Tävlingar</p><h2>Öppna för alla nivåer</h2><p class="lead">{e(C['competitions']['lead'])}</p>
<a class="btn btn--o" href="{u('tavlingar')}">Om tävlingarna</a></div><ul class="comps">{comps}</ul></div></section>
{drip('ink', 'cream', 5)}
<section class="sec"><div class="wrap split split--rev"><div>{polaroid(g['image'], 'Tjejsatsningen', -2)}</div>
<div><p class="kicker">{e(g['title'])}</p><h2>Fler tjejer på brädan och i parken</h2><p class="lead">{e(g['lead'])}</p><a class="more" href="{u('tjejer')}">Så gör vi</a></div></div></section>
<section class="sec sec--tight"><div class="wrap"><h2>Här håller vi till</h2><ul class="pl">{places}</ul></div></section>
{cta_band()}
<section class="sec"><div class="wrap"><div class="head-row"><h2>Från backen och rampen</h2><a class="more" href="{u('galleri')}">Hela galleriet</a></div>
<div class="wall wall--4">{gal}</div></div></section>"""
    page("", "Uppsala Crew IF – skateboard, snowboard och freeski i Uppsala",
         "Uppsala Crew IF är föreningen för skateboard, snowboard och freeski i Uppsala. Skateskola, tävlingar och åkning för alla nivåer. Medlemskap 50–100 kr per år.", body)


def sport(s):
    sched = ""
    if s.get("schedule"):
        sched = '<table class="tbl"><caption>Träningstider</caption><tbody>' + "".join(
            f'<tr><th scope="row">{e(r["k"])}</th><td>{e(r["v"])}</td></tr>' for r in s["schedule"]) + "</tbody></table>"
    secs = "".join(f'<section class="txt"><h2>{e(x["h"])}</h2>{paras(x["p"])}</section>' for x in s["sections"])
    imgs = [x for x in s["images"] if x != s["hero"]]
    wall = "".join(polaroid(x, None, t, "(min-width: 900px) 30vw, 45vw") for x, t in zip(imgs, (-2, 3, -1, 2, -3, 1)))
    body = phero("Sport", s["title"], s["short"], s["hero"], s["when"]) + f"""
<section class="sec sec--tight"><div class="wrap split split--wide"><div class="prose">{secs}</div>
<aside class="side"><dl class="kv"><dt>Var</dt><dd>{e(s['where'])}</dd><dt>När</dt><dd>{e(s['when'])}</dd></dl>{sched}
<a class="btn btn--o" href="{u('bli-medlem')}">Bli medlem</a></aside></div></section>
{f'<section class="sec sec--tight"><div class="wrap"><h2>Bilder</h2><div class="wall">{wall}</div></div></section>' if wall else ''}
{cta_band()}"""
    page(s["slug"], f"{s['title']} i Uppsala", s["meta_description"], body, trail_for(s["slug"]),
         [{"@context": "https://schema.org", "@type": "Service", "name": f"{s['title']} med Uppsala Crew IF",
           "serviceType": s["title"], "description": s["short"], "provider": {"@id": SITE + "/#org"}, "areaServed": "Uppsala"}])


def about():
    a = C["about"]
    tl = "".join(f'<li><span class="sticker" style="--r:{r}deg">{e(t["year"])}</span><p>{e(t["text"])}</p></li>'
                 for t, r in zip(a["timeline"], (-4, 3, -2, 4)))
    body = phero("Föreningen", T("om-foreningen"), a["lead"], "graffiti") + f"""
<section class="sec sec--tight"><div class="wrap"><h2>Så har det gått</h2><ol class="tl">{tl}</ol></div></section>
{drip('cream', 'ink', 2)}
<section class="sec sec--ink"><div class="wrap split"><div><h2>Vision</h2><p class="lead">{e(a['vision'])}</p></div>
<div><h2>Organisation</h2><p>{e(a['org_text'])}</p><p>Org.nr {ORG['orgnr']}. {ORG['street']}, {ORG['zip']} {ORG['city']}.</p>
<a class="btn btn--o" href="{u('engagera-dig')}">Engagera dig</a></div></div></section>{drip('ink', 'cream', 6)}"""
    page("om-foreningen", T("om-foreningen"), a["meta_description"], body, trail_for("om-foreningen"))


def girls():
    g = C["girls"]
    secs = "".join(f'<section class="txt"><h2>{e(x["h"])}</h2>{paras(x["p"])}</section>' for x in g["sections"])
    body = phero("Föreningen", g["title"], g["lead"], g["image"], "Egen tjejklass") + f"""
<section class="sec sec--tight"><div class="wrap split split--wide"><div class="prose">{secs}</div>
<aside class="side"><p>Frågor om satsningen?</p><a class="btn btn--o" href="{u('kontakt')}">Kontakta oss</a></aside></div></section>{cta_band()}"""
    page("tjejer", g["title"], g["meta_description"], body, trail_for("tjejer"))


def places():
    rows = ""
    for k, p in enumerate(C["places"]):
        pic = polaroid(p["image"], p["address"], (-2, 2, -1)[k]) if p["image"] else f'<div class="noimg"><span class="marker">{e(p["title"])}</span></div>'
        rows += f"""<article class="row{' row--flip' if k % 2 else ''}"><div class="row__img">{pic}</div>
<div class="row__txt"><p class="num">0{k + 1}</p><h2><a href="{u('platser/' + p['slug'])}">{e(p['title'])}</a></h2><p class="meta">{e(p['address'])}</p><p>{e(p['short'])}</p>
<a class="more" href="{u('platser/' + p['slug'])}">Mer om {e(p['title'])}</a></div></article>"""
    body = phero("Platser", T("platser"), "Backen på vintern, hallen när det blir kallt och minirampen när det är varmt.") + \
        f'<section class="sec sec--tight"><div class="wrap">{rows}</div></section>{cta_band()}'
    page("platser", "Platser där vi åker", "Uppsala Crew IF håller till i Sunnerstabacken, på Allis Uppsala och vid KAP-rampen på Kapellgärdet. Adresser och vad som finns på varje plats.", body, trail_for("platser"))


def place(p):
    slug = "platser/" + p["slug"]
    others = "".join(f'<li><a href="{u("platser/" + o["slug"])}">{e(o["title"])}</a></li>' for o in C["places"] if o is not p)
    body = phero("Plats", p["title"], p["short"], p["image"], p["address"]) + f"""
<section class="sec sec--tight"><div class="wrap split split--wide"><div class="prose txt">{paras(p['body'])}</div>
<aside class="side"><dl class="kv"><dt>Adress</dt><dd>{e(p['address'])}</dd></dl><p class="menu__h">Andra platser</p><ul class="lst">{others}</ul></aside></div></section>{cta_band()}"""
    page(slug, f"{p['title']} – Uppsala Crew IF", f"{p['title']}, {p['address']}. {p['short']}", body, trail_for(slug),
         [{"@context": "https://schema.org", "@type": "SportsActivityLocation", "name": p["title"], "description": p["short"],
           "address": {"@type": "PostalAddress", "streetAddress": p["address"].split(",")[0], "addressLocality": "Uppsala", "addressCountry": "SE"},
           "url": SITE + f"/{slug}/", **({"image": SITE + f"/media/{p['image']}-960.webp"} if p["image"] else {})}])


def comps():
    c = C["competitions"]
    rows = ""
    for k, it in enumerate(c["items"]):
        cls = "".join(sticker(x, (-3, 2, -1, 3)[n % 4], "sticker--o" if n == 0 else "") for n, x in enumerate(it["classes"]))
        rows += f"""<article class="row{' row--flip' if k % 2 else ''}"><div class="row__img">{polaroid(it['image'], it['place'], (-2, 2)[k])}</div>
<div class="row__txt"><p class="num">0{k + 1}</p><h2>{e(it['title'])}</h2><p class="meta">{e(it['sport'])} · {e(it['place'])}</p><p>{e(it['text'])}</p>
<p class="menu__h">Klasser</p><p class="tags">{cls}</p></div></article>"""
    body = phero("Föreningen", T("tavlingar"), c["lead"], label="Alla nivåer") + f'<section class="sec sec--tight"><div class="wrap">{rows}</div></section>{cta_band()}'
    page("tavlingar", T("tavlingar"), c["meta_description"], body, trail_for("tavlingar"))


def gallery():
    tilts = (-3, 2, -1, 3, -2, 1)
    wall = "".join(polaroid(g["image"], g["caption"], tilts[k % 6], "(min-width: 900px) 30vw, 45vw") for k, g in enumerate(C["gallery"]))
    body = phero("Föreningen", T("galleri"), "Bilder från Sunnerstabacken, Allis, KAP-rampen och skateskolan.") + \
        f'<section class="sec sec--tight"><div class="wrap"><div class="wall">{wall}</div></div></section>{cta_band()}'
    page("galleri", "Galleri", "Bilder från Uppsala Crew IF: snowboard och freeski i Sunnerstabacken, skateboard på Allis och KAP-rampen, skateskolan och graffitin.", body, trail_for("galleri"))


def engage():
    g = C["engage"]
    roles = "".join(f'<li><span class="num">0{k + 1}</span><div><h2 class="h3">{e(r["title"])}</h2><p>{e(r["text"])}</p></div></li>' for k, r in enumerate(g["roles"]))
    body = phero("Föreningen", T("engagera-dig"), g["lead"], "instruktorer", "Ideellt") + f"""
<section class="sec sec--tight"><div class="wrap"><ol class="roles">{roles}</ol>
<p class="btns"><a class="btn btn--o" href="{u('kontakt')}">Hör av dig</a><a class="btn btn--line-ink" href="mailto:{ORG['email']}">{ORG['email']}</a></p></div></section>"""
    page("engagera-dig", T("engagera-dig"), g["meta_description"], body, trail_for("engagera-dig"))


def partners():
    p = C["partners"]
    fed = "".join(f'<li><a href="{e(f["url"])}" rel="noopener">{e(f["name"])}</a></li>' for f in p["federations"])
    sp = "".join(sticker(s, (-3, 2, -2, 4, -1, 3)[k], "sticker--big" + (" sticker--o" if k % 3 == 0 else "")) for k, s in enumerate(p["sponsors"]))
    body = phero("Föreningen", T("partners"), p["lead"]) + f"""
<section class="sec sec--tight"><div class="wrap split"><div><h2>Förbund och samarbeten</h2><ul class="lst lst--big">{fed}</ul></div>
<div><h2>Sponsorer</h2><p>{e(p['sponsors_note'])}</p><p class="tags tags--wall">{sp}</p></div></div></section>{cta_band()}"""
    page("partners", T("partners"), p["meta_description"], body, trail_for("partners"))


def membership():
    m = C["membership"]
    ben = "".join(f"<li>{e(b)}</li>" for b in m["benefits"])
    steps = "".join(f'<li><span class="num">0{k + 1}</span><p>{e(s)}</p></li>' for k, s in enumerate(m["steps"]))
    body = phero("Medlemskap", T("bli-medlem"), m["price_note"], label=m["price"]) + f"""
<section class="sec sec--tight"><div class="wrap split split--wide"><div><h2>Det här ingår</h2><ul class="checks">{ben}</ul>
<h2>Så går det till</h2><ol class="steps">{steps}</ol></div><div>{member_form()}</div></div></section>"""
    page("bli-medlem", "Bli medlem", m["meta_description"], body, trail_for("bli-medlem"))


def faq():
    qs = "".join(f'<details class="faq"><summary>{e(q["q"])}</summary><p>{e(q["a"])}</p></details>' for q in C["faq"])
    body = phero("Föreningen", T("vanliga-fragor"), "Svar om medlemskap, försäkring, skateskolan och tävlingar.") + \
        f'<section class="sec sec--tight"><div class="wrap narrow">{qs}<p class="btns"><a class="btn btn--o" href="{u("kontakt")}">Fråga oss något annat</a></p></div></section>'
    page("vanliga-fragor", T("vanliga-fragor"), "Vanliga frågor om Uppsala Crew IF: medlemsavgift, försäkring, skateskolan, utrustning och tävlingar.", body, trail_for("vanliga-fragor"),
         [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
             {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in C["faq"]]}])


def contact():
    body = phero("Kontakt", T("kontakt"), "Mejla, ring eller skriv i formuläret. Aktiviteter meddelas på Instagram.") + f"""
<section class="sec sec--tight"><div class="wrap split split--wide"><div>
<p class="big"><a href="mailto:{ORG['email']}">{ORG['email']}</a><a href="tel:{ORG['phone_href']}">{ORG['phone']}</a></p>
<dl class="kv"><dt>Postadress</dt><dd>{ORG['street']}<br>{ORG['zip']} {ORG['city']}</dd><dt>Alternativ e-post</dt><dd><a href="mailto:{ORG['email_alt']}">{ORG['email_alt']}</a></dd>
<dt>Instagram</dt><dd><a href="{ORG['instagram']}" rel="noopener">{ORG['instagram_handle']}</a></dd><dt>Facebook</dt><dd><a href="{ORG['facebook']}" rel="noopener">Uppsala Crew IF</a></dd>
<dt>Org.nr</dt><dd>{ORG['orgnr']}</dd></dl></div><div>{contact_form()}</div></div></section>"""
    page("kontakt", T("kontakt"), f"Kontakta Uppsala Crew IF: {ORG['email']}, {ORG['phone']}, {ORG['street']}, {ORG['city']}.", body, trail_for("kontakt"))


def privacy():
    secs = "".join(f'<section class="txt"><h2>{e(x["h"])}</h2><p>{e(x["p"])}</p></section>' for x in C["privacy"])
    body = phero("Föreningen", T("integritetspolicy"), "Så behandlar Uppsala Crew IF dina personuppgifter.") + \
        f'<section class="sec sec--tight"><div class="wrap narrow prose">{secs}</div></section>'
    page("integritetspolicy", T("integritetspolicy"), "Uppsala Crew IF:s integritetspolicy: vilka personuppgifter vi behandlar, varför, hur länge och dina rättigheter.", body, trail_for("integritetspolicy"))


def notfound():
    body = f"""<section class="hero hero--404">{img('graffiti', '100vw', False, 'hero__bg')}<div class="wrap hero__in"><div class="plate">
<p class="kicker">Fel 404</p><h1>Sidan finns inte</h1><p class="lead">Länken kan vara gammal eller felstavad.</p>
<p class="btns"><a class="btn btn--o" href="{u('')}">Till startsidan</a><a class="btn btn--line" href="{u('kontakt')}">Kontakt</a></p></div></div></section>{drip('ink', 'cream')}"""
    page("404", "Sidan finns inte", "Sidan kunde inte hittas på Uppsala Crew IF:s webbplats.", body, out="404.html")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    for f in ("site.css", "site.js"):
        shutil.copy(SRC / f, OUT / "assets" / f)
    home(); about(); girls(); places(); comps(); gallery(); engage(); partners(); membership(); faq(); contact(); privacy(); notfound()
    for s in C["sports"]:
        sport(s)
    for p in C["places"]:
        place(p)
    n = len(list(OUT.rglob("*.html")))
    print(f"{V}: {n} sidor skrivna till {OUT}")


if __name__ == "__main__":
    main()
