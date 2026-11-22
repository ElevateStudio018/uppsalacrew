#!/usr/bin/env python3
"""v05 "Rutnät" – brutalistiskt rutnät. Läser content/content.json och skriver docs/v05/."""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C = json.loads((ROOT / "content/content.json").read_text(encoding="utf-8"))
MAN = json.loads((ROOT / "docs/media/manifest.json").read_text(encoding="utf-8"))
OUT = ROOT / "docs/v05"
B = "/uppsalacrew/v05"
M = "/uppsalacrew/media"
SITE = C["org"]["site"]
PREVIEW = "https://elevatestudio018.github.io/uppsalacrew"
ORG = C["org"]
PAGES = {p["slug"]: p for p in C["pages"]}
SPORTS = {s["slug"]: s for s in C["sports"]}
PLACES = {p["slug"]: p for p in C["places"]}
# diy-spot-filerna i mediepoolen innehåller en datumsatt årsmötesaffisch, inte en DIY-spot: utesluts.
SKIP = {"diy-spot"}
for _s in C["sports"]:
    _s["images"] = [n for n in _s["images"] if n not in SKIP]
C["gallery"] = [g for g in C["gallery"] if g["image"] not in SKIP]


def e(s):
    return html.escape(str(s), quote=True)


def u(slug):
    return f"{B}/{slug}/" if slug else f"{B}/"


def img(name, sizes="100vw", lazy=True, alt=None, cls=""):
    m = MAN[name]
    ws = m["widths"]
    srcset = ", ".join(f"{M}/{name}-{w}.webp {w}w" for w in ws)
    src = f"{M}/{name}-{max(w for w in ws if w <= 960)}.webp"
    a = 'loading="lazy" decoding="async"' if lazy else 'fetchpriority="high" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{src}" srcset="{srcset}" sizes="{sizes}" width="{m["w"]}" height="{m["h"]}" '
            f'alt="{e(alt or m["alt"])}" {a}>')


def duo(name, sizes="100vw", lazy=True, alt=None, cls=""):
    return f'<figure class="duo {cls}">{img(name, sizes, lazy, alt)}</figure>'


# ------------------------------------------------------------------ JSON-LD
def org_ld():
    return {
        "@context": "https://schema.org", "@type": "SportsOrganization", "@id": SITE + "/#org",
        "name": ORG["name"], "legalName": ORG["legal"], "url": SITE + "/",
        "logo": PREVIEW + "/media/logo-rund-512.png",
        "description": ORG["tagline"], "foundingDate": ORG["founded"],
        "email": ORG["email"], "telephone": ORG["phone_href"],
        "identifier": {"@type": "PropertyValue", "propertyID": "Organisationsnummer", "value": ORG["orgnr"]},
        "address": {"@type": "PostalAddress", "streetAddress": ORG["street"], "postalCode": ORG["zip"].replace(" ", ""),
                    "addressLocality": ORG["city"], "addressCountry": "SE"},
        "sport": ["Skateboarding", "Snowboarding", "Freestyle skiing"],
        "sameAs": [ORG["instagram"], ORG["facebook"]],
    }


def crumbs_ld(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{SITE}/{s}/" if s else SITE + "/"}
        for i, (n, s) in enumerate(trail)]}


# ------------------------------------------------------------------ ramverk
NAV = [("skateboard", "Skateboard"), ("snowboard-och-freeski", "Snow/Freeski"), ("skateskola", "Skateskola"),
       ("platser", "Platser"), ("tavlingar", "Tävlingar"), ("om-foreningen", "Föreningen"), ("kontakt", "Kontakt")]


def header(slug):
    def cur(s):
        top = slug.split("/")[0]
        return ' aria-current="page"' if s == slug or (s == top and slug) else ""
    links = "".join(f'<li><a class="nav__a" href="{u(s)}"{cur(s)}>{t}</a></li>' for s, t in NAV)
    all_links = "".join(f'<li><a href="{u(p["slug"])}">{e(p["title"])}</a></li>' for p in C["pages"])
    return f"""<a class="skip" href="#main">Hoppa till innehållet</a>
<header class="hd">
 <a class="hd__logo" href="{B}/" aria-label="Uppsala Crew IF, startsida"><img src="{M}/logo-ljus-192.png" width="192" height="192" alt=""><span>Uppsala<br>Crew IF</span></a>
 <nav class="nav" aria-label="Huvudmeny"><ul>{links}</ul></nav>
 <a class="hd__cta" href="{u('bli-medlem')}">Bli medlem <span aria-hidden="true">→</span></a>
 <button class="hd__btn" type="button" aria-expanded="false" aria-controls="meny">Meny</button>
</header>
<div class="menu" id="meny" hidden><nav aria-label="Alla sidor"><ul>{all_links}</ul></nav></div>"""


def footer():
    cols = {}
    for p in C["pages"]:
        if p["slug"]:
            cols.setdefault("Sidor", []).append(p)
    links = "".join(f'<li><a href="{u(p["slug"])}">{e(p["title"])}</a></li>' for p in cols["Sidor"])
    places = "&nbsp;/&nbsp;".join(["Sunnerstabacken", "Allis Uppsala", "KAP-rampen", "Kapellgärdet"])
    return f"""<footer class="ft">
 <div class="ft__grid">
  <div class="cell ft__id"><img src="{M}/logo-rund-192.png" width="96" height="96" alt="Uppsala Crew IF logotyp" loading="lazy"><p class="ft__name">{e(ORG['legal'])}</p><p class="mono">{e(ORG['tagline'])}</p></div>
  <div class="cell"><p class="lbl">Kontakt</p><ul class="mono ft__list"><li><a href="mailto:{ORG['email']}">{ORG['email']}</a></li><li><a href="tel:{ORG['phone_href']}">{ORG['phone']}</a></li><li>{ORG['street']}, {ORG['zip']} {ORG['city']}</li><li>Org.nr {ORG['orgnr']}</li></ul></div>
  <div class="cell"><p class="lbl">Följ</p><ul class="mono ft__list"><li><a href="{ORG['instagram']}" rel="noopener">Instagram {ORG['instagram_handle']}</a></li><li><a href="{ORG['facebook']}" rel="noopener">Facebook</a></li></ul><p class="lbl" style="margin-top:1.5rem">Platser</p><p class="mono">{places}</p></div>
  <div class="cell ft__nav"><p class="lbl">Sidor</p><ul class="ft__links">{links}</ul></div>
 </div>
 <p class="ft__bar mono"><span>© {ORG['name']}</span><span>Förhandsvisning v05 / Rutnät</span></p>
</footer>"""


def crumbs(trail):
    lis = []
    for i, (n, s) in enumerate(trail):
        if i == len(trail) - 1:
            lis.append(f'<li aria-current="page">{e(n)}</li>')
        else:
            lis.append(f'<li><a href="{u(s)}">{e(n)}</a></li>')
    return f'<nav class="crumbs mono" aria-label="Brödsmulor"><ol>{"".join(lis)}</ol></nav>'


def write(slug, title, desc, body, ld=None, trail=None, og="snowboard-hopp", path=None):
    lds = [org_ld()] + (ld or [])
    if trail:
        lds.append(crumbs_ld(trail))
    full = f"{title} | {ORG['name']}" if slug else f"{ORG['name']} – {ORG['tagline']}"
    canon = f"{SITE}/{slug}/" if slug else SITE + "/"
    ldjs = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    doc = f"""<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:locale" content="sv_SE">
<meta property="og:site_name" content="{e(ORG['name'])}">
<meta property="og:title" content="{e(full)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{PREVIEW}/media/{og}-960.webp">
<meta name="theme-color" content="#0D0D0D">
<link rel="icon" href="{M}/logo-rund-64.png" type="image/png">
<link rel="apple-touch-icon" href="{M}/logo-rund-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Space+Grotesk:wght@400;700&display=swap">
<link rel="stylesheet" href="{B}/assets/site.css">
<script>document.documentElement.classList.add("js")</script>
{ldjs}
</head>
<body>
{header(slug)}
<main id="main">
{body}
</main>
{footer()}
<script src="{B}/assets/site.js" defer></script>
</body>
</html>
"""
    p = OUT / (path or (f"{slug}/index.html" if slug else "index.html"))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(doc, encoding="utf-8")


def pagehead(trail, label, h1, lead, side=""):
    sidecell = f'<div class="cell cell--side rv">{side}</div>' if side else ""
    return f"""<section class="ph">
 {crumbs(trail)}
 <div class="g g--ph">
  <div class="cell cell--h1 rv"><p class="lbl">{e(label)}</p><h1>{e(h1)}</h1></div>
  <div class="cell cell--lead rv"><p class="lead">{e(lead)}</p></div>
  {sidecell}
 </div>
</section>"""


def data(rows):
    return '<dl class="data">' + "".join(f"<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>" for k, v in rows) + "</dl>"


def band():
    items = ["Sunnerstabacken", "Allis Uppsala", "KAP-rampen", "Kapellgärdet", "Ulleråkersvägen 22", "Uppsala"]
    seq = "".join(f"<span>{e(i)}</span><span class=\"sep\" aria-hidden=\"true\">/</span>" for i in items)
    return f"""<div class="band" aria-label="Platser där vi åker: {e(', '.join(items[:4]))}"><div class="band__track" aria-hidden="true"><div>{seq}</div><div>{seq}</div></div></div>"""


def sections_html(secs, start=1):
    out = []
    for i, s in enumerate(secs):
        ps = "".join(f"<p>{e(p)}</p>" for p in s["p"])
        off = " sec--off" if i % 2 else ""
        out.append(f"""<section class="sec{off}"><div class="g g--txt">
 <div class="cell cell--num rv"><span class="num">{i + start:02d}</span></div>
 <div class="cell cell--txt rv"><h2>{e(s['h'])}</h2>{ps}</div>
</div></section>""")
    return "\n".join(out)


def cta(h="Bli medlem för 50–100 kr per år", t=None, href="bli-medlem", label="Till medlemsansökan"):
    t = t or C["membership"]["price_note"]
    return f"""<section class="sec sec--off"><div class="g g--cta">
 <div class="cell cell--blue rv"><p class="lbl">Medlemskap</p><h2>{e(h)}</h2><p>{e(t)}</p></div>
 <a class="cell cell--go inv rv" href="{u(href)}"><span>{e(label)}</span><span class="arrow" aria-hidden="true">→</span></a>
</div></section>"""


def form(kind):
    consent = f'<label class="chk"><input type="checkbox" name="samtycke" required> <span>Jag godkänner att föreningen behandlar mina uppgifter enligt <a href="{u("integritetspolicy")}">integritetspolicyn</a>.</span></label>'
    if kind == "join":
        fields = """<label class="fld"><span>Namn</span><input name="Namn" autocomplete="name" required></label>
<label class="fld"><span>E-post</span><input type="email" name="E-post" autocomplete="email" required></label>
<label class="fld"><span>Födelseår</span><input name="Födelseår" inputmode="numeric" maxlength="4"></label>
<label class="fld"><span>Sport</span><select name="Sport"><option>Skateboard</option><option>Snowboard</option><option>Freeski</option><option>Flera</option></select></label>
<label class="fld fld--w"><span>Meddelande (valfritt)</span><textarea name="Meddelande" rows="3"></textarea></label>"""
        subj, btn = "Medlemsansökan Uppsala Crew IF", "Skicka ansökan"
    else:
        fields = """<label class="fld"><span>Namn</span><input name="Namn" autocomplete="name" required></label>
<label class="fld"><span>E-post</span><input type="email" name="E-post" autocomplete="email" required></label>
<label class="fld fld--w"><span>Meddelande</span><textarea name="Meddelande" rows="5" required></textarea></label>"""
        subj, btn = "Meddelande via uppsalacrew.se", "Skicka meddelande"
    return f"""<form class="form" data-mail="{ORG['email']}" data-subject="{e(subj)}" action="mailto:{ORG['email']}" method="post" enctype="text/plain">
{fields}
<div class="fld--w">{consent}</div>
<div class="fld--w form__end"><button class="btn" type="submit">{btn}</button><p class="mono form__note">Formuläret öppnar ett förifyllt mejl som du skickar själv.</p></div>
<p class="form-status mono fld--w" role="status" aria-live="polite"></p>
</form>"""


# ------------------------------------------------------------------ sidor
def build_home():
    i = C["intro"]
    facts = "".join(f'<div class="cell cell--fact rv"><p class="lbl">{e(f["label"])}</p><p class="fact">{e(f["value"])}</p></div>' for f in C["facts"])
    sports = ""
    spans = ["s7", "s5", "s12"]
    for k, s in enumerate(C["sports"]):
        sports += f"""<a class="cell cell--sport inv rv {spans[k]}" href="{u(s['slug'])}">
 {duo(s['hero'], '(min-width:900px) 50vw, 100vw')}
 <div class="sport__b"><p class="lbl">{k + 1:02d} / Sport</p><h3>{e(s['title'])}</h3><p>{e(s['short'])}</p>
 {data([("Var", s['where']), ("När", s['when'])])}</div></a>"""
    comps = ""
    for c in C["competitions"]["items"]:
        comps += f"""<a class="cell cell--comp inv rv" href="{u('tavlingar')}"><p class="lbl">{e(c['sport'])} / {e(c['place'])}</p><h3>{e(c['title'])}</h3><ul class="chips">{''.join(f'<li>{e(x)}</li>' for x in c['classes'])}</ul></a>"""
    gal = "".join(f'<div class="cell cell--gal rv">{duo(g["image"], "(min-width:900px) 25vw, 50vw", alt=None)}</div>' for g in C["gallery"][:4])
    body = f"""<section class="hero">
 <div class="g g--hero">
  <div class="cell cell--h1 rv"><p class="lbl">Uppsala Crew IF / Sedan {ORG['founded']}</p><h1>{e(i['headline'])}</h1></div>
  <div class="cell cell--lead rv"><p class="lead">{e(i['lead'])}</p><div class="btns"><a class="btn" href="{u('bli-medlem')}">Bli medlem</a><a class="btn btn--line" href="{u('skateskola')}">Skateskolan</a></div></div>
  <div class="cell cell--heroimg rv">{duo('snowboard-hopp', '100vw', lazy=False)}</div>
 </div>
</section>
{band()}
<section class="sec"><h2 class="vh">Fakta om föreningen</h2><div class="g g--facts">{facts}</div></section>
<section class="sec sec--off"><div class="sechd"><p class="lbl">Sporter</p><h2>Tre sporter, en förening</h2></div><div class="g g--sports">{sports}</div></section>
<section class="sec"><div class="g g--split">
 <div class="cell cell--dark rv"><p class="lbl">Tjejsatsning</p><h2>{e(C['girls']['title'])}</h2><p>{e(C['girls']['lead'])}</p><p><a class="link" href="{u('tjejer')}">Läs om satsningen</a></p></div>
 <div class="cell cell--img rv">{duo(C['girls']['image'], '(min-width:900px) 50vw, 100vw')}</div>
</div></section>
<section class="sec sec--off"><div class="sechd"><p class="lbl">Tävlingar</p><h2>Återkommande tävlingar</h2><p>{e(C['competitions']['lead'])}</p></div><div class="g g--two">{comps}</div></section>
<section class="sec"><div class="sechd"><p class="lbl">Galleri</p><h2>Från backen och rampen</h2></div><div class="g g--gal4">{gal}</div><p class="more"><a class="link" href="{u('galleri')}">Hela galleriet</a></p></section>
{cta()}"""
    write("", "Start", C["intro"]["lead"][:155].rsplit(" ", 1)[0] + ".", body)


def build_sport(slug):
    s = SPORTS[slug]
    trail = [("Start", ""), (s["title"], slug)]
    rows = s.get("schedule") and [(r["k"], r["v"]) for r in s["schedule"]] or [("Var", s["where"]), ("När", s["when"])]
    body = pagehead(trail, "Sport", s["title"], s["short"], data(rows))
    body += f'<section class="sec"><div class="g g--one"><div class="cell cell--wide rv">{duo(s["hero"], "100vw", lazy=False)}</div></div></section>'
    body += sections_html(s["sections"])
    imgs = "".join(f'<div class="cell cell--gal rv">{duo(n, "(min-width:900px) 33vw, 50vw")}</div>' for n in s["images"])
    body += f'<section class="sec"><div class="sechd"><p class="lbl">Bilder</p><h2>{e(s["title"])} i Uppsala</h2></div><div class="g g--gal3">{imgs}</div></section>'
    rel = [p for p in C["places"] if p["title"] in s["where"]]
    if rel:
        cells = "".join(f'<a class="cell cell--place inv rv" href="{u("platser/" + p["slug"])}"><p class="lbl">Plats</p><h3>{e(p["title"])}</h3><p class="mono">{e(p["address"])}</p></a>' for p in rel)
        body += f'<section class="sec sec--off"><div class="sechd"><p class="lbl">Platser</p><h2>Här åker vi</h2></div><div class="g g--places">{cells}</div></section>'
    body += cta()
    ld = [{"@context": "https://schema.org", "@type": "Service", "name": s["title"], "serviceType": s["title"],
           "description": s["meta_description"], "provider": {"@id": SITE + "/#org"},
           "areaServed": {"@type": "City", "name": "Uppsala"}}]
    write(slug, s["title"], s["meta_description"], body, ld, trail, og=s["hero"])


def build_girls():
    g = C["girls"]
    trail = [("Start", ""), (g["title"], "tjejer")]
    body = pagehead(trail, "Föreningen", g["title"], g["lead"])
    body += f'<section class="sec"><div class="g g--one"><div class="cell cell--wide rv">{duo(g["image"], "100vw", lazy=False)}</div></div></section>'
    body += sections_html(g["sections"])
    body += cta("Vill du vara med och bygga satsningen", "Hör av dig som ledare, förebild eller åkare.", "kontakt", "Kontakta oss")
    write("tjejer", g["title"], g["meta_description"], body, trail=trail, og=g["image"])


def place_cell(p, lazy=True):
    vis = duo(p["image"], "(min-width:900px) 33vw, 100vw", lazy) if p["image"] else '<div class="noimg" aria-hidden="true"><span>KAP</span></div>'
    return f"""<a class="cell cell--placecard inv rv" href="{u('platser/' + p['slug'])}">{vis}<div class="sport__b"><p class="lbl">{e(p['address'])}</p><h2 class="h3">{e(p['title'])}</h2><p>{e(p['short'])}</p></div></a>"""


def build_places():
    trail = [("Start", ""), ("Platser", "platser")]
    body = pagehead(trail, "Platser", "Platser", "Skateboard på Allis Uppsala, KAP-rampen och Kapellgärdet. Snowboard och freeski i Sunnerstabacken.")
    body += band()
    body += f'<section class="sec"><div class="g g--gal3">{"".join(place_cell(p) for p in C["places"])}</div></section>'
    body += cta()
    write("platser", "Platser", "Här åker Uppsala Crew IF: Sunnerstabacken, Allis Uppsala och KAP-rampen vid Kapellgärdet i Uppsala.", body, trail=trail)
    for p in C["places"]:
        slug = "platser/" + p["slug"]
        t = trail + [(p["title"], slug)]
        b = pagehead(t, "Plats", p["title"], p["short"], data([("Adress", p["address"])]))
        if p["image"]:
            b += f'<section class="sec"><div class="g g--one"><div class="cell cell--wide rv">{duo(p["image"], "100vw", lazy=False)}</div></div></section>'
        ps = "".join(f"<p>{e(x)}</p>" for x in p["body"])
        b += f'<section class="sec sec--off"><div class="g g--txt"><div class="cell cell--num rv"><span class="num">01</span></div><div class="cell cell--txt rv"><h2>Om platsen</h2>{ps}</div></div></section>'
        others = "".join(place_cell(o) for o in C["places"] if o is not p)
        b += f'<section class="sec"><div class="sechd"><p class="lbl">Fler platser</p><h2>Andra platser</h2></div><div class="g g--two">{others}</div></section>'
        b += cta()
        ld = [{"@context": "https://schema.org", "@type": "SportsActivityLocation", "name": p["title"],
               "description": p["short"], "address": {"@type": "PostalAddress", "streetAddress": p["address"], "addressLocality": "Uppsala", "addressCountry": "SE"},
               "url": f"{SITE}/{slug}/"}]
        desc = f"{p['title']}, {p['address']}. {p['short']}"
        write(slug, p["title"], desc[:158], b, ld, t, og=p["image"] or "snowboard-hopp")


def build_comps():
    c = C["competitions"]
    trail = [("Start", ""), ("Tävlingar", "tavlingar")]
    body = pagehead(trail, "Föreningen", "Tävlingar", c["lead"])
    for k, it in enumerate(c["items"]):
        off = " sec--off" if k % 2 else ""
        body += f"""<section class="sec{off}"><div class="g g--split">
 <div class="cell cell--img rv">{duo(it['image'], '(min-width:900px) 50vw, 100vw')}</div>
 <div class="cell cell--txt rv"><p class="lbl">{e(it['sport'])} / {e(it['place'])}</p><h2>{e(it['title'])}</h2><p>{e(it['text'])}</p><p class="lbl">Klasser</p><ul class="chips">{''.join(f'<li>{e(x)}</li>' for x in it['classes'])}</ul></div>
</div></section>"""
    body += f'<section class="sec"><div class="g g--one"><div class="cell cell--dark rv"><p class="lbl">Datum</p><h2>Kommande tävlingar</h2><p>Datum publiceras på Instagram. <a class="link link--inv" href="{ORG["instagram"]}" rel="noopener">Följ {ORG["instagram_handle"]}</a></p></div></div></section>'
    write("tavlingar", "Tävlingar", c["meta_description"], body, trail=trail, og="skate-luft-inne")


def build_gallery():
    trail = [("Start", ""), ("Galleri", "galleri")]
    body = pagehead(trail, "Föreningen", "Galleri", "Bilder från Sunnerstabacken, Allis Uppsala, skateskolan och tävlingarna. Håll muspekaren över en bild för att se den i färg.")
    figs = ""
    for g in C["gallery"]:
        figs += f'<figure class="cell cell--fig rv"><div class="duo">{img(g["image"], "(min-width:900px) 33vw, 50vw")}</div><figcaption class="mono">{e(g["caption"])}</figcaption></figure>'
    body += f'<section class="sec"><div class="g g--gal3">{figs}</div></section>'
    write("galleri", "Galleri", "Bilder från Uppsala Crew IF: snowboard och freeski i Sunnerstabacken, skateboard på Allis och KAP-rampen, skateskolan och tävlingar.", body, trail=trail)


def build_engage():
    en = C["engage"]
    trail = [("Start", ""), ("Engagera dig", "engagera-dig")]
    body = pagehead(trail, "Föreningen", "Engagera dig", en["lead"])
    cells = "".join(f'<div class="cell cell--role inv rv"><span class="num">{k + 1:02d}</span><h2 class="h3">{e(r["title"])}</h2><p>{e(r["text"])}</p></div>' for k, r in enumerate(en["roles"]))
    body += f'<section class="sec"><div class="g g--two">{cells}</div></section>'
    body += cta("Hör av dig", "Berätta vad du vill göra så hittar vi en uppgift som passar.", "kontakt", "Kontakta oss")
    write("engagera-dig", "Engagera dig", en["meta_description"], body, trail=trail, og="instruktorer")


def build_partners():
    p = C["partners"]
    trail = [("Start", ""), ("Partners och förbund", "partners")]
    body = pagehead(trail, "Föreningen", "Partners och förbund", p["lead"])
    fed = "".join(f'<a class="cell cell--fed inv rv" href="{f["url"]}" rel="noopener"><span>{e(f["name"])}</span><span class="arrow" aria-hidden="true">↗</span></a>' for f in p["federations"])
    sp = "".join(f'<div class="cell cell--sp rv"><span>{e(s)}</span></div>' for s in p["sponsors"])
    body += f'<section class="sec"><div class="sechd"><p class="lbl">Förbund och samarbeten</p><h2>Ansluten till</h2></div><div class="g g--fed">{fed}</div></section>'
    body += f'<section class="sec sec--off"><div class="sechd"><p class="lbl">Sponsorer</p><h2>Sponsorer</h2><p>{e(p["sponsors_note"])}</p></div><div class="g g--sp">{sp}</div></section>'
    body += cta("Stötta åkningen i Uppsala", C["engage"]["roles"][3]["text"], "kontakt", "Kontakta oss")
    write("partners", "Partners och förbund", p["meta_description"] + " Förbund, samarbeten och sponsorer av Uppsala Rail Jam.", body, trail=trail)


def build_about():
    a = C["about"]
    trail = [("Start", ""), ("Om föreningen", "om-foreningen")]
    body = pagehead(trail, "Föreningen", "Om föreningen", a["lead"], data([(f["label"], f["value"]) for f in C["facts"]]))
    tl = "".join(f'<div class="cell cell--year inv rv"><span class="year">{e(t["year"])}</span><p>{e(t["text"])}</p></div>' for t in a["timeline"])
    body += f'<section class="sec"><div class="sechd"><p class="lbl">Historik</p><h2>Från 2022 och framåt</h2></div><div class="g g--tl">{tl}</div></section>'
    body += f"""<section class="sec sec--off"><div class="g g--split">
 <div class="cell cell--blue rv"><p class="lbl">Vision</p><h2>Vision</h2><p class="big">{e(a['vision'])}</p></div>
 <div class="cell cell--txt rv"><p class="lbl">Organisation</p><h2>Organisation</h2><p>{e(a['org_text'])}</p><p class="mono">Org.nr {ORG['orgnr']}<br>{ORG['street']}, {ORG['zip']} {ORG['city']}</p></div>
</div></section>
<section class="sec"><div class="g g--one"><div class="cell cell--wide rv">{duo('graffiti', '100vw', alt=MAN['graffiti']['alt'])}</div></div></section>"""
    body += cta()
    write("om-foreningen", "Om föreningen", a["meta_description"], body, trail=trail, og="graffiti")


def build_join():
    m = C["membership"]
    trail = [("Start", ""), ("Bli medlem", "bli-medlem")]
    body = pagehead(trail, "Medlemskap", "Bli medlem", m["price_note"], f'<p class="lbl">Avgift</p><p class="fact">{e(m["price"])}</p>')
    ben = "".join(f'<div class="cell cell--ben inv rv"><span class="num">{k + 1:02d}</span><p>{e(b)}</p></div>' for k, b in enumerate(m["benefits"]))
    steps = "".join(f'<li class="cell rv"><span class="lbl">Steg {k + 1}</span><p>{e(s)}</p></li>' for k, s in enumerate(m["steps"]))
    body += f'<section class="sec"><div class="sechd"><p class="lbl">Det här ingår</p><h2>Som medlem</h2></div><div class="g g--two">{ben}</div></section>'
    body += f'<section class="sec sec--off"><div class="sechd"><p class="lbl">Så går det till</p><h2>Tre steg</h2></div><ol class="g g--steps">{steps}</ol></section>'
    body += f'<section class="sec" id="ansok"><div class="g g--one"><div class="cell cell--form rv"><h2>Medlemsansökan</h2>{form("join")}</div></div></section>'
    write("bli-medlem", "Bli medlem", m["meta_description"], body, trail=trail, og="instruktorer")


def build_faq():
    trail = [("Start", ""), ("Vanliga frågor", "vanliga-fragor")]
    body = pagehead(trail, "Frågor och svar", "Vanliga frågor", "Om medlemskap, försäkring, utrustning och var vi tränar.")
    qs = "".join(f'<details class="cell qa rv"><summary><span class="num">{k + 1:02d}</span><h2 class="h3">{e(q["q"])}</h2><span class="pm" aria-hidden="true"></span></summary><p>{e(q["a"])}</p></details>' for k, q in enumerate(C["faq"]))
    body += f'<section class="sec"><div class="g g--one">{qs}</div></section>'
    body += cta("Hittade du inte svaret", "Mejla oss eller använd kontaktformuläret.", "kontakt", "Kontakta oss")
    ld = [{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}} for q in C["faq"]]}]
    write("vanliga-fragor", "Vanliga frågor", "Svar på vanliga frågor om Uppsala Crew IF: medlemsavgift, försäkring, utrustning, skateskolan och var vi tränar.", body, ld, trail)


def build_contact():
    trail = [("Start", ""), ("Kontakt", "kontakt")]
    body = pagehead(trail, "Kontakt", "Kontakt", "Frågor om träning, medlemskap, tävlingar eller samarbete. Mejla, ring eller skriv i formuläret.")
    cells = [("E-post", f'<a href="mailto:{ORG["email"]}">{ORG["email"]}</a><br><a href="mailto:{ORG["email_alt"]}">{ORG["email_alt"]}</a>'),
             ("Telefon", f'<a href="tel:{ORG["phone_href"]}">{ORG["phone"]}</a>'),
             ("Postadress", f'{ORG["street"]}<br>{ORG["zip"]} {ORG["city"]}'),
             ("Instagram", f'<a href="{ORG["instagram"]}" rel="noopener">{ORG["instagram_handle"]}</a>'),
             ("Facebook", f'<a href="{ORG["facebook"]}" rel="noopener">Uppsala Crew IF</a>'),
             ("Org.nr", ORG["orgnr"])]
    cc = "".join(f'<div class="cell cell--ct rv"><p class="lbl">{k}</p><p class="ct">{v}</p></div>' for k, v in cells)
    body += f'<section class="sec"><div class="g g--ct">{cc}</div></section>'
    body += f'<section class="sec sec--off"><div class="g g--one"><div class="cell cell--form rv"><h2>Skriv till oss</h2>{form("contact")}</div></div></section>'
    ld = [{"@context": "https://schema.org", "@type": "ContactPage", "name": "Kontakt", "about": {"@id": SITE + "/#org"}}]
    write("kontakt", "Kontakt", f"Kontakta Uppsala Crew IF på {ORG['email']} eller {ORG['phone']}. Postadress {ORG['street']}, {ORG['zip']} Uppsala.", body, ld, trail)


def build_privacy():
    trail = [("Start", ""), ("Integritetspolicy", "integritetspolicy")]
    body = pagehead(trail, "Integritet", "Integritetspolicy", "Så hanterar Uppsala Crew IF personuppgifter enligt dataskyddsförordningen.")
    body += sections_html([{"h": x["h"], "p": [x["p"]]} for x in C["privacy"]])
    write("integritetspolicy", "Integritetspolicy", "Integritetspolicy för Uppsala Crew IF: vilka personuppgifter vi behandlar, varför, hur länge och vilka rättigheter du har.", body, trail=trail)


def build_404():
    body = f"""<section class="ph"><div class="g g--ph">
 <div class="cell cell--h1 rv"><p class="lbl">Fel 404</p><h1>Sidan finns inte</h1></div>
 <div class="cell cell--lead rv"><p class="lead">Länken kan vara gammal eller felstavad.</p><div class="btns"><a class="btn" href="{B}/">Till startsidan</a><a class="btn btn--line" href="{u('kontakt')}">Kontakt</a></div></div>
</div></section>"""
    write("404", "Sidan finns inte", "Sidan kunde inte hittas på Uppsala Crew IF:s webbplats.", body, path="404.html")


CSS = r"""
:root{--paper:#F2F2F0;--ink:#0D0D0D;--blue:#3D5AFE;--mute:#4a4a48;--line:1px solid var(--ink);
--fh:"Space Grotesk",system-ui,sans-serif;--fm:"IBM Plex Mono",ui-monospace,monospace;--gut:16px;--max:1440px}
*,*::before,*::after{box-sizing:border-box;border-radius:0}
html{-webkit-text-size-adjust:100%;scroll-padding-top:80px}
body{margin:0;background:var(--paper);color:var(--ink);font:400 1.0625rem/1.6 var(--fh);overflow-x:hidden}
img{display:block;max-width:100%;height:auto}
a{color:inherit}
h1,h2,h3,.h3{font-family:var(--fh);font-weight:700;line-height:1.02;letter-spacing:-.025em;margin:0 0 .6em}
h1{font-size:clamp(2.5rem,8.5vw,7.4rem);text-transform:uppercase;letter-spacing:-.04em;line-height:.92;overflow-wrap:anywhere;hyphens:auto}
h2{font-size:clamp(1.75rem,4vw,3.25rem)}
h3,.h3{font-size:clamp(1.35rem,2.2vw,1.9rem)}
p{margin:0 0 1em;max-width:68ch}
.mono,.lbl,.data,.chips,.crumbs,.btn,.nav__a,.hd__cta,.hd__btn,figcaption{font-family:var(--fm)}
.lbl{font-size:.75rem;font-weight:500;text-transform:uppercase;letter-spacing:.08em;margin:0 0 1rem}
.lead{font-size:clamp(1.15rem,1.7vw,1.4rem);line-height:1.45}
.vh{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.skip{position:absolute;left:-999px;top:0;background:var(--blue);color:#fff;padding:12px 16px;z-index:99}
.skip:focus{left:0}
:focus-visible{outline:3px solid var(--blue);outline-offset:2px}
.cell--blue :focus-visible,.cell--dark :focus-visible{outline-color:var(--paper)}

/* header */
.hd{position:sticky;top:0;z-index:50;display:grid;grid-template-columns:auto 1fr auto;background:var(--paper);border-bottom:var(--line)}
.hd__logo{display:flex;align-items:center;gap:10px;padding:8px var(--gut);text-decoration:none;font-weight:700;line-height:1;font-size:.95rem;text-transform:uppercase;border-right:var(--line);min-height:60px}
.hd__logo img{width:40px;height:40px}
.nav{display:none}
.hd__cta{display:none}
.hd__btn{grid-column:3;appearance:none;border:0;border-left:var(--line);background:var(--ink);color:var(--paper);font-size:.85rem;text-transform:uppercase;letter-spacing:.08em;padding:0 22px;min-height:60px;cursor:pointer}
.hd__btn[aria-expanded=true]{background:var(--blue)}
.menu{position:fixed;inset:61px 0 0 0;z-index:49;background:var(--paper);overflow:auto;border-top:var(--line)}
.menu ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:1fr 1fr}
.menu li{border-bottom:var(--line)}
.menu li:nth-child(odd){border-right:var(--line)}
.menu a{display:flex;align-items:center;min-height:64px;padding:12px var(--gut);text-decoration:none;font-weight:700;font-size:1.05rem}
.menu a:hover,.menu a:focus-visible{background:var(--ink);color:var(--paper)}
@media(min-width:1100px){
 .hd{grid-template-columns:auto 1fr auto}
 .hd__btn,.menu{display:none!important}
 .nav{display:block}
 .nav ul{display:flex;list-style:none;margin:0;padding:0;height:100%}
 .nav li{flex:1;border-right:var(--line)}
 .nav__a{display:flex;align-items:center;justify-content:center;height:100%;padding:0 12px;font-size:.8rem;text-transform:uppercase;letter-spacing:.05em;text-decoration:none;transition:background .15s,color .15s}
 .nav__a:hover,.nav__a[aria-current]{background:var(--ink);color:var(--paper)}
 .hd__cta{display:flex;align-items:center;gap:10px;padding:0 28px;background:var(--blue);color:#fff;text-decoration:none;font-size:.85rem;text-transform:uppercase;letter-spacing:.06em}
 .hd__cta:hover{background:var(--ink)}
}

/* grid system */
main{max-width:var(--max);margin:0 auto;border-left:var(--line);border-right:var(--line)}
.g{display:grid;grid-template-columns:1fr;gap:1px;background:var(--ink);border-top:var(--line);border-bottom:var(--line)}
.cell{position:relative;background:var(--paper);padding:24px var(--gut);min-width:0;text-decoration:none;color:inherit;overflow:hidden}
.sec{margin:56px 0 0}
.sechd{padding:0 var(--gut) 24px}
.sechd p:not(.lbl){max-width:60ch}
.more{padding:16px var(--gut) 0;margin:0}
@media(min-width:900px){
 :root{--gut:32px}
 .g{grid-template-columns:repeat(12,1fr)}
 .sec{margin-top:96px}
 .sec--off{margin-left:calc(100%/12);border-left:var(--line)}
 .sec--off>.g{border-left:0}
 .cell{padding:36px var(--gut)}
}

/* fill animation: bakgrund sveper in från vänster */
.cell::after{content:"";position:absolute;inset:0;background:var(--ink);transform:scaleX(0);transform-origin:left;pointer-events:none;z-index:3}
.js .rv{opacity:1}
.js .rv>*{transition:opacity .35s ease calc(var(--d,0ms) + 260ms)}
.js .rv:not(.in)>*{opacity:0}
.js .rv.in::after{animation:sweep .7s cubic-bezier(.7,0,.2,1) var(--d,0ms) both}
@keyframes sweep{0%{transform:scaleX(0);transform-origin:left}49.9%{transform:scaleX(1);transform-origin:left}50%{transform:scaleX(1);transform-origin:right}100%{transform:scaleX(0);transform-origin:right}}
.cell--blue::after{background:var(--paper)}
.cell--dark::after{background:var(--blue)}

/* invert on hover */
.inv{transition:background-color .18s,color .18s}
.inv:hover,.inv:focus-visible{background:var(--ink);color:var(--paper)}
.inv:hover .lbl,.inv:hover .data dt{color:var(--paper)}
.inv:hover .chips li{border-color:var(--paper)}

/* duotone */
.duo{margin:0;position:relative;background:var(--blue);overflow:hidden}
.duo img{width:100%;height:100%;object-fit:cover;filter:grayscale(1) contrast(1.25) brightness(1.05);mix-blend-mode:multiply;transition:filter .45s,mix-blend-mode 0s .1s,transform .6s}
.cell:hover .duo img,.duo:hover img,a:focus-visible .duo img{filter:none;mix-blend-mode:normal;transform:scale(1.02)}

/* hero */
.g--hero .cell--h1{padding-top:40px}
.g--hero .cell--heroimg{padding:0}
.g--hero .cell--heroimg .duo{aspect-ratio:16/8}
@media(min-width:900px){
 .g--hero .cell--h1{grid-column:1/9;padding-top:64px;padding-bottom:48px}
 .g--hero .cell--lead{grid-column:9/13;display:flex;flex-direction:column;justify-content:flex-end}
 .g--hero .cell--heroimg{grid-column:1/13}
 .g--hero .cell--heroimg .duo{aspect-ratio:2560/887}
}
.btns{display:flex;flex-wrap:wrap;gap:1px;margin-top:8px}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:12px 22px;background:var(--ink);color:var(--paper);border:1px solid var(--ink);text-decoration:none;font-size:.85rem;text-transform:uppercase;letter-spacing:.06em;cursor:pointer;transition:background .15s,color .15s}
.btn:hover{background:var(--blue);border-color:var(--blue);color:#fff}
.btn--line{background:transparent;color:var(--ink)}
.btn--line:hover{background:var(--ink);color:var(--paper);border-color:var(--ink)}

/* band */
.band{border-top:var(--line);border-bottom:var(--line);background:var(--ink);color:var(--paper);overflow:hidden;margin-top:-1px}
.band__track{display:flex;width:max-content;animation:band 38s linear infinite}
.band__track>div{display:flex;flex-shrink:0}
.band span{font:700 clamp(1.4rem,3vw,2.4rem)/1 var(--fh);text-transform:uppercase;padding:18px 20px;white-space:nowrap}
.band .sep{color:var(--blue);padding:18px 0}
@keyframes band{to{transform:translateX(-50%)}}
.band:hover .band__track{animation-play-state:paused}

/* facts */
.cell--fact .fact,.fact{font:700 clamp(1.4rem,2.4vw,2rem)/1.1 var(--fh);margin:0;letter-spacing:-.02em}
@media(min-width:600px) and (max-width:899px){.g--facts{grid-template-columns:1fr 1fr}}
@media(min-width:900px){.g--facts .cell{grid-column:span 3;min-height:200px;display:flex;flex-direction:column;justify-content:space-between}}

/* sports */
.cell--sport,.cell--placecard{padding:0;display:flex;flex-direction:column}
.cell--sport .duo,.cell--placecard .duo{aspect-ratio:16/9}
.sport__b{padding:24px var(--gut) 28px}
.sport__b p:not(.lbl){margin-bottom:1rem}
.data{margin:0;display:grid;gap:0;border-top:var(--line)}
.data div{display:grid;grid-template-columns:7.5em 1fr;gap:12px;padding:10px 0;border-bottom:var(--line);font-size:.85rem}
.inv:hover .data,.inv:hover .data div{border-color:var(--paper)}
.data dt{text-transform:uppercase;letter-spacing:.06em;color:var(--mute)}
.data dd{margin:0}
@media(min-width:900px){
 .g--sports .s7{grid-column:span 7}.g--sports .s5{grid-column:span 5}
 .g--sports .s12{grid-column:span 12;display:grid;grid-template-columns:7fr 5fr}
 .g--sports .s12 .duo{aspect-ratio:auto;height:100%}
}

/* misc cells */
.cell--dark{background:var(--ink);color:var(--paper)}
.cell--dark .lbl{color:var(--paper)}
.cell--blue{background:var(--blue);color:#fff}
.cell--img{padding:0}.cell--img .duo{height:100%;min-height:260px}
.cell--wide{padding:0}.cell--wide .duo{aspect-ratio:16/7;max-height:620px}
@media(max-width:899px){.cell--wide .duo{aspect-ratio:4/3}}
@media(min-width:900px){
 .g--split>.cell{grid-column:span 6}
 .g--two>.cell{grid-column:span 6}
 .g--one>.cell{grid-column:1/-1}
 .g--gal4>.cell{grid-column:span 3}
 .g--gal3>*{grid-column:span 4}
 .g--places>.cell{grid-column:span 4}
 .g--fed>.cell{grid-column:span 4}
 .g--sp>.cell{grid-column:span 2}
 .g--ct>.cell{grid-column:span 4}
 .g--tl>.cell{grid-column:span 3}
 .g--steps>.cell{grid-column:span 4}
 .g--cta .cell--blue{grid-column:span 8}.g--cta .cell--go{grid-column:span 4}
}
@media(min-width:600px) and (max-width:899px){.g--gal4,.g--gal3,.g--sp,.g--ct,.g--tl,.g--fed{grid-template-columns:1fr 1fr}}
@media(max-width:899px){.g--gal4,.g--sp{grid-template-columns:1fr 1fr}}
.cell--gal{padding:0}.cell--gal .duo{aspect-ratio:1}
.cell--comp{min-height:220px;display:flex;flex-direction:column;justify-content:space-between}
.chips{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:6px}
.chips li{border:var(--line);padding:6px 10px;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em}
.cell--dark .chips li{border-color:var(--paper)}

/* text sections */
.cell--num{display:flex;align-items:flex-start}
.num{font:500 .85rem/1 var(--fm);display:inline-block;border:var(--line);padding:8px 10px;letter-spacing:.06em}
.inv:hover .num{border-color:var(--paper)}
@media(min-width:900px){
 .g--txt .cell--num{grid-column:span 3}
 .g--txt .cell--txt{grid-column:span 9;padding-right:calc(100%/12)}
}
.cell--txt h2{max-width:20ch}

/* page head */
.ph .crumbs{padding:20px var(--gut)}
.crumbs ol{list-style:none;display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;font-size:.78rem;text-transform:uppercase;letter-spacing:.06em}
.crumbs li+li::before{content:"/";margin-right:6px;color:var(--blue)}
.crumbs a{display:inline-block;padding:6px 0;min-height:24px}
@media(min-width:900px){
 .g--ph .cell--h1{grid-column:1/-1;padding-top:56px}
 .g--ph .cell--lead{grid-column:1/8}
 .g--ph .cell--side{grid-column:8/13}
 .g--ph .cell--lead:last-child{grid-column:1/-1}
}
.g--ph h1{font-size:clamp(2.3rem,7.5vw,6.4rem)}

/* cta */
.cell--go{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;min-height:160px;font:700 1.4rem/1.1 var(--fh);background:var(--paper)}
.arrow{font-size:2.4rem;line-height:1;transition:transform .2s}
.cell--go:hover .arrow,.cell--fed:hover .arrow{transform:translateX(6px)}
.link{font-family:var(--fm);font-size:.85rem;text-transform:uppercase;letter-spacing:.06em;text-decoration:underline;text-underline-offset:4px;display:inline-block;padding:10px 0}
.link--inv{color:var(--paper)}
.noimg{aspect-ratio:16/9;background:var(--blue);color:var(--paper);display:flex;align-items:flex-end;padding:var(--gut)}
.noimg span{font:700 clamp(4rem,9vw,7rem)/.8 var(--fh);letter-spacing:-.05em}
.cell--placecard:hover .noimg{background:var(--paper);color:var(--ink)}

/* roles / benefits / timeline / partners */
.cell--role .num,.cell--ben .num{margin-bottom:24px}
.cell--year .year{display:block;font:700 clamp(2.6rem,5vw,4rem)/1 var(--fh);letter-spacing:-.04em;color:var(--blue);margin-bottom:16px}
.cell--year:hover .year{color:var(--paper)}
.cell--fed{display:flex;justify-content:space-between;align-items:center;gap:12px;min-height:110px;font-weight:700;font-size:1.15rem}
.cell--sp{display:flex;align-items:center;justify-content:center;min-height:120px;font:500 1rem var(--fm);text-transform:uppercase;text-align:center}
.big{font-size:clamp(1.2rem,2vw,1.6rem);line-height:1.35}
ol.g{list-style:none;margin:0;padding:0}
.g--steps .cell p{margin:0}
.ct{font:500 1rem/1.6 var(--fm);margin:0;overflow-wrap:anywhere}
.ct a{display:inline-block;padding:4px 0}

/* figures */
.cell--fig{margin:0;padding:0}
.cell--fig .duo{aspect-ratio:4/3}
.cell--fig figcaption{padding:12px var(--gut);font-size:.8rem;text-transform:uppercase;letter-spacing:.05em;border-top:var(--line)}

/* faq */
.qa{padding:0}
.qa summary{display:grid;grid-template-columns:auto 1fr auto;gap:16px;align-items:center;padding:20px var(--gut);cursor:pointer;list-style:none;min-height:64px;transition:background .15s,color .15s}
.qa summary::-webkit-details-marker{display:none}
.qa summary:hover{background:var(--ink);color:var(--paper)}
.qa summary:hover .num{border-color:var(--paper)}
.qa h2{margin:0;font-size:clamp(1.1rem,1.8vw,1.5rem)}
.qa .pm{width:20px;height:20px;position:relative}
.qa .pm::before,.qa .pm::after{content:"";position:absolute;left:0;right:0;top:9px;height:2px;background:currentColor}
.qa .pm::after{transform:rotate(90deg);transition:transform .2s}
.qa[open] .pm::after{transform:rotate(0)}
.qa>p{padding:0 var(--gut) 24px;margin:0 0 0 calc(var(--gut) + 3rem)}
@media(max-width:600px){.qa>p{margin-left:0}}

/* form */
.form{display:grid;gap:16px;margin-top:8px}
@media(min-width:700px){.form{grid-template-columns:1fr 1fr}.fld--w{grid-column:1/-1}}
.fld{display:flex;flex-direction:column;gap:6px}
.fld span{font:500 .75rem var(--fm);text-transform:uppercase;letter-spacing:.08em}
input,select,textarea{font:inherit;font-size:1rem;color:var(--ink);background:var(--paper);border:var(--line);padding:12px 14px;min-height:48px;width:100%}
textarea{resize:vertical}
input:focus,select:focus,textarea:focus{outline:3px solid var(--blue);outline-offset:0}
.chk{display:flex;gap:12px;align-items:flex-start;font-size:.95rem;min-height:44px}
.chk input{width:22px;height:22px;min-height:0;margin:2px 0 0;accent-color:var(--blue);flex-shrink:0}
.form__end{display:flex;flex-wrap:wrap;gap:16px;align-items:center}
.form__note{font-size:.78rem;margin:0}
.form-status{margin:0;font-size:.85rem}
.cell--form h2{margin-bottom:.4em}

/* footer */
.ft{max-width:var(--max);margin:96px auto 0;border:var(--line);border-bottom:0;background:var(--ink)}
.ft__grid{display:grid;gap:1px;background:var(--paper)}
.ft .cell{background:var(--ink);color:var(--paper)}
.ft .cell::after{display:none}
.ft__id img{width:72px;height:72px;margin-bottom:16px}
.ft__name{font-weight:700;font-size:1.2rem}
.ft__list,.ft__links{list-style:none;margin:0;padding:0}
.ft__list li{font-size:.85rem;padding:4px 0}
.ft__list a,.ft__links a{display:inline-block;padding:6px 0;min-height:32px}
.ft__links{columns:2;column-gap:16px}
.ft__links a{font-size:.95rem;text-decoration:none}
.ft__links a:hover,.ft__list a:hover{color:var(--blue);background:var(--paper)}
.ft__bar{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px;margin:0;padding:16px var(--gut);color:var(--paper);font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;border-top:1px solid var(--paper)}
@media(min-width:900px){.ft__grid{grid-template-columns:3fr 3fr 3fr 4fr}}
.ft .lbl{color:var(--paper);opacity:.85}

@media (prefers-reduced-motion:reduce){
 *,*::before,*::after{animation:none!important;transition:none!important}
 .js .rv:not(.in)>*{opacity:1}
 .cell::after{display:none}
 .band__track{width:auto;flex-wrap:wrap}
 .band__track>div:last-child{display:none}
 .band__track>div{flex-wrap:wrap}
}
"""

JS = r"""
document.documentElement.classList.add('js');
(function(){
 var btn=document.querySelector('.hd__btn'),menu=document.getElementById('meny');
 function close(f){menu.hidden=true;btn.setAttribute('aria-expanded','false');document.body.style.overflow='';if(f)btn.focus();}
 if(btn){btn.addEventListener('click',function(){var o=btn.getAttribute('aria-expanded')==='true';if(o){close();}else{menu.hidden=false;btn.setAttribute('aria-expanded','true');document.body.style.overflow='hidden';var a=menu.querySelector('a');if(a)a.focus();}});
 document.addEventListener('keydown',function(e){if(e.key==='Escape'&&btn.getAttribute('aria-expanded')==='true')close(true);});}
 var rm=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
 var els=[].slice.call(document.querySelectorAll('.rv'));
 if(rm||!('IntersectionObserver' in window)){els.forEach(function(el){el.classList.add('in')});}
 else{var io=new IntersectionObserver(function(en){var n=0;en.forEach(function(x){if(x.isIntersecting){x.target.style.setProperty('--d',(n++*90)+'ms');x.target.classList.add('in');io.unobserve(x.target);}});},{rootMargin:'0px 0px -8% 0px'});
 els.forEach(function(el){io.observe(el)});}
 document.querySelectorAll('form[data-mail]').forEach(function(f){f.addEventListener('submit',function(ev){ev.preventDefault();
  if(!f.reportValidity())return;var lines=[];[].forEach.call(f.elements,function(el){if(el.name&&el.name!=='samtycke'&&el.value)lines.push(el.name+': '+el.value);});
  lines.push('','Jag godkänner behandling av mina uppgifter enligt integritetspolicyn.');
  location.href='mailto:'+f.dataset.mail+'?subject='+encodeURIComponent(f.dataset.subject)+'&body='+encodeURIComponent(lines.join('\n'));
  var s=f.querySelector('.form-status');if(s)s.textContent='Ditt e-postprogram öppnas med ett förifyllt mejl. Skicka det för att slutföra.';});});
})();
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    (OUT / "assets/site.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (OUT / "assets/site.js").write_text(JS.strip() + "\n", encoding="utf-8")
    build_home()
    for s in SPORTS:
        build_sport(s)
    build_girls(); build_places(); build_comps(); build_gallery(); build_engage(); build_partners()
    build_about(); build_join(); build_faq(); build_contact(); build_privacy(); build_404()
    missing = [p["slug"] for p in C["pages"] if not (OUT / (p["slug"] + "/index.html" if p["slug"] else "index.html")).exists()]
    assert not missing, missing
    print("v05 klar:", sum(1 for _ in OUT.rglob("*.html")), "sidor")


if __name__ == "__main__":
    main()
