#!/usr/bin/env python3
"""Genererar den statiska sajten för Uppsala Crew IF.  Kör: python3 build.py"""
import json, os, html
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent
OUT = ROOT / "public"
SITE = "https://www.uppsalacrew.se"
TODAY = date.today().isoformat()
BASE = os.environ.get("BASE", "")  # t.ex. /uppsalacrew för GitHub Pages-förhandsvisning

ORG = {
    "name": "Uppsala Crew IF",
    "legal": "Uppsala Crew Idrottsförening",
    "orgnr": "802540-8660",
    "founded": "2022",
    "email": "info@uppsalacrew.se",
    "email_alt": "uppsalacrew@gmail.com",
    "phone": "073-579 56 36",
    "phone_href": "+46735795636",
    "street": "Glimmervägen 6D",
    "zip": "752 41",
    "city": "Uppsala",
    "instagram": "https://www.instagram.com/uppsalacrew/",
    "facebook": "https://www.facebook.com/profile.php?id=100089833039131",
}

# Bilder: namn -> (bredd, höjd i original, tillgängliga bredder)
IMG = {
    "snowboard-hopp-sunnerstabacken": (2560, 887),
    "freeski-hopp-sunnerstabacken": (1686, 949),
    "snowboard-rail-funpark": (1080, 608),
    "kvallsaking-hopp-sunnersta": (978, 550),
    "allis-bowl": (1280, 912),
    "allis-skatehall-1": (4032, 3024),
    "allis-skatehall-2": (4032, 3024),
    "crew-instruktorer-backen": (1180, 1480),
    "skateskola-grupp": (1476, 681),
    "affisch-miniramp-madness-2023": (1284, 1269),
    "affisch-miniramp-madness-2024": (905, 1280),
    "affisch-uppsala-rail-jam-2025": (1587, 2245),
    "affisch-freeski-sweden-2024": (1080, 1920),
}


def e(s):
    return html.escape(s, quote=True)


def img(name, alt, sizes="100vw", lazy=True, cls=""):
    w, h = IMG[name]
    widths = [x for x in (480, 960, 1600, 2400) if x <= w or x == 480]
    srcset = ", ".join(f"/assets/img/{name}-{x}.webp {min(x, w) if x != 480 else 480}w" for x in widths)
    default = f"/assets/img/{name}-{widths[min(1, len(widths)-1)]}.webp"
    attrs = 'loading="lazy" decoding="async"' if lazy else 'fetchpriority="high" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<img{c} src="{default}" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" '
            f'alt="{e(alt)}" {attrs}>')


# ---------------------------------------------------------------- innehåll

ACTIVITIES = [
    {"slug": "skateboard", "title": "Skateboard", "short": "Skateskola, tävlingar och åkning för alla åldrar.",
     "where": "Allis Uppsala, KAP-rampen, Kapellgärdet", "when": "Året runt"},
    {"slug": "snowboard-och-freeski", "title": "Snowboard och freeski", "short": "Parkåkning, coachning och tävlingar i hemmabacken.",
     "where": "Sunnerstabacken", "when": "Vintersäsongen"},
    {"slug": "skateskola", "title": "Skateskola", "short": "Ledarledd träning för barn och unga på måndagar.",
     "where": "KAP-rampen, inomhus på Allis vid kyla", "when": "Måndagar 18.00–19.00"},
]

PLACES = [
    {"slug": "sunnerstabacken", "title": "Sunnerstabacken", "img": "freeski-hopp-sunnerstabacken",
     "alt": "Freeskiåkare i luften över ett hopp i Sunnerstabacken med Mälaren i bakgrunden",
     "short": "Funpark med hopp och rails. Här håller vi till under vintersäsongen.",
     "addr": "Sunnersta, Uppsala"},
    {"slug": "allis-uppsala", "title": "Allis Uppsala", "img": "allis-skatehall-1",
     "alt": "Skatehallen i Allaktivitetshuset Allis med ramper, boxar och rails",
     "short": "Inomhushall med bowl, ramper och street. Hit flyttar träningen när det blir kallt.",
     "addr": "Allaktivitetshuset Allis, Uppsala"},
    {"slug": "kap-rampen", "title": "KAP-rampen", "img": None,
     "alt": "", "short": "Miniramp utomhus vid Kapellgärdet. Skateskolans hemmaplan och platsen för Miniramp Madness.",
     "addr": "Ulleråkersvägen 22, Uppsala"},
]

EVENTS = [
    {"slug": "uppsala-rail-jam-2025", "title": "Uppsala Rail Jam 2025", "type": "Tävling", "sport": "Snowboard och freeski",
     "date": "2025-01-18", "date_h": "18 januari 2025", "time": "12.00–15.00", "place": "Sunnerstabacken, Uppsala",
     "img": "affisch-uppsala-rail-jam-2025", "poster": True,
     "alt": "Affisch för Uppsala Rail Jam 18 januari 2025 i Sunnerstabacken med sponsorernas logotyper",
     "summary": "Railtävling för snowboard och freeski i Sunnerstabacken, öppen för alla nivåer, åldrar och kön.",
     "body": """<p>Uppsala Rail Jam 2025 hölls i Sunnerstabacken. Mellan 12 och 14 åkte vi, hängde, tränade och peppade varandra. Därefter var tanken att alla skulle känna sig bekväma nog att vara med och tävla, oavsett nivå, ålder och kön. I tävlingen hade alla chans till priser.</p>
<p>Evenemanget arrangerades i samarbete med Backyard Session Tour, med Bollen Valencia som speaker.</p>
<h2>Mat och rabatt</h2>
<p>På Aktivt Uteliv nedanför backen går det att köpa lunch. På lördagar har de våffelbuffé, men säljer också korv och pajer. Medlemmar i Uppsala Crew får 10 procent rabatt mot uppvisat medlemskort.</p>
<h2>Sponsorer</h2>
<p>Tack till Eivy, Backyard Session Tour, Burton Europe, Osthang, Alpingaraget och Dragon.</p>"""},
    {"slug": "miniramp-madness-2024", "title": "Miniramp Madness 2024", "type": "Tävling", "sport": "Skateboard",
     "date": "2024-09-07", "date_h": "7 september 2024", "time": "11.00–19.15", "place": "KAP-rampen, Ulleråkersvägen 22, Uppsala",
     "img": "affisch-miniramp-madness-2024", "poster": True,
     "alt": "Affisch för Uppsala Open Miniramp Madness 7 september 2024 på KAP-rampen med klasserna tjej, junior och senior",
     "summary": "Minirampstävling på KAP-rampen med klasser för tjejer, juniorer och seniorer, plus skejtloppis.",
     "body": """<p>Året innan blev Miniramp Madness den största skejtfesten i Uppsala på många år. 2024 körde vi igen, med målet att få ännu fler åskådare och tävlande.</p>
<p>I prispotten låg 3 000 kr till bästa tjej och bästa senior, 1 500 kr till tvåan och 500 kr till trean. I juniorklassen fick vinnarna priser.</p>
<h2>Skejtloppis</h2>
<p>I samband med tävlingen bjöd vi in alla som hade något att sälja till en skejtloppis. Avlagda brädor, delar och kläder fick nya ägare.</p>
<h2>Tidsschema</h2>
<table class="schedule"><tbody>
<tr><th scope="row">11.00–13.00</th><td>Uppvärmning och anmälan</td></tr>
<tr><th scope="row">13.00–14.00</th><td>Kval juniorer</td></tr>
<tr><th scope="row">14.15–15.15</th><td>Kval dam</td></tr>
<tr><th scope="row">15.30–16.30</th><td>Kval senior</td></tr>
<tr><th scope="row">16.45–17.15</th><td>Final juniorer</td></tr>
<tr><th scope="row">17.30–18.00</th><td>Final dam</td></tr>
<tr><th scope="row">18.15–18.45</th><td>Final senior</td></tr>
<tr><th scope="row">18.45–19.00</th><td>Best trick</td></tr>
<tr><th scope="row">19.15</th><td>Prisutdelning</td></tr>
</tbody></table>"""},
    {"slug": "freeskilandslaget-i-sunnerstabacken-2024", "title": "Freeskilandslaget i Sunnerstabacken", "type": "Prova på", "sport": "Freeski",
     "date": "2024-02-27", "date_h": "27 februari 2024", "time": "18.00–20.30", "place": "Sunnerstabacken, Uppsala",
     "img": "affisch-freeski-sweden-2024", "poster": True,
     "alt": "Affisch: Freeski Sweden hälsar på, Sunnersta 27 februari, med en freeskiåkare i luften",
     "summary": "Freeski Sweden besökte backen för en kväll med åkning, coachning och autografer. Alla fick vara med.",
     "body": """<p>Tisdagen den 27 februari 2024 kom svenska freeskilandslaget till Sunnerstabacken som en del av sin turné till lokala backar. Alla fick vara med.</p>
<h2>Program</h2>
<table class="schedule"><tbody>
<tr><th scope="row">18.00</th><td>Samling vid liften, indelning i grupper och uppvärmning</td></tr>
<tr><th scope="row">18.20–20.00</th><td>Åkning, coachning och häng, kvällen filmades</td></tr>
<tr><th scope="row">20.00–20.30</th><td>Autografskrivning</td></tr>
<tr><th scope="row">20.30</th><td>Avslut</td></tr>
</tbody></table>"""},
    {"slug": "miniramp-madness-2023", "title": "Miniramp Madness 2023", "type": "Tävling", "sport": "Skateboard",
     "date": "2023-08-27", "date_h": "Augusti 2023", "time": None, "place": "KAP-rampen, Ulleråkersvägen 22, Uppsala",
     "img": "affisch-miniramp-madness-2023", "poster": True,
     "alt": "Affisch för Uppsala Open Miniramp Madness 2023 på KAP-rampen med klasserna junior, senior och tjej",
     "summary": "Den första upplagan av Miniramp Madness, med klasser för juniorer, seniorer och tjejer.",
     "body": """<p>Den första upplagan av Miniramp Madness, även kallad Uppsala Open, arrangerades på KAP-rampen vid Ulleråkersvägen 22. Tävlingen hade klasserna junior, senior och tjej och blev den största skejtfesten i Uppsala på många år. Den lade grunden för att tävlingen kom tillbaka året efter.</p>"""},
]

FAQ = [
    ("Vad kostar det att bli medlem?", "Medlemsavgiften är 50–100 kr per år. Du väljer själv beloppet utifrån vad du har råd med."),
    ("Vem kan bli medlem?", "Alla som åker skateboard, snowboard eller freeski, eller vill börja. Föreningen är till för den som åker för skojs skull och för den som vill träna, utvecklas och tävla på elitnivå."),
    ("Är jag försäkrad på era aktiviteter?", "Ja. Som medlem har du olycksfallsförsäkring genom Sveriges Skateboardförbund och Svenska Skidförbundet när du deltar i föreningens aktiviteter."),
    ("Behöver jag egen utrustning?", "Inte i Sunnerstabacken. Där finns möjlighet att låna utrustning och få coachning av våra instruktörer."),
    ("Var tränar ni?", "Skateboard på KAP-rampen, Kapellgärdet och inomhus på Allis Uppsala. Snowboard och freeski i Sunnerstabacken under vintern."),
]

PARTNERS = [
    ("Riksidrottsförbundet", "https://www.rf.se/"),
    ("Sveriges Skateboardförbund", "https://sverigesskateboardforbund.se/"),
    ("Svenska Skidförbundet", "https://www.skidor.com/"),
    ("RF-SISU Uppland", "https://www.rfsisu.se/distrikt/uppland"),
    ("Uppsala kommun, kultur och fritid", "https://www.uppsala.se/"),
]

# ---------------------------------------------------------------- mallar

NAV = [
    ("Verksamhet", None, [(f"/verksamhet/{a['slug']}/", a["title"], a["short"]) for a in ACTIVITIES]),
    ("Platser", "/platser/", None),
    ("Evenemang", "/evenemang/", None),
    ("Om föreningen", "/om-foreningen/", None),
    ("Kontakt", "/kontakt/", None),
]

CARET = '<svg class="caret" viewBox="0 0 10 10" aria-hidden="true"><path d="M1 3l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>'


def header(path):
    items = []
    for label, href, sub in NAV:
        if sub:
            cur = ' aria-current="page"' if path.startswith("/verksamhet/") else ""
            links = "".join(f'<li><a href="{h}">{e(t)}<span>{e(s)}</span></a></li>' for h, t, s in sub)
            items.append(f'<li class="has-drop"><button class="nav__link" aria-expanded="false" aria-controls="drop-{label.lower()}"{cur}>{label}{CARET}</button>'
                         f'<ul class="nav__drop" id="drop-{label.lower()}">{links}</ul></li>')
        else:
            cur = ' aria-current="page"' if path.startswith(href) else ""
            items.append(f'<li><a class="nav__link" href="{href}"{cur}>{label}</a></li>')
    return f"""<a class="skip" href="#innehall">Hoppa till innehållet</a>
<div class="topbar"><div class="wrap">
  <span class="topbar__places">Allis Uppsala · KAP-rampen · Kapellgärdet · Sunnerstabacken</span>
  <span class="topbar__right"><a href="tel:{ORG['phone_href']}">{ORG['phone']}</a><a href="{ORG['instagram']}" rel="noopener">Instagram</a></span>
</div></div>
<header class="header"><div class="wrap">
  <a class="brand" href="/"><img src="/assets/img/logo-192.png" width="44" height="44" alt="">
    <span>Uppsala Crew IF<small>Skateboard, snowboard och freeski</small></span></a>
  <button class="menu-btn" aria-expanded="false" aria-controls="nav">Meny</button>
  <nav class="nav" id="nav" aria-label="Huvudmeny">
    <ul class="nav__list">{''.join(items)}</ul>
    <a class="btn btn--line" href="/bli-medlem/">Bli medlem</a>
  </nav>
</div></header>"""


def footer():
    acts = "".join(f'<li><a href="/verksamhet/{a["slug"]}/">{a["title"]}</a></li>' for a in ACTIVITIES)
    places = "".join(f'<li><a href="/platser/{p["slug"]}/">{p["title"]}</a></li>' for p in PLACES)
    partners = "".join(f'<li><a href="{u}" rel="noopener">{n}</a></li>' for n, u in PARTNERS)
    return f"""<footer class="footer"><div class="wrap">
  <div class="footer__grid">
    <div class="footer__brand">
      <a class="brand" href="/"><img src="/assets/img/logo-192.png" width="44" height="44" alt="Uppsala Crew IF logotyp" loading="lazy"><span>Uppsala Crew IF<small>Ideell idrottsförening sedan {ORG['founded']}</small></span></a>
      <p class="muted" style="margin-top:1rem;max-width:34ch">Vi skapar bättre förutsättningar för skateboard, snowboard och freeski i Uppsala.</p>
    </div>
    <div><h2>Verksamhet</h2><ul>{acts}<li><a href="/evenemang/">Evenemang</a></li></ul></div>
    <div><h2>Platser</h2><ul>{places}</ul></div>
    <div><h2>Föreningen</h2><ul><li><a href="/om-foreningen/">Om föreningen</a></li><li><a href="/bli-medlem/">Bli medlem</a></li><li><a href="/kontakt/">Kontakt</a></li><li><a href="{ORG['instagram']}" rel="noopener">Instagram</a></li><li><a href="{ORG['facebook']}" rel="noopener">Facebook</a></li></ul></div>
    <div><h2>Kontakt</h2><ul>
      <li><a href="mailto:{ORG['email']}">{ORG['email']}</a></li>
      <li><a href="tel:{ORG['phone_href']}">{ORG['phone']}</a></li>
      <li style="padding:.3em 0">{ORG['street']}<br>{ORG['zip']} {ORG['city']}</li>
      <li style="padding:.3em 0">Org.nr {ORG['orgnr']}</li></ul></div>
  </div>
  <div style="margin-top:3rem"><h2>Vi samarbetar med och är anslutna till</h2><ul class="partners">{partners}</ul></div>
  <div class="footer__legal"><span>© {date.today().year} {ORG['legal']}. Org.nr {ORG['orgnr']}.</span><span><a href="/integritetspolicy/">Integritetspolicy</a></span></div>
</div></footer>"""


def org_ld():
    return {
        "@context": "https://schema.org", "@type": "SportsOrganization", "@id": SITE + "/#org",
        "name": ORG["name"], "legalName": ORG["legal"], "url": SITE + "/",
        "logo": SITE + "/assets/img/logo-512.png", "image": SITE + "/assets/img/og.jpg",
        "description": "Ideell idrottsförening för skateboard, snowboard och freeski i Uppsala.",
        "foundingDate": ORG["founded"], "email": ORG["email"], "telephone": ORG["phone_href"],
        "identifier": {"@type": "PropertyValue", "propertyID": "Organisationsnummer", "value": ORG["orgnr"]},
        "address": {"@type": "PostalAddress", "streetAddress": ORG["street"], "postalCode": ORG["zip"].replace(" ", ""),
                    "addressLocality": ORG["city"], "addressCountry": "SE"},
        "areaServed": {"@type": "City", "name": "Uppsala"},
        "sport": ["Skateboarding", "Snowboarding", "Freestyle skiing"],
        "memberOf": [{"@type": "SportsOrganization", "name": "Sveriges Skateboardförbund"},
                     {"@type": "SportsOrganization", "name": "Svenska Skidförbundet"}],
        "sameAs": [ORG["instagram"], ORG["facebook"]],
    }


def crumbs_ld(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + h} for i, (n, h) in enumerate(trail)]}


def crumbs_html(trail):
    lis = []
    for i, (n, h) in enumerate(trail):
        lis.append(f'<li><a href="{h}">{e(n)}</a></li>' if i < len(trail) - 1 else f'<li aria-current="page">{e(n)}</li>')
    return f'<nav class="crumbs" aria-label="Brödsmulor"><ol>{"".join(lis)}</ol></nav>'


PAGES = []


def page(path, title, desc, body, ld=None, og_img="/assets/img/og.jpg", trail=None, preload=None):
    ld = list(ld or [])
    ld.insert(0, org_ld())
    if trail:
        ld.append(crumbs_ld(trail))
    full_title = title if path == "/" else f"{title} – Uppsala Crew IF"
    pre = f'<link rel="preload" as="image" href="{preload[0]}" imagesrcset="{preload[1]}" imagesizes="100vw">' if preload else ""
    doc = f"""<!doctype html>
<html lang="sv" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta name="theme-color" content="#111214">
<meta property="og:type" content="website">
<meta property="og:locale" content="sv_SE">
<meta property="og:site_name" content="Uppsala Crew IF">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}{og_img}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/img/logo-64.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,400&display=swap">
{pre}
<link rel="stylesheet" href="/assets/tokens.css">
<link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">{json.dumps(ld if len(ld) > 1 else ld[0], ensure_ascii=False)}</script>
</head>
<body>
{header(path)}
<main id="innehall">
{crumbs_wrap(trail)}{body}
</main>
{footer()}
<script src="/assets/site.js" defer></script>
</body>
</html>
"""
    if BASE:
        import re
        doc = re.sub(r'(href|src|srcset|imagesrcset)="/(?!/)', lambda m: f'{m.group(1)}="{BASE}/', doc)
        doc = re.sub(r'(srcset="[^"]*")', lambda m: m.group(1).replace(' /assets', f' {BASE}/assets'), doc)
        doc = doc.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"')
    target = OUT / (path.strip("/") + "/index.html" if path != "/" else "index.html")
    if path == "/404/":
        target = OUT / "404.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc, encoding="utf-8")
    if path != "/404/":
        PAGES.append(path)


def crumbs_wrap(trail):
    return ""  # brödsmulor renderas i pagehead


def pagehead(trail, eyebrow, h1, lead, extra=""):
    return f"""<section class="pagehead"><div class="wrap">{crumbs_html(trail)}<div class="grid"><div>
<p class="eyebrow">{eyebrow}</p><h1>{h1}</h1><p class="lead">{lead}</p>{extra}</div></div></div></section>"""


def join_form(heading="Medlemsansökan"):
    return f"""<form class="form" data-mail="{ORG['email']}" data-subject="Medlemsansökan Uppsala Crew IF" action="mailto:{ORG['email']}" method="post" enctype="text/plain">
  <h3>{heading}</h3>
  <p class="muted" style="font-size:var(--fs-sm);margin:0">Fyll i dina uppgifter så får du ett mejl med vidare instruktioner och betalning.</p>
  <div class="field"><label for="m-namn">Namn</label><input id="m-namn" name="namn" data-label="Namn" autocomplete="name" required></div>
  <div class="field"><label for="m-epost">E-post</label><input id="m-epost" name="epost" type="email" data-label="E-post" autocomplete="email" required></div>
  <div class="field"><label for="m-sport">Vad åker du?</label><select id="m-sport" name="sport" data-label="Sport"><option value="">Välj</option><option>Skateboard</option><option>Snowboard</option><option>Freeski</option><option>Flera av dem</option></select></div>
  <div class="field"><label for="m-belopp">Medlemsavgift</label><select id="m-belopp" name="belopp" data-label="Avgift"><option>50 kr</option><option>75 kr</option><option selected>100 kr</option></select></div>
  <label class="check"><input type="checkbox" required><span>Jag godkänner att föreningen sparar mina uppgifter enligt <a class="textlink" style="min-height:0;display:inline" href="/integritetspolicy/">integritetspolicyn</a>.</span></label>
  <button class="btn btn--primary" type="submit">Skicka ansökan</button>
  <p class="form-status" role="status" aria-live="polite"></p>
</form>"""


def contact_block():
    return f"""<section class="contact" aria-labelledby="kontakt-h"><div class="wrap"><div class="contact__grid">
<div class="reveal"><p class="eyebrow" style="color:#9ba1a7"><b style="color:#fff">Kontakt</b></p>
<h2 id="kontakt-h" style="margin-bottom:var(--s-6);max-width:16ch">Frågor om träning, medlemskap eller samarbete</h2>
<div class="contact__big"><a href="mailto:{ORG['email']}">{ORG['email']}</a><a href="tel:{ORG['phone_href']}">{ORG['phone']}</a></div></div>
<div class="reveal"><dl>
<dt>Postadress</dt><dd>{ORG['street']}<br>{ORG['zip']} {ORG['city']}</dd>
<dt>Org.nr</dt><dd>{ORG['orgnr']}</dd>
<dt>Instagram</dt><dd><a href="{ORG['instagram']}" rel="noopener" style="color:#fff">@uppsalacrew</a></dd>
<dt>Facebook</dt><dd><a href="{ORG['facebook']}" rel="noopener" style="color:#fff">Uppsala Crew IF</a></dd>
</dl><p style="margin-top:var(--s-6)"><a class="btn btn--line" href="/kontakt/">Till kontaktsidan</a></p></div>
</div></div></section>"""


def event_row(ev, h="h3"):
    upcoming = ev["date"] >= TODAY
    status = '<span class="tag">Kommande</span>' if upcoming else '<span class="tag">Genomförd</span>'
    imgcls = "ev__img ev__img--poster" if ev["poster"] else "ev__img"
    time = f"<dt>Tid</dt><dd>{ev['time']}</dd>" if ev["time"] else ""
    return f"""<article class="ev reveal"><div class="{imgcls}">{img(ev['img'], ev['alt'], '(min-width:1024px) 55vw, 100vw')}</div>
<div><p class="ev__date">{ev['date_h']} {status}</p><{h}><a href="/evenemang/{ev['slug']}/">{e(ev['title'])}</a></{h}>
<p>{e(ev['summary'])}</p>
<dl><dt>Typ</dt><dd>{ev['type']}</dd><dt>Sport</dt><dd>{ev['sport']}</dd>{time}<dt>Plats</dt><dd>{e(ev['place'])}</dd></dl>
<a class="textlink" href="/evenemang/{ev['slug']}/"><span class="arrow">Läs om evenemanget</span></a></div></article>"""


def faq_ld(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


def event_ld(ev):
    return {"@context": "https://schema.org", "@type": "SportsEvent", "name": ev["title"], "startDate": ev["date"],
            "eventStatus": "https://schema.org/EventScheduled", "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "location": {"@type": "Place", "name": ev["place"].split(",")[0], "address": {"@type": "PostalAddress", "streetAddress": ev["place"], "addressLocality": "Uppsala", "addressCountry": "SE"}},
            "image": SITE + f"/assets/img/{ev['img']}-960.webp", "description": ev["summary"], "isAccessibleForFree": True,
            "organizer": {"@id": SITE + "/#org"}, "url": SITE + f"/evenemang/{ev['slug']}/"}


# ---------------------------------------------------------------- sidor

def build_home():
    hero_name = "snowboard-hopp-sunnerstabacken"
    rows = "".join(f"""<li><a href="/verksamhet/{a['slug']}/"><span class="n">0{i+1}</span><h3>{a['title']}</h3>
<span class="meta"><span>{e(a['short'])}</span><span><b>Var:</b> {e(a['where'])}</span><span><b>När:</b> {e(a['when'])}</span></span>
<span class="go arrow">Läs mer</span></a></li>""" for i, a in enumerate(ACTIVITIES))
    places = "".join(f"""<li><h3>{p['title']}</h3><p>{e(p['short'])}</p><a href="/platser/{p['slug']}/" class="textlink"><span class="arrow">Om {p['title']}</span></a></li>""" for p in PLACES)
    events = "".join(event_row(ev) for ev in EVENTS[:3])
    faq = "".join(f'<div class="faq__item"><h3>{e(q)}</h3><p>{e(a)}</p></div>' for q, a in FAQ)
    body = f"""
<section class="hero" aria-labelledby="hero-h">
  <div class="hero__media">{img(hero_name, 'Snowboardåkare i luften över ett hopp i Sunnerstabacken en solig vinterdag', '100vw', lazy=False)}</div>
  <div class="hero__text"><div class="wrap"><div>
    <h1 id="hero-h">Skateboard, snowboard och freeski i Uppsala</h1>
    <div class="hero__actions"><a class="btn btn--primary" href="/bli-medlem/">Bli medlem</a><a class="textlink" href="/om-foreningen/"><span class="arrow">Om föreningen</span></a></div>
  </div></div></div>
</section>
<div class="facts"><div class="wrap"><dl class="facts__panel">
  <div class="facts__item"><dt>Grundad</dt><dd>{ORG['founded']}</dd></div>
  <div class="facts__item"><dt>Sporter</dt><dd>Skate, snow, freeski</dd></div>
  <div class="facts__item"><dt>Medlemsavgift</dt><dd>50–100 kr per år</dd></div>
  <div class="facts__item"><dt>Försäkring</dt><dd>Ingår för medlemmar</dd></div>
</dl></div></div>

<section class="sec" aria-labelledby="v-h"><div class="wrap"><div class="grid">
  <div class="sec__head reveal"><p class="eyebrow"><b>01</b> Verksamhet</p>
  <h2 id="v-h">För dig som åker för skojs skull och för dig som vill tävla</h2>
  <p class="lead" style="margin-top:var(--s-5)">Uppsala Crew arbetar för bättre förutsättningar att åka skateboard, snowboard och freeski i Uppsala, från första försöket till elitnivå.</p></div>
  <ul class="table-list reveal">{rows}</ul>
</div></div></section>

<section class="sec--tight sec--grey" aria-labelledby="p-h"><div class="wrap" style="padding-top:var(--sec-tight);padding-bottom:var(--sec-tight)">
  <div class="places">
    <figure class="places__img reveal" style="margin:0">{img('freeski-hopp-sunnerstabacken', 'Freeskiåkare i luften över ett hopp i Sunnerstabacken med Mälaren i bakgrunden', '(min-width:1024px) 58vw, 100vw')}<figcaption>Sunnerstabacken, vintersäsong.</figcaption></figure>
    <div class="places__body reveal"><p class="eyebrow"><b>02</b> Platser</p><h2 id="p-h" style="margin-bottom:var(--s-6)">Här åker vi</h2><ul class="places__list">{places}</ul></div>
  </div>
</div></section>

<section class="sec--wide" aria-labelledby="e-h" style="padding:var(--sec-wide) 0"><div class="wrap">
  <div class="grid"><div class="sec__head reveal"><p class="eyebrow"><b>03</b> Evenemang</p><h2 id="e-h">Tävlingar och prova på</h2>
  <p class="lead" style="margin-top:var(--s-5)">Vi arrangerar tävlingar och evenemang som är öppna för alla nivåer, åldrar och kön.</p></div></div>
  {events}
  <p style="margin-top:var(--s-6)"><a class="btn btn--line arrow" href="/evenemang/">Alla evenemang</a></p>
</div></section>

<section><div class="wrap"><div class="duo duo--rev reveal">
<figure style="margin:0">{img('crew-instruktorer-backen', 'Instruktörer i Uppsala Crew-jackor vid backen en vinterkväll', '(min-width:768px) 40vw, 100vw')}<figcaption>Föreningens instruktörer i Sunnerstabacken.</figcaption></figure>
<figure style="margin:0">{img('snowboard-rail-funpark', 'Snowboardåkare på en box i funparken i Sunnerstabacken', '(min-width:768px) 60vw, 100vw')}<figcaption>Funparken, Sunnerstabacken.</figcaption></figure>
</div></div></section>

<section class="sec" aria-labelledby="m-h"><div class="wrap"><div class="join">
  <div class="reveal"><p class="eyebrow"><b>04</b> Medlemskap</p><h2 id="m-h">Bli medlem i Uppsala Crew IF</h2>
  <p class="price">50–100 kr <small>per år, du väljer belopp</small></p>
  <ul class="benefits">
    <li><span class="n">01</span><span>Du bidrar till bättre förutsättningar för skate-, snow- och freeskiåkning i Uppsala.</span></li>
    <li><span class="n">02</span><span>Fritt tillträde till föreningens evenemang och tävlingar.</span></li>
    <li><span class="n">03</span><span>Olycksfallsförsäkring genom Sveriges Skateboardförbund och Svenska Skidförbundet på våra aktiviteter.</span></li>
    <li><span class="n">04</span><span>10 procent rabatt på Aktivt Uteliv vid Sunnerstabacken mot uppvisat medlemskort.</span></li>
  </ul></div>
  <div class="reveal">{join_form()}</div>
</div></div></section>

<section class="sec--tight sec--grey" aria-labelledby="f-h" style="padding:var(--sec-base) 0"><div class="wrap"><div class="grid">
  <div class="faq-aside reveal"><p class="eyebrow"><b>05</b> Frågor</p><h2 id="f-h" style="font-size:var(--fs-h3)">Vanliga frågor</h2></div>
  <div class="faq reveal">{faq}</div>
</div></div></section>
{contact_block()}"""
    w = IMG[hero_name][0]
    srcset = ", ".join(f"/assets/img/{hero_name}-{x}.webp {x}w" for x in (480, 960, 1600, 2400))
    page("/", "Uppsala Crew IF – skateboard, snowboard och freeski i Uppsala",
         "Uppsala Crew IF är Uppsalas ideella förening för skateboard, snowboard och freeski. Skateskola, tävlingar och åkning på Allis, KAP-rampen och i Sunnerstabacken. Bli medlem för 50–100 kr per år.",
         body, ld=[faq_ld(FAQ), {"@context": "https://schema.org", "@type": "WebSite", "name": "Uppsala Crew IF", "url": SITE + "/", "inLanguage": "sv-SE", "publisher": {"@id": SITE + "/#org"}}],
         preload=(f"/assets/img/{hero_name}-960.webp", srcset))


def build_about():
    trail = [("Start", "/"), ("Om föreningen", "/om-foreningen/")]
    body = pagehead(trail, "<b>Föreningen</b>", "Om Uppsala Crew IF",
                    "Uppsala Crew Idrottsförening startade 2022 och är verksam inom skateboard, snowboard och freeski. Vi finns på Allis Uppsala, Kapellgärdet, KAP-rampen och i Sunnerstabacken.")
    body += f"""
<section class="sec"><div class="wrap"><div class="about">
  <div class="reveal"><p class="eyebrow"><b>Historik</b></p>
  <ol class="timeline">
    <li><span class="y">2022</span><p>Uppsala Crew Idrottsförening bildas.</p></li>
    <li><span class="y">2023</span><p>Första Miniramp Madness på KAP-rampen, den största skejtfesten i Uppsala på många år.</p></li>
    <li><span class="y">2024</span><p>Freeskilandslaget besöker Sunnerstabacken. Miniramp Madness körs igen med skejtloppis och prispott.</p></li>
    <li><span class="y">2025</span><p>Uppsala Rail Jam i Sunnerstabacken tillsammans med Backyard Session Tour.</p></li>
  </ol></div>
  <div class="prose reveal">
    <p class="eyebrow"><b>Vision</b></p>
    <h2 style="font-size:var(--fs-h2);margin-top:0">Vi vill sätta Uppsala på Sveriges skatekarta och få fler att hitta till vintersporterna</h2>
    <p>Föreningen finns till för den som bara åker för skojs skull, och för den som vill träna, utvecklas och tävla på elitnivå. Vi vill också öka antalet tjejer som skejtar och åker park i Uppsala.</p>
    <p><a class="textlink" href="/verksamhet/skateboard/"><span class="arrow">Om skateboard i föreningen</span></a><br>
    <a class="textlink" href="/verksamhet/snowboard-och-freeski/"><span class="arrow">Om snowboard och freeski</span></a></p>
  </div>
</div></div></section>
<section class="sec--tight" style="padding-bottom:var(--sec-tight)"><div class="wrap"><div class="duo reveal">
  <figure style="margin:0">{img('skateskola-grupp', 'Barn och ledare från skateskolan samlade med brädor i skatehallen', '(min-width:768px) 60vw, 100vw')}<figcaption>Skateskolan inomhus på Allis.</figcaption></figure>
  <figure style="margin:0">{img('kvallsaking-hopp-sunnersta', 'Upplyst hopp i Sunnerstabacken en vinterkväll', '(min-width:768px) 40vw, 100vw')}<figcaption>Kvällsåkning i Sunnerstabacken.</figcaption></figure>
</div></div></section>
<section class="sec sec--grey"><div class="wrap"><div class="split">
  <div class="prose reveal"><p class="eyebrow"><b>Organisation</b></p><h2 style="margin-top:0">En ideell idrottsförening</h2>
  <p>Uppsala Crew IF är en ideell förening som drivs av styrelse och ideella ledare. Medlemmar är försäkrade genom Sveriges Skateboardförbund och Svenska Skidförbundet vid föreningens aktiviteter.</p>
  <p>Vill du engagera dig som ledare, instruktör eller funktionär vid tävlingar? <a href="/kontakt/">Hör av dig till oss</a>.</p></div>
  <aside class="aside-box reveal"><dl>
    <dt>Namn</dt><dd>{ORG['legal']}</dd><dt>Org.nr</dt><dd>{ORG['orgnr']}</dd><dt>Grundad</dt><dd>{ORG['founded']}</dd>
    <dt>Säte</dt><dd>Uppsala</dd><dt>Förbund</dt><dd>Sveriges Skateboardförbund, Svenska Skidförbundet</dd></dl>
    <a class="btn btn--primary" href="/bli-medlem/">Bli medlem</a></aside>
</div></div></section>
{contact_block()}"""
    page("/om-foreningen/", "Om föreningen", "Uppsala Crew IF bildades 2022 och arbetar för skateboard, snowboard och freeski i Uppsala. Läs om vår historik, vision och organisation.", body, trail=trail)


def build_activities():
    trail0 = [("Start", "/"), ("Verksamhet", "/verksamhet/")]
    # Skateboard
    t = trail0 + [("Skateboard", "/verksamhet/skateboard/")]
    body = pagehead(t, "<b>Verksamhet</b> 01", "Skateboard i Uppsala",
                    "Skateskola, tävlingar och åkning för alla från fem år till pensionsålder. Vi åker på Allis Uppsala, KAP-rampen och Kapellgärdet.")
    body += f"""
<section class="bleed">{img('allis-bowl', 'Bowlen i skatehallen på Allis Uppsala med en skateboard på kanten', '100vw')}</section>
<section class="sec"><div class="wrap"><div class="split">
<div class="prose reveal">
<h2 style="margin-top:0">Från gatan till olympisk gren</h2>
<p>Skateboard har gått från att vara en lek på gatan till en respekterad sport på världsnivå. Det som började som en subkultur är i dag en av de snabbast växande grenarna inom actionsport, och sedan Tokyo 2021 är skateboard en olympisk gren.</p>
<p>Skateboard är också en kultur och ett sätt att uttrycka sig. Med rätt förutsättningar kan Uppsala bli en ledande kraft i den skateboardkultur som växer i världen.</p>
<h2>En sport på egna villkor</h2>
<p>Skateboard passar många barn och unga som inte trivs i traditionella lagsporter med strikta träningstider. Forskning visar att skateboard är en bra aktivitet för personer med neuropsykiatriska diagnoser: den är pulshöjande, social, individanpassad och inkluderande. Du tar paus när du vill och lägger upp träningen som det passar dig.</p>
<p>Sporten kräver relativt lite pengar, vilket gör den tillgänglig för många och kan bidra till att bryta exkludering.</p>
<h2>Alla åldrar på samma ramp</h2>
<p>Skateboard är en av få sporter där barn och vuxna åker tillsammans, på samma villkor och samma tider. Det skapar en trygg plats där unga tränar med äldre åkare och en gemenskap över åldrarna. Det ökar också chansen att man fortsätter åka hela livet.</p>
<h2>Vår vision</h2>
<p>Vi vill utveckla skateboard som sport i Uppsala och sätta staden på Sveriges skatekarta. Vi vill ge den som vill möjlighet att träna mot elitnivå, ordna aktiviteter för den som åker för nöjes skull och öka antalet tjejer som skejtar.</p>
</div>
<aside class="aside-box reveal" style="align-self:start;position:sticky;top:7rem"><dl>
<dt>Platser</dt><dd>Allis Uppsala, KAP-rampen, Kapellgärdet</dd><dt>Träning</dt><dd>Skateskola måndagar 18.00–19.00</dd><dt>Tävling</dt><dd>Miniramp Madness</dd></dl>
<p><a class="btn btn--primary" href="/verksamhet/skateskola/">Om skateskolan</a></p>
<p><a class="textlink" href="/bli-medlem/"><span class="arrow">Bli medlem</span></a></p></aside>
</div></div></section>
<section class="sec--tight" style="padding-bottom:var(--sec-base)"><div class="wrap"><div class="duo duo--rev reveal">
<figure style="margin:0">{img('allis-skatehall-2', 'Översikt över skatehallen på Allis med ramper och boxar', '(min-width:768px) 40vw, 100vw')}</figure>
<figure style="margin:0">{img('allis-skatehall-1', 'Skatehallen på Allis med street-hinder och rails', '(min-width:768px) 60vw, 100vw')}<figcaption>Allaktivitetshuset Allis, Uppsala.</figcaption></figure>
</div></div></section>"""
    page("/verksamhet/skateboard/", "Skateboard i Uppsala", "Skateboard med Uppsala Crew IF: skateskola, tävlingar och åkning för alla åldrar på Allis Uppsala, KAP-rampen och Kapellgärdet.", body, trail=t,
         ld=[{"@context": "https://schema.org", "@type": "Service", "name": "Skateboard", "serviceType": "Skateboardträning och tävlingar", "provider": {"@id": SITE + "/#org"}, "areaServed": "Uppsala"}])

    # Snowboard & freeski
    t = trail0 + [("Snowboard och freeski", "/verksamhet/snowboard-och-freeski/")]
    body = pagehead(t, "<b>Verksamhet</b> 02", "Snowboard och freeski i Sunnerstabacken",
                    "Under vintern håller vi till i Sunnerstabacken. Där finns en funpark, utrustning att låna och instruktörer som coachar.")
    body += f"""
<section class="bleed">{img('snowboard-hopp-sunnerstabacken', 'Snowboardåkare i luften över ett hopp i Sunnerstabacken', '100vw')}</section>
<section class="sec"><div class="wrap"><div class="split">
<div class="prose reveal">
<h2 style="margin-top:0">Två sporter, samma park</h2>
<p>Snowboard föddes ur surfare och skejtare i USA på 1960-talet som experimenterade fram nya vinteraktiviteter. Sedan 1998 är snowboard en olympisk gren.</p>
<p>Freeski är den yngsta grenen och växte fram på 1990-talet, när puckelpiståkare inspirerades av snowboardåkare och ville bort från de regeltyngda delarna av skidåkningen. Tillväxten har ökat kraftigt de senaste tio åren, och 2014 blev freeski olympisk gren.</p>
<h2>Big air, halfpipe och slopestyle</h2>
<p>Det är de tävlingsgrenar som vuxit sig starkast i båda disciplinerna, med stora tävlingar runt om i världen och en organiserad världscup. Bedömningen bygger på utförande, svårighetsgrad, luftfärd, variation, kombination och risktagande, alltså hur långt du vågar pusha din tekniska nivå och samtidigt behålla kontrollen.</p>
<p>Ledordet i båda sporterna är att lista ut vad som går att göra och som helst aldrig gjorts förut.</p>
<h2>Hemmabacken räcker</h2>
<p>Parkåkning kräver lite snö och få hinder. Därför går det att träna länge under säsongen, även när det finns lite snö kvar. När liftarna är stängda hikar man upp till hindren. Barn och unga som tränar i sin lokala backe kan bli lika duktiga som elitåkare, utan att åka till stora anläggningar i fjällen.</p>
<h2>Vår vision</h2>
<p>De flesta barn och unga har inte råd att åka till fjällen varje år, men att åka i den lokala backen kostar ofta lite. Vi vill att alla, oavsett ekonomi, ska kunna åka i Sunnersta. Vi vill också öka antalet tjejer som åker park, särskilt inom freeski där tjejerna är för få i hela Sverige.</p>
</div>
<aside class="aside-box reveal" style="align-self:start;position:sticky;top:7rem"><dl>
<dt>Plats</dt><dd>Sunnerstabacken</dd><dt>Säsong</dt><dd>Vinter, när backen har öppet</dd><dt>Utrustning</dt><dd>Går att låna</dd><dt>Tävling</dt><dd>Uppsala Rail Jam</dd></dl>
<p><a class="btn btn--primary" href="/platser/sunnerstabacken/">Om Sunnerstabacken</a></p>
<p><a class="textlink" href="/bli-medlem/"><span class="arrow">Bli medlem</span></a></p></aside>
</div></div></section>
<section style="padding-bottom:var(--sec-base)"><div class="wrap"><div class="duo reveal">
<figure style="margin:0">{img('snowboard-rail-funpark', 'Snowboardåkare på en box i funparken i Sunnerstabacken', '(min-width:768px) 60vw, 100vw')}</figure>
<figure style="margin:0">{img('kvallsaking-hopp-sunnersta', 'Upplyst hopp i Sunnerstabacken en vinterkväll', '(min-width:768px) 40vw, 100vw')}</figure>
</div></div></section>"""
    page("/verksamhet/snowboard-och-freeski/", "Snowboard och freeski i Uppsala", "Parkåkning i snowboard och freeski i Sunnerstabacken med Uppsala Crew IF. Låna utrustning, få coachning och tävla i Uppsala Rail Jam.", body, trail=t,
         ld=[{"@context": "https://schema.org", "@type": "Service", "name": "Snowboard och freeski", "serviceType": "Coachning och parkåkning", "provider": {"@id": SITE + "/#org"}, "areaServed": "Uppsala"}])

    # Skateskola
    t = trail0 + [("Skateskola", "/verksamhet/skateskola/")]
    body = pagehead(t, "<b>Verksamhet</b> 03", "Skateskola på måndagar",
                    "Ledarledd skateträning för barn och unga. Utomhus på KAP-rampen så länge vädret tillåter, inomhus på Allis Uppsala när det blir kallt.")
    body += f"""
<section class="sec--tight" style="padding-top:var(--sec-tight)"><div class="wrap"><div class="split">
<figure class="reveal" style="margin:0">{img('skateskola-grupp', 'Barn och ledare från skateskolan samlade med brädor i skatehallen', '(min-width:1024px) 58vw, 100vw')}<figcaption>Skateskolans deltagare och ledare.</figcaption></figure>
<aside class="aside-box reveal" style="align-self:start"><dl>
<dt>Dag</dt><dd>Måndagar</dd><dt>Tid</dt><dd>18.00–19.00</dd><dt>Plats</dt><dd>KAP-rampen, Ulleråkersvägen 22</dd><dt>Vinter</dt><dd>Inomhus på Allis Uppsala</dd><dt>Regn</dt><dd>Utomhusträning ställs in</dd></dl>
<a class="btn btn--primary" href="/bli-medlem/">Bli medlem</a></aside>
</div></div></section>
<section class="sec"><div class="wrap"><div class="prose reveal">
<h2 style="margin-top:0">Så fungerar skateskolan</h2>
<p>Träningen hålls på måndagar klockan 18.00–19.00. Under den varma delen av året är vi på KAP-rampen och kör så länge vädret tillåter. Vid regn ställs utomhusträningen in. När temperaturen sjunker flyttar träningen inomhus till Allis Uppsala.</p>
<p>Ta med bräda och hjälm. Är du osäker på vad som gäller just den här veckan, följ <a href="{ORG['instagram']}" rel="noopener">@uppsalacrew på Instagram</a> där vi lägger ut ändringar och inställda pass.</p>
<div class="notice">Datum för terminsstart publiceras på Instagram. Kontakta oss på <a href="mailto:{ORG['email']}">{ORG['email']}</a> om du har frågor om platser och nivåer.</div>
</div></div></section>"""
    page("/verksamhet/skateskola/", "Skateskola i Uppsala", "Skateskola för barn och unga i Uppsala på måndagar 18.00–19.00 på KAP-rampen och inomhus på Allis. Arrangeras av Uppsala Crew IF.", body, trail=t,
         ld=[{"@context": "https://schema.org", "@type": "Service", "name": "Skateskola", "serviceType": "Skateboardträning för barn och unga", "provider": {"@id": SITE + "/#org"}, "areaServed": "Uppsala"}])

    # Verksamhet översikt
    t = trail0
    rows = "".join(f"""<li><a href="/verksamhet/{a['slug']}/"><span class="n">0{i+1}</span><h3>{a['title']}</h3>
<span class="meta"><span>{e(a['short'])}</span><span><b>Var:</b> {e(a['where'])}</span><span><b>När:</b> {e(a['when'])}</span></span><span class="go arrow">Läs mer</span></a></li>""" for i, a in enumerate(ACTIVITIES))
    body = pagehead(t, "<b>Verksamhet</b>", "Det här gör vi", "Träning, coachning och tävlingar i skateboard, snowboard och freeski i Uppsala.")
    body += f'<section class="sec"><div class="wrap"><div class="grid"><ul class="table-list">{rows}</ul></div></div></section>'
    page("/verksamhet/", "Verksamhet", "Uppsala Crew IF:s verksamhet: skateboard, snowboard, freeski och skateskola i Uppsala.", body, trail=t)


def build_places():
    t0 = [("Start", "/"), ("Platser", "/platser/")]
    lst = "".join(f"""<li><h3><a href="/platser/{p['slug']}/" style="text-decoration:none">{p['title']}</a></h3><p>{e(p['short'])}</p><p class="muted">{e(p['addr'])}</p></li>""" for p in PLACES)
    lst += '<li><h3>Kapellgärdet</h3><p>Område vid KAP-rampen där vi också håller till under skateboardsäsongen.</p></li>'
    body = pagehead(t0, "<b>Platser</b>", "Här åker vi i Uppsala", "Fyra platser, tre sporter. Utomhus på sommaren, inomhus när det blir kallt och i backen på vintern.")
    body += f"""<section class="sec"><div class="wrap"><div class="places">
<figure class="places__img reveal" style="margin:0">{img('allis-skatehall-2', 'Skatehallen i Allaktivitetshuset Allis', '(min-width:1024px) 58vw, 100vw')}<figcaption>Allis Uppsala.</figcaption></figure>
<div class="places__body reveal"><ul class="places__list">{lst}</ul></div></div></div></section>"""
    page("/platser/", "Platser", "Var Uppsala Crew IF åker: Sunnerstabacken, Allis Uppsala, KAP-rampen och Kapellgärdet.", body, trail=t0)

    texts = {
        "sunnerstabacken": f"""<p>Under vintersäsongen håller Uppsala Crew till i Sunnerstabacken. Här finns en funpark med hopp, boxar och rails som varierar beroende på säsong och snöläge.</p>
<p>Det går att låna utrustning och få coachning av föreningens instruktörer. Här arrangerar vi också Uppsala Rail Jam, och 2024 fick backen besök av freeskilandslaget.</p>
<h2>Mat och medlemsrabatt</h2><p>På Aktivt Uteliv nedanför backen går det att köpa lunch. Medlemmar får 10 procent rabatt mot uppvisat medlemskort.</p>
<h2>Öppettider</h2><p>Backens öppettider varierar med väder och snö. Aktuella tider finns hos Sunnerstabacken. Föreningens aktiviteter meddelas på <a href="{ORG['instagram']}" rel="noopener">Instagram</a>.</p>""",
        "allis-uppsala": f"""<p>Allaktivitetshuset Allis har en skatehall med bowl, ramper och street-hinder. När det blir för kallt för KAP-rampen flyttar skateskolan inomhus hit.</p>
<p>Hallen gör det möjligt att skejta året runt i Uppsala, oavsett väder.</p>
<p><a class="textlink" href="/verksamhet/skateskola/"><span class="arrow">Om skateskolan</span></a></p>""",
        "kap-rampen": f"""<p>KAP-rampen är en miniramp utomhus vid Kapellgärdet, Ulleråkersvägen 22. Det är skateskolans hemmaplan under den varma delen av året och platsen där vi arrangerar Miniramp Madness.</p>
<p>Träningen här hålls på måndagar 18.00–19.00 så länge vädret tillåter. Vid regn ställs den in.</p>
<p><a class="textlink" href="/evenemang/miniramp-madness-2024/"><span class="arrow">Om Miniramp Madness</span></a></p>""",
    }
    for p in PLACES:
        t = t0 + [(p["title"], f"/platser/{p['slug']}/")]
        body = pagehead(t, "<b>Platser</b>", p["title"], p["short"])
        hero = f'<section class="bleed">{img(p["img"], p["alt"], "100vw")}</section>' if p["img"] else ""
        if p["slug"] == "kap-rampen":
            hero = f'<section class="bleed">{img("affisch-miniramp-madness-2024", "Affisch för Miniramp Madness på KAP-rampen", "100vw", cls="")}</section>'
            hero = ""
        body += hero + f"""<section class="sec"><div class="wrap"><div class="split">
<div class="prose reveal">{texts[p['slug']]}</div>
<aside class="aside-box reveal" style="align-self:start"><dl><dt>Adress</dt><dd>{e(p['addr'])}</dd></dl>
<a class="btn btn--line" href="https://www.google.com/maps/search/?api=1&amp;query={e(p['addr'].replace(' ', '+'))}" rel="noopener">Visa på karta</a></aside>
</div></div></section>"""
        page(f"/platser/{p['slug']}/", f"{p['title']}, Uppsala", f"{p['title']}: {p['short']} Uppsala Crew IF.", body, trail=t,
             ld=[{"@context": "https://schema.org", "@type": "SportsActivityLocation", "name": p["title"], "address": {"@type": "PostalAddress", "streetAddress": p["addr"], "addressLocality": "Uppsala", "addressCountry": "SE"}}])


def build_events():
    t0 = [("Start", "/"), ("Evenemang", "/evenemang/")]
    rows = "".join(event_row(ev, "h2") for ev in EVENTS)
    upcoming = [ev for ev in EVENTS if ev["date"] >= TODAY]
    note = "" if upcoming else f'<div class="notice">Inga kommande evenemang är publicerade just nu. Nya datum läggs först ut på <a href="{ORG["instagram"]}" rel="noopener">Instagram</a>.</div>'
    body = pagehead(t0, "<b>Evenemang</b>", "Tävlingar och evenemang", "Här kan du läsa om tävlingar och evenemang som Uppsala Crew arrangerar eller är med och arrangerar.", note)
    body += f'<section class="sec"><div class="wrap">{rows}</div></section>'
    page("/evenemang/", "Evenemang", "Tävlingar och evenemang med Uppsala Crew IF: Uppsala Rail Jam, Miniramp Madness och besök av freeskilandslaget.", body, trail=t0,
         ld=[event_ld(ev) for ev in EVENTS])
    for ev in EVENTS:
        t = t0 + [(ev["title"], f"/evenemang/{ev['slug']}/")]
        past = ev["date"] < TODAY
        status = "Genomförd" if past else "Kommande"
        body = pagehead(t, f"<b>{ev['type']}</b> {ev['sport']}", e(ev["title"]), e(ev["summary"]))
        time = f"<dt>Tid</dt><dd>{ev['time']}</dd>" if ev["time"] else ""
        body += f"""<section class="sec"><div class="wrap"><div class="split">
<div class="prose reveal">{ev['body']}</div>
<aside class="reveal" style="align-self:start"><div class="aside-box"><dl><dt>Status</dt><dd>{status}</dd><dt>Datum</dt><dd>{ev['date_h']}</dd>{time}<dt>Plats</dt><dd>{e(ev['place'])}</dd><dt>Sport</dt><dd>{ev['sport']}</dd></dl></div>
<figure style="margin:var(--s-6) 0 0">{img(ev['img'], ev['alt'], '(min-width:1024px) 30vw, 100vw', cls='poster')}</figure></aside>
</div></div></section>"""
        page(f"/evenemang/{ev['slug']}/", ev["title"], f"{ev['title']}, {ev['date_h']}, {ev['place']}. {ev['summary']}", body, trail=t, ld=[event_ld(ev)],
             og_img=f"/assets/img/{ev['img']}-960.webp")


def build_join():
    t = [("Start", "/"), ("Bli medlem", "/bli-medlem/")]
    body = pagehead(t, "<b>Medlemskap</b>", "Bli medlem i Uppsala Crew IF",
                    "Som medlem bidrar du till bättre förutsättningar för skate-, snow- och freeskiåkning i Uppsala. Avgiften är 50–100 kr per år, beroende på vad du har råd med.")
    body += f"""<section class="sec"><div class="wrap"><div class="join">
<div class="reveal"><h2 style="font-size:var(--fs-h3)">Det här ingår</h2>
<ul class="benefits">
<li><span class="n">01</span><span>Fritt tillträde till föreningens evenemang och tävlingar.</span></li>
<li><span class="n">02</span><span>Olycksfallsförsäkring genom Sveriges Skateboardförbund och Svenska Skidförbundet på föreningens aktiviteter.</span></li>
<li><span class="n">03</span><span>10 procent rabatt på Aktivt Uteliv vid Sunnerstabacken mot uppvisat medlemskort.</span></li>
<li><span class="n">04</span><span>Du stöttar ideellt arbete för fler platser att åka på och fler tjejer i parken.</span></li>
</ul>
<h2 style="font-size:var(--fs-h3);margin-top:var(--s-8)">Så går det till</h2>
<ul class="benefits">
<li><span class="n">01</span><span>Fyll i namn och e-post i formuläret.</span></li>
<li><span class="n">02</span><span>Du får ett mejl från föreningen med vidare instruktioner.</span></li>
<li><span class="n">03</span><span>Betala medlemsavgiften, 50–100 kr, så är du medlem för året.</span></li>
</ul></div>
<div class="reveal">{join_form()}</div>
</div></div></section>"""
    page("/bli-medlem/", "Bli medlem", "Bli medlem i Uppsala Crew IF för 50–100 kr per år. Fritt tillträde till evenemang och olycksfallsförsäkring på föreningens aktiviteter.", body, trail=t)


def build_contact():
    t = [("Start", "/"), ("Kontakt", "/kontakt/")]
    body = pagehead(t, "<b>Kontakt</b>", "Kontakta Uppsala Crew IF", f"Du når oss enklast via e-post. För senaste nytt om träningar och evenemang, följ @uppsalacrew på Instagram.")
    body += f"""<section class="sec"><div class="wrap"><div class="split">
<div class="reveal">
<div class="contact__big" style="--x:0"><a href="mailto:{ORG['email']}" style="color:var(--ink);border-color:var(--line)">{ORG['email']}</a><a href="tel:{ORG['phone_href']}" style="color:var(--ink);border-color:var(--line)">{ORG['phone']}</a></div>
<form class="form" style="margin-top:var(--s-7)" data-mail="{ORG['email']}" data-subject="Meddelande via uppsalacrew.se" action="mailto:{ORG['email']}" method="post" enctype="text/plain">
<h2 style="font-size:var(--fs-h4)">Skicka ett meddelande</h2>
<div class="field"><label for="k-namn">Namn</label><input id="k-namn" data-label="Namn" autocomplete="name" required></div>
<div class="field"><label for="k-epost">E-post</label><input id="k-epost" type="email" data-label="E-post" autocomplete="email" required></div>
<div class="field"><label for="k-amne">Ärende</label><select id="k-amne" data-label="Ärende"><option>Medlemskap</option><option>Skateskola</option><option>Evenemang</option><option>Samarbete och sponsring</option><option>Annat</option></select></div>
<div class="field"><label for="k-msg">Meddelande</label><textarea id="k-msg" data-label="Meddelande" required></textarea></div>
<label class="check"><input type="checkbox" required><span>Jag godkänner att föreningen sparar mina uppgifter för att kunna svara, enligt <a href="/integritetspolicy/">integritetspolicyn</a>.</span></label>
<button class="btn btn--primary" type="submit">Skicka meddelande</button>
<p class="form-status" role="status" aria-live="polite"></p>
</form></div>
<aside class="aside-box reveal" style="align-self:start"><dl>
<dt>Förening</dt><dd>{ORG['legal']}</dd><dt>Postadress</dt><dd>{ORG['street']}<br>{ORG['zip']} {ORG['city']}</dd><dt>Org.nr</dt><dd>{ORG['orgnr']}</dd>
<dt>E-post</dt><dd><a href="mailto:{ORG['email']}">{ORG['email']}</a><br><a href="mailto:{ORG['email_alt']}">{ORG['email_alt']}</a></dd>
<dt>Instagram</dt><dd><a href="{ORG['instagram']}" rel="noopener">@uppsalacrew</a></dd><dt>Facebook</dt><dd><a href="{ORG['facebook']}" rel="noopener">Uppsala Crew IF</a></dd></dl></aside>
</div></div></section>"""
    page("/kontakt/", "Kontakt", f"Kontakta Uppsala Crew IF på {ORG['email']} eller {ORG['phone']}. Postadress {ORG['street']}, {ORG['zip']} Uppsala. Org.nr {ORG['orgnr']}.", body, trail=t,
         ld=[{"@context": "https://schema.org", "@type": "ContactPage", "name": "Kontakt", "about": {"@id": SITE + "/#org"}}])


def build_privacy():
    t = [("Start", "/"), ("Integritetspolicy", "/integritetspolicy/")]
    body = pagehead(t, "<b>Integritet</b>", "Integritetspolicy", "Så hanterar Uppsala Crew IF personuppgifter enligt dataskyddsförordningen (GDPR).")
    body += f"""<section class="sec"><div class="wrap"><div class="prose">
<h2 style="margin-top:0">Personuppgiftsansvarig</h2><p>{ORG['legal']}, org.nr {ORG['orgnr']}, {ORG['street']}, {ORG['zip']} {ORG['city']}. E-post <a href="mailto:{ORG['email']}">{ORG['email']}</a>.</p>
<h2>Vilka uppgifter vi behandlar</h2><p>När du ansöker om medlemskap eller kontaktar oss behandlar vi de uppgifter du själv lämnar, till exempel namn och e-postadress. Formulären på webbplatsen öppnar ett e-postmeddelande som du själv skickar till föreningen.</p>
<h2>Varför</h2><p>Vi behandlar uppgifterna för att administrera medlemskap, försäkring via förbunden, kallelser och för att besvara frågor. Den rättsliga grunden är avtal (medlemskap) och berättigat intresse (kontakt).</p>
<h2>Hur länge</h2><p>Medlemsuppgifter sparas så länge du är medlem och därefter så länge lagen kräver, exempelvis för bokföring. Övrig korrespondens raderas när ärendet är avslutat.</p>
<h2>Dina rättigheter</h2><p>Du har rätt att begära utdrag, rättelse eller radering av dina uppgifter, och att invända mot behandlingen. Kontakta oss på e-postadressen ovan. Du kan också vända dig till Integritetsskyddsmyndigheten.</p>
<h2>Kakor</h2><p>Webbplatsen använder inga spårningskakor. Typsnitt hämtas från Google Fonts.</p>
</div></div></section>"""
    page("/integritetspolicy/", "Integritetspolicy", "Så hanterar Uppsala Crew IF dina personuppgifter enligt GDPR.", body, trail=t)


def build_404():
    body = pagehead([("Start", "/"), ("Sidan finns inte", "/404/")], "<b>404</b>", "Sidan finns inte", "Sidan kan ha flyttats när webbplatsen gjordes om.",
                    '<p style="margin-top:2rem"><a class="btn btn--primary" href="/">Till startsidan</a></p>')
    page("/404/", "Sidan finns inte", "Sidan kunde inte hittas.", body)


def build_meta():
    urls = "".join(f"<url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in PAGES)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    llms = f"""# Uppsala Crew IF

> Ideell idrottsförening i Uppsala för skateboard, snowboard och freeski. Grundad {ORG['founded']}. Org.nr {ORG['orgnr']}.

## Verksamhet
""" + "".join(f"- [{a['title']}]({SITE}/verksamhet/{a['slug']}/): {a['short']} Var: {a['where']}. När: {a['when']}.\n" for a in ACTIVITIES) + """
## Platser
""" + "".join(f"- [{p['title']}]({SITE}/platser/{p['slug']}/): {p['short']} ({p['addr']})\n" for p in PLACES) + """
## Evenemang
""" + "".join(f"- [{ev['title']}]({SITE}/evenemang/{ev['slug']}/): {ev['date_h']}, {ev['place']}.\n" for ev in EVENTS) + f"""
## Medlemskap
- Avgift 50–100 kr per år. Inkluderar fritt tillträde till evenemang och olycksfallsförsäkring via Sveriges Skateboardförbund och Svenska Skidförbundet. [Bli medlem]({SITE}/bli-medlem/)

## Kontakt
- E-post: {ORG['email']}
- Telefon: {ORG['phone']}
- Postadress: {ORG['street']}, {ORG['zip']} {ORG['city']}
- Instagram: {ORG['instagram']}
"""
    (OUT / "llms.txt").write_text(llms)
    # Omdirigeringar från gamla WordPress-adresser (Netlify/Cloudflare Pages-format)
    (OUT / "_redirects").write_text("""/om-oss /om-foreningen/ 301
/?page_id=8739 /om-foreningen/ 301
/?page_id=8733 /kontakt/ 301
/?page_id=8460 /evenemang/ 301
/?page_id=3938 /bli-medlem/ 301
""")
    (OUT / ".htaccess").write_text("""ErrorDocument 404 /404.html
RewriteEngine On
RewriteCond %{QUERY_STRING} ^page_id=8739$
RewriteRule ^$ /om-foreningen/? [R=301,L]
RewriteCond %{QUERY_STRING} ^page_id=8733$
RewriteRule ^$ /kontakt/? [R=301,L]
RewriteCond %{QUERY_STRING} ^page_id=8460$
RewriteRule ^$ /evenemang/? [R=301,L]
RewriteCond %{QUERY_STRING} ^page_id=3938$
RewriteRule ^$ /bli-medlem/? [R=301,L]
RewriteCond %{QUERY_STRING} ^event-item=uppsala-rail-jam
RewriteRule ^$ /evenemang/uppsala-rail-jam-2025/? [R=301,L]
RewriteCond %{QUERY_STRING} ^event-item=miniramp-madness
RewriteRule ^$ /evenemang/miniramp-madness-2024/? [R=301,L]
RewriteCond %{QUERY_STRING} ^event-item=freeskilandslaget
RewriteRule ^$ /evenemang/freeskilandslaget-i-sunnerstabacken-2024/? [R=301,L]
<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType image/webp "access plus 1 year"
ExpiresByType text/css "access plus 1 month"
ExpiresByType application/javascript "access plus 1 month"
</IfModule>
""")


if __name__ == "__main__":
    import shutil
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    build_home(); build_about(); build_activities(); build_places(); build_events(); build_join(); build_contact(); build_privacy(); build_404()
    build_meta()
    print(f"{len(PAGES)} sidor byggda i {OUT}")
