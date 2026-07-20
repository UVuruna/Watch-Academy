# GUIDE screenshotovi — spisak i uputstvo (za vlasnika)

> NOTE (EN, for agents): OWNER-FACING screenshot instructions in
> Serbian by the owner's explicit convention (like ICONS_SPISAK.md).
> The GUIDE rebuild session reads the file list; the prose is for the
> owner. Do not translate.

GUIDE dijalog postoji (11 starih strana iz jula), ali je aplikacija od
tada narasla — arhetipovi, Observatory, eklipse, Deep Time, novi meni,
metali… Stari screenshotovi su zastareli, novi featuri nemaju nijedan.
**Ovo je kompletan spisak snimaka za NOVI Guide** — radiš ih TEK kad
sve vizuelno legne (tvoje slike + poslednje runde), na svom monitoru,
na 720 px dial-u osim gde piše drugačije.

## Format (važi za sve)

- PNG, ceo relevantan region (sat + margina; za dijaloge ceo prozor).
- Bez dev okruženja u kadru (VSCode, terminali) — čista pozadina.
- Imena fajlova tačno iz tabele; spusti u `assets/guide/` (ravno).
- Gde piše „hover" — uhvati i TOOLTIP u kadru.
- Guide slaže 1–2 slike po strani sa naslovom i pasusom; tekstove
  pišem ja kad slike legnu — ti samo snimaš.

## Spisak snimaka

| # | Fajl | Šta se vidi | Kako da ga namestiš |
|---|------|-------------|---------------------|
| 1 | `dial_default.png` | podrazumevani sat (hexa paint, planete) | čist start, podne |
| 2 | `pointers_four.png` | 4 pointera uporedo (Trinity/Seasons/Prism/Compass) | 4 snimka pa složi, ili 4 fajla `pointer_<ime>.png` |
| 3 | `aurora_calendar.png` | Aurora i Calendar točkovi | isto — može 2 fajla |
| 4 | `archetype_prism.png` | Prizma arhetip sa NOVIM lancetima, centar-prozor upaljen | oko podneva, Archetype ON |
| 5 | `archetype_reveal.png` | Omega double-click — sve figure pune, bez kazaljki | double-click pa snimi u 60s |
| 6 | `tetramorph_hover.png` | tetramorf tri kolone (biće+jevanđelista+element) | Seasons light arhetip, hover na Lava |
| 7 | `weekday_metals.png` | ista tema u zlatu/bronzi/srebru | 3 fajla `metal_<boja>.png` |
| 8 | `earth_card.png` | nova Earth kartica (Date naslov, era emblem, sezona) | hover na Zemlju |
| 9 | `eclipse_solar.png` | solarna eklipsa na prstenu (crno sunce + crveni glow) | Time Travel → 2. avg 2027, 12:06 |
| 10 | `eclipse_lunar.png` | lunarna totalna (bakarni disk + bronza + tirkiz) | Time Travel → najbliža totalna lunarna (Quick Jump ▸ Moon) |
| 11 | `mason_g_motto.png` | Mason prsten sa moto lukovima | Design ▸ Ring ▸ Mason |
| 12 | `observatory_full.png` | Observatory svih 5 grafikona | 🔭 iz menija |
| 13 | `observatory_zoom.png` | zumiran grafikon sa godišnjim tickovima | zumiraj envelope na ~10 godina |
| 14 | `observatory_enlarge.png` | Enlarge preko celog ekrana sa legendom | Enlarge na Laskar grafikon |
| 15 | `encyclopedia_gallery.png` | galerija topika (sa novim grupama) | Enciklopedija početna |
| 16 | `encyclopedia_eclipse.png` | poglavlje eklipse sa emblemom | kad emblemi legnu |
| 17 | `settings_nav.png` | novi Settings (nav kolona + paneli) | Settings ▸ Colors sekcija |
| 18 | `time_travel.png` | Time Travel dijalog | otvoren, neki istorijski datum |
| 19 | `quick_jump.png` | Quick Jump meni sa polovima (❄/⚫) i Griničem 🌐 | tray meni raširen |
| 20 | `moon_phases_page.png` | Moon stranica sa ŽIVOM fazom | Enciklopedija ▸ Moon ▸ bilo koja faza |

Ako u međuvremenu dodamo feature — dopisujemo red; jedan fajl, jedna
tabela, kao i za ikonice.

## Status (2026-07-20)

Svih 20 snimaka snimljeno programski (Qt drajver na pravom hardveru,
720 px dial, podne 20.7.2026): dial kadrovi su PROVIDNI PNG-ovi
(alpha), hover karte i meniji screen-capture bez dev okruženja,
dijalozi ceo prozor. Umesto `aurora_calendar.png` — dva fajla
`pointer_Aurora/Calendar.png`; metali `metal_gold/bronze/silver.png`
(grčka tema). Eklipse: solarna 2.8.2027 12:06, lunarna totalna
31.12.2028 (bakar + tirkiz). Usput nađen i popravljen bug: `eclipse`
je falio u `ART_SOURCED_ROOTS` pa su emblemi poglavlja i hover
bedževi bili tiho odsutni. Novi `pages.json` + `captions.json`
složeni (14 strana, engleski tekstovi — SR tek u S15); starih 88
numerisanih slajdova iz jula penzionisano. Preostaje: tvoje čitanje
tekstova.

## Redosled

Snimaš JEDNOM, na kraju: posle tvog art talasa (era/eklipse/jevanđelisti/
centri/lanceti), SVG ikonica i mog poslednjeg vizuelnog prolaza — pa
odmah javljaš i ja slažem novi pages.json + tekstove, pa prevod, pa build.
