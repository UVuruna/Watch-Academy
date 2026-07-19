# SVG ikonice — spisak i uputstvo (za vlasnika)

> NOTE (EN, for agents): This file is OWNER-FACING generation
> instructions, written in Serbian by the owner's explicit order
> (2026-07-19) — an approved exception to the English-only rule.
> Agents read the file list and drop paths; the prose is for the owner.

Ovde je spisak malih ikonica koje nam trebaju tamo gde EMOJI nije
adekvatan (ili se sudara sa već upotrebljenim sunce/mesec znacima).
Radiš ih kad kažeš — ovo je samo spreman spisak, kao što su spremne
i instrukcije za GUIDE screenshotove.

## Format (važi za sve)

- **SVG, vektorski, monohromatski** — linija (stroke) stil, bez
  ispune gde ne mora; boja = `currentColor` da nasledi temu
  (zlatni akcenat / beli tekst, zavisno gde stoji).
- **ViewBox 24×24**, stroke ~1.5–2 px, zaobljeni krajevi — da se
  slaže sa modernom temom dijaloga.
- **Bez teksta i brojeva u ikonici.**
- Spusti u: `assets/icons/<ime>.svg` (tačna imena iz tabele).
- Aplikacija degradira elegantno: dok ikonice nema, stoji privremeni
  emoji/znak — svaka koju spustiš samo „legne".

## Spisak

| # | Fajl | Predstavlja | Gde se koristi | Ideja motiva (slobodno menjaj) |
|---|------|-------------|----------------|-------------------------------|
| 1 | `light.svg` | SVETLO (polarni dan) | polovi u Location meniju (desna strana) | otvoreno oko; ili horizont sa zracima NAGORE (bez sunčevog diska) |
| 2 | `dark.svg` | MRAK (polarna noć) | polovi u Location meniju | zatvoreno oko; ili horizont sa zvezdama (bez meseca) |
| 3 | `eclipse_sun.svg` | pomračenje Sunca | Quick Jump ▸ Sun, hover kartica, enciklopedija Eclipses | disk preko diska, korona prsten |
| 4 | `eclipse_moon.svg` | pomračenje Meseca | Quick Jump ▸ Moon, hover kartica, enciklopedija Eclipses | disk u senci sa tankim rubom |
| 5 | `year.svg` | GODINA | Quick Jump ▸ Year · Month · Day | prsten sa 4 zareza (godišnja doba) |
| 6 | `month.svg` | MESEC (kalendarski) | isto | prsten sa 12 zareza |
| 7 | `day.svg` | DAN | isto | prsten sa jednim podeokom / jedna kućica kalendara |
| 8 | `century.svg` | VEK | Quick Jump ▸ Century · Millennium | stub sa C zarezima — rimski motiv bez slova |
| 9 | `millennium.svg` | MILENIJUM | isto | tri stuba / piramida |
| 10 | `now.svg` | SADA (povratak na sadašnjost) | Quick Jump ▸ Now | tačka u krugu (nišan) |
| 11 | `solstice.svg` | solsticij | Observatory oznake, hover prekretnica | vrh sinusoide sa tačkom |
| 12 | `equinox.svg` | ekvinocij | isto | presek sinusoide i linije (tačka ravnoteže) |
| 13 | `age_light.svg` | Doba Svetla (mini) | year-line / Earth kartica uz eru | uzlazna polovina talasa |
| 14 | `age_dark.svg` | Doba Tame (mini) | isto | silazna polovina talasa |

Ako u međuvremenu nađemo još mesta gde emoji škripi, dopisujemo u
ovu tabelu — jedna tabela, jedan folder, jedno pravilo.

## Prioritet

1–4 odmah rešavaju tvoje današnje primedbe (polovi + eklipse);
5–10 čiste Quick Jump; 11–14 su ukras, mogu poslednje.
