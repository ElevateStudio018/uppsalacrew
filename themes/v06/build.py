#!/usr/bin/env python3
"""v06 "Appen" – sportapp med bento-grid. Läser content/content.json och skriver docs/v06/."""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
C = json.loads((ROOT / "content/content.json").read_text(encoding="utf-8"))
MAN = json.loads((ROOT / "docs/media/manifest.json").read_text(encoding="utf-8"))
OUT = ROOT / "docs/v06"
B = "/uppsalacrew/v06"
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
    return f'<figure class="ph-img {cls}">{img(name, sizes, lazy, alt)}</figure>'


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
NAV = [("skateboard", "Skateboard"), ("snowboard-och-freeski", "Snow"), ("skateskola", "Skateskola"),
       ("platser", "Platser"), ("tavlingar", "Tävlingar"), ("om-foreningen", "Föreningen"), ("kontakt", "Kontakt")]


def header(slug):
    def cur(s):
        top = slug.split("/")[0]
        return ' aria-current="page"' if s == slug or (s == top and slug) else ""
    links = "".join(f'<li><a class="nav__a" href="{u(s)}"{cur(s)}>{t}</a></li>' for s, t in NAV)
    all_links = "".join(f'<li><a href="{u(p["slug"])}">{e(p["title"])}</a></li>' for p in C["pages"])
    return f"""<a class="skip" href="#main">Hoppa till innehållet</a>
<header class="hd"><div class="pill">
 <a class="hd__logo" href="{B}/" aria-label="Uppsala Crew IF, startsida"><img src="{M}/logo-rund-64.png" width="64" height="64" alt=""><span>Uppsala Crew</span></a>
 <nav class="nav" aria-label="Huvudmeny"><ul>{links}</ul></nav>
 <a class="hd__cta" href="{u('bli-medlem')}">Bli medlem</a>
 <button class="hd__btn" type="button" aria-expanded="false" aria-controls="meny"><span class="bars" aria-hidden="true"></span><span>Meny</span></button>
</div></header>
<div class="menu" id="meny" hidden><nav aria-label="Alla sidor"><ul>{all_links}</ul></nav></div>
<div class="toast" id="toast" role="dialog" aria-labelledby="toast-h" hidden><img src="{M}/logo-rund-64.png" width="44" height="44" alt=""><div><p class="toast__h" id="toast-h">Bli medlem för 50–100 kr per år</p><p class="toast__t">Försäkring på aktiviteterna och fritt tillträde till evenemangen.</p><a class="toast__a" href="{u('bli-medlem')}">Till ansökan</a></div><button class="toast__x" type="button" aria-label="Stäng påminnelsen">×</button></div>"""


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
 <p class="ft__bar mono"><span>© {ORG['name']}</span><span>Förhandsvisning v06 / Appen</span></p>
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
<meta name="theme-color" content="#EEF0F2">
<link rel="icon" href="{M}/logo-rund-64.png" type="image/png">
<link rel="apple-touch-icon" href="{M}/logo-rund-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;800&display=swap">
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
def sport_card(s, k=0):
    chips = f'<ul class="chips"><li><b>Var</b> {e(s["where"])}</li><li><b>När</b> {e(s["when"])}</li></ul>'
    return f"""<a class="cell card rv" href="{u(s['slug'])}">{duo(s['hero'], '(min-width:900px) 40vw, 100vw')}<div class="card__b"><h3>{e(s['title'])}</h3><p>{e(s['short'])}</p>{chips}</div></a>"""


def build_home():
    i = C["intro"]
    sk, sn, ss = SPORTS["skateboard"], SPORTS["snowboard-och-freeski"], SPORTS["skateskola"]
    facts = "".join(f'<div class="cell stat rv{" stat--dark" if k % 3 == 1 else ""}"><p class="lbl">{e(f["label"])}</p><p class="fact">{e(f["value"])}</p></div>' for k, f in enumerate(C["facts"]))
    def panel(pid, s, extra, hidden):
        h = " hidden" if hidden else ""
        return f"""<div class="seg__panel" id="p-{pid}" role="tabpanel" aria-labelledby="t-{pid}"{h}><div class="g g--seg">{sport_card(s)}{extra}</div></div>"""
    sk_extra = f'{sport_card(ss)}<a class="cell stat stat--dark rv" href="{u("platser/kap-rampen")}"><p class="lbl">Skateskola</p><p class="fact">Måndagar<br>18.00–19.00</p><p class="mono">KAP-rampen, Ulleråkersvägen 22</p></a>'
    sn_extra = f'<a class="cell stat stat--coral rv" href="{u("platser/sunnerstabacken")}"><p class="lbl">Hemmabacke</p><p class="fact">Sunnerstabacken</p><p class="mono">Låna utrustning och få coachning</p></a><div class="cell tile-img rv">{duo("instruktorer", "(min-width:900px) 30vw, 100vw")}</div>'
    comps = "".join(f'<a class="cell comp rv{" stat--dark" if k else ""}" href="{u("tavlingar")}"><p class="lbl">{e(c["sport"])} · {e(c["place"])}</p><h3>{e(c["title"])}</h3><ul class="chips">{"".join(f"<li>{e(x)}</li>" for x in c["classes"])}</ul></a>' for k, c in enumerate(C["competitions"]["items"]))
    body = f"""<section class="hero"><div class="g g--hero">
 <div class="cell hero__t rv"><p class="lbl">Uppsala Crew IF · Sedan {ORG['founded']}</p><h1>{e(i['headline'])}</h1><p class="lead">{e(i['lead'])}</p><div class="btns"><a class="btn" href="{u('bli-medlem')}">Bli medlem</a><a class="btn btn--line" href="{u('skateskola')}">Skateskolan</a></div></div>
 <div class="cell hero__img rv">{duo('snowboard-hopp', '(min-width:900px) 50vw, 100vw', lazy=False)}</div>
</div></section>
<section class="sec"><h2 class="vh">Fakta om föreningen</h2><div class="g g--facts">{facts}</div></section>
<section class="sec"><div class="sechd sechd--row"><div><p class="lbl">Sporter</p><h2>Välj din säsong</h2></div>
 <div class="seg" role="tablist" aria-label="Välj sport"><button type="button" class="seg__b" role="tab" id="t-skate" aria-controls="p-skate" aria-selected="true">Skate</button><button type="button" class="seg__b" role="tab" id="t-snow" aria-controls="p-snow" aria-selected="false" tabindex="-1">Snow</button></div></div>
 {panel('skate', sk, sk_extra, False)}{panel('snow', sn, sn_extra, True)}
</section>
<section class="sec"><div class="g g--bento">
 <div class="cell tile-img rv b-a">{duo(C['girls']['image'], '(min-width:900px) 50vw, 100vw')}</div>
 <div class="cell stat stat--dark rv b-b"><p class="lbl">Tjejsatsning</p><h2 class="h3">{e(C['girls']['title'])}</h2><p>{e(C['girls']['lead'])}</p><a class="link" href="{u('tjejer')}">Läs mer</a></div>
 {comps}
 <a class="cell stat stat--coral rv b-c" href="{u('bli-medlem')}"><p class="lbl">Medlemskap</p><p class="fact">{e(C['membership']['price'])}</p><p>{e(C['membership']['price_note'])}</p><span class="link">Bli medlem</span></a>
</div></section>
<section class="sec"><div class="sechd"><p class="lbl">Galleri</p><h2>Från backen och rampen</h2></div><div class="g g--gal4">{"".join(f'<div class="cell cell--gal rv">{duo(g["image"], "(min-width:900px) 25vw, 50vw")}</div>' for g in C["gallery"][:4])}</div><p class="more"><a class="link" href="{u('galleri')}">Hela galleriet</a></p></section>"""
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
    body = pagehead(trail, "Föreningen", "Galleri", "Bilder från Sunnerstabacken, Allis Uppsala, skateskolan och tävlingarna.")
    figs = ""
    for g in C["gallery"]:
        figs += f'<figure class="cell cell--fig rv"><div class="ph-img">{img(g["image"], "(min-width:900px) 33vw, 50vw")}</div><figcaption class="mono">{e(g["caption"])}</figcaption></figure>'
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


CSS = (Path(__file__).parent / "site.css").read_text(encoding="utf-8")
JS = (Path(__file__).parent / "site.js").read_text(encoding="utf-8")


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
    print("v06 klar:", sum(1 for _ in OUT.rglob("*.html")), "sidor")


if __name__ == "__main__":
    main()
