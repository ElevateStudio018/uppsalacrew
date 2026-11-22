# Uppdrag: temavariant av Uppsala Crew IF:s webbplats

Repo: /home/user/uppsalacrew. Publiceras via GitHub Pages från `docs/` på https://elevatestudio018.github.io/uppsalacrew/.

## Det du har
- `content/content.json` – ALLT innehåll (texter, sidor, fakta, FAQ, platser, tävlingsformat, partners, galleri). Använd bara detta. Hitta aldrig på siffror, namn, omdömen, datum, citat, kontaktuppgifter, styrelsenamn eller kommande evenemang. Inga datumsatta evenemang ska finnas på sajten.
- `docs/media/` – gemensam bildpool i WebP (`<namn>-<bredd>.webp`), `manifest.json` med originalmått, tillgängliga bredder och alt-text. Loggor: `logo-rund-{64,192,512}.png` (vit rund logga på svart), `logo-ljus.png` / `logo-ljus-192.png` (svart logga, transparent utanför cirkeln). Rita aldrig en egen logga. Referera bilder med absolut sökväg `/uppsalacrew/media/...`.
- `build.py` i roten = första versionen (v00, stram förbundsstil). Titta gärna för struktur/SEO-mönster, men din design ska vara HELT annorlunda.

## Det du ska leverera, per tema NN
- `themes/vNN/build.py` (Python 3, bara standardbibliotek) som läser `content/content.json` + `docs/media/manifest.json` och skriver hela sajten till `docs/vNN/`. Egen CSS/JS under `docs/vNN/assets/`. Inga byggverktyg, inga npm-paket, inga tunga JS-bibliotek (vanilla JS).
- Alla interna länkar och resurser börjar med `/uppsalacrew/vNN/` (sidor) resp. `/uppsalacrew/media/` (bilder). Rena URL:er: `docs/vNN/<slug>/index.html`.
- Alla sidor i `pages` i content.json ska finnas (18 st), plus `404.html`. Varje sida: unik `<title>` och metabeskrivning, en h1, logisk rubrikordning, canonical till `https://www.uppsalacrew.se/<slug>/`, Open Graph, `<meta name="robots" content="noindex">` (det är en förhandsvisning), JSON-LD (SportsOrganization på alla sidor, FAQPage på vanliga-fragor, BreadcrumbList på undersidor, Service på sportsidorna, SportsActivityLocation på platssidorna).
- Bilder: `<img>` med srcset från manifestets widths, width/height, lazy utom hero, beskrivande alt.
- Formulär (bli medlem, kontakt): skickas som förifyllt mejl (mailto via JS, som i v00), med samtyckesruta och länk till integritetspolicyn.
- Mobil först: inga horisontella scrollar på 390 px, tryckytor ≥44 px, fungerande meny (tangentbord + Escape). Synlig fokusring. Kontrast WCAG AA. `prefers-reduced-motion` ska ge en komplett, stilla sida.
- Svensk copy från content.json; du får skriva korta rubriker/ingresser men inga utropstecken, ingen emoji, inga klyschor ("Välkommen till", "passion", "allt från A till Ö").
- Förbjudna typsnitt: Poppins, Montserrat, Outfit, Plus Jakarta Sans, Raleway, Nunito, Quicksand, Lato, Open Sans, Roboto, Inter som rubrik. Inga lila→blå-gradienter, inga glaspaneler, inga emoji-ikoner, inte "tre lika kort med ikon i cirkel".

## Verifiering (obligatorisk)
1. Kör `python3 themes/vNN/build.py`.
2. Starta `cd /home/user/uppsalacrew && python3 -m http.server <unik port>` i bakgrunden — servern måste köras från repo-roten med en symlänk eller motsvarande så att `/uppsalacrew/` mappar till `docs/`: enklast `mkdir -p /tmp/ucsrv_NN && ln -sfn /home/user/uppsalacrew/docs /tmp/ucsrv_NN/uppsalacrew && python3 -m http.server PORT -d /tmp/ucsrv_NN`.
3. Med Playwright (förinstallerat, `require('playwright')`, `chromium.launch()`): ta helsidesskärmdumpar av start + minst tre undersidor i 390 och 1440 px (scrolla igenom först så lazy-bilder och animationer laddas, eller tvinga fram slutläget). Titta på dem med Read-verktyget. Kontrollera horisontell overflow och trasiga bilder/länkar (404 på någon intern länk = fel). Rätta och upprepa tills det ser professionellt ut. Spara skärmdumparna i `/tmp/ucshots/vNN/`.
4. Committa INTE och pusha INTE — huvudsessionen gör det.

## Svara med
Max 8 rader per tema: namn på temat, typsnitt/palett, vad som är speciellt (layout, animationer), och allt som inte blev bra.
