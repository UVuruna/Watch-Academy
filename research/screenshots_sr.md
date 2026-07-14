Owner-facing checklist, in Serbian by explicit request (2026-07-14).

# Spisak screenshotova

Ovo je kompletna, obeležljiva (checkbox) lista svih snimaka ekrana koje
vlasnik treba da napravi za DOMY Watch — 5 za Encyclopedia poglavlje
"The Instrument" i 37 za redizajnirani Guide. Sve se snima na živoj
aplikaciji (desni klik na numeračnik ili na tray ikonicu otvara isti
meni), po pravilu na podrazumevanim (baseline) podešavanjima osim gde
je drugačije naznačeno u koloni pripreme.

Gde fajlovi idu:
- **Guide** slike (37 komada) prepisuju/dodaju postojeća imena u
  `assets/guide/` — nastavljaju flat `NN_opis.png` konvenciju već
  korišćenu za fajlove 01-53.
- **Instrument** slike (5 komada) idu direktno na navedene putanje
  (od 2026-07-14 stablo ima sloj izvora — podrazumevani je `gemini/`):
  `assets/instrument/gemini/dial.png`, `solar_rotation.png`,
  `twilight.png`, `year_wheel.png`, `moon_lunations.png`.
- Format/rezolucija: snimati u prirodnoj veličini piksela aplikacije —
  slike smeju biti i veće od 800×800 (to ograničenje važi samo za
  Gemini medaljone, ne za screenshotove).

Meni je od 2026-07-13 reorganizovan — svuda ispod koristi NOVU strukturu
gornjeg nivoa: **Design** (Pointer/Ring/Umbra | Hands/Earth | Size),
**Primary Slot**, **Secondary Slot**, **Elements** | **Legend**,
**Solar rotation**, **Click-through** | **Settings**, **Encyclopedia**,
**Guide**, **Time Travel** | **Exit**. Stari "Theme ▸ Day slot/Info
slot" sada je **Primary Slot**/**Secondary Slot** direktno na gornjem
nivou; stari "Theme ▸ Earth" sada je **Design ▸ Earth**; teme
"Religions"/"Religions II" sada se zovu **Creeds**/**Mysteries**.

Weekday podmeni od tekst-talasa (2026-07-14) drži **21 temu u šest
grupa srodstva** (potvrđeno u kodu): **Ancient Gods** (Egyptian, Greek,
Norse, Slavic), **Society** (Professions, Creeds, Mysteries),
**Scripture** (Bible, Bible II, Bible Dark), **Animals** (Wolf Pack,
Elephant Herd, Bee Hive), **The Inner Wheel** (Virtues, Sins, Moods),
**Arcana** (Planets sa Image/Sign/Art, Alchemy, Japanese week, Cosmos).
Metal pod-podmeni (Gold/Bronze/Silver/Colored) postoji kod SEDAM tema:
Greek, Norse, Professions, Wolf Pack, Bee Hive, Elephant Herd, Cosmos.

---

## Instrument (5 kadrova)

- [ ] dial.png — Bilo koji pointer, Time Travel nije potreban; snimak A: ceo krug u trenutku kad je satna kazaljka jasno između podneva i ponoći (pre- ili posle-podne) da njen ugao od 15°/h izgleda vidljivo drugačije od minutne kazaljke — Ceo krug numeračnika u kadru; opciono dodaj i snimak B, blizak kadar oboda od 10h do 14h, da se u istom fajlu/setu vidi hijerarhija crtica (najsjajnija strelica na 12h, obične bele na neparnim satima, sive na parnim, fina minutna podela između).

- [ ] solar_rotation.png — Grad = Beograd; Time Travel na po jedan datum sa svake strane DST prelaska (npr. oko poslednje nedelje marta i poslednje nedelje oktobra) — Uhvati ceo krug oba puta tako da se vidi nagib heksagrama naspram uspravne 12h/24h crtice (nagib ide od −4.17° do +10.76°); ako je nagib presitan na celom krugu, dozvoljen je bliži kadar samo na zvezdu i 12h/24h crticu.

- [ ] twilight.png — Snimak A: grad = Beograd (ili maketni dan 20.6.2025 — izlazak 04:52 / zalazak 20:27); snimak B: grad = Tromsø, oko 21. juna — Ceo krug oba puta: u snimku A treba da se vide oba pojasa (plavi civilni sumrak oko 06h, braon oko 18h); u snimku B pojas mora biti očigledno mnogo širi od običnog ~9° luka iz snimka A (bele noći/produženi sumrak režim).

- [ ] year_wheel.png — Pointer = Seasons (cross); Time Travel na solsticij ili ekvinocij blizu lokalnog podneva (npr. 21. jun za letnji solsticij ili 23. septembar za jesenji ekvinocij) — Ceo krug u kadru, marker vidljivo tačno na kardinalnoj tački (vrh/dno za solsticije, levi/desni ugao za ekvinocije); uključi hover/legend popup na markeru ako je moguć.

- [ ] moon_lunations.png — Pointer = Seasons; Time Travel na datum blizu punog meseca, ili na zlatni test-datum 2026-07-07 (osvetljenost meseca 0.7400, rastući grbavi mesec) — Ceo krug sa vidljivim sjajem mesečevog markera na točku; po mogućstvu sa hover popup-om (redni broj lunacije + % osvetljenosti + naziv faze + dan ciklusa).

---

## Guide (37 kadrova)

- [ ] 54 — 54_menu_top_level.png — Desni klik bilo gde unutar kruga numeračnika; baseline, ne otvarati nijedan podmeni — Ceo meni gornjeg nivoa: Design, Primary Slot, Secondary Slot, Elements, Legend, Solar rotation, Click-through, Settings…, Encyclopedia…, Guide…, Time Travel…, Exit — plus dovoljno numeračnika iza menija da se vidi da je desni klik baš na DOMY Watch.

- [ ] 55 — 55_tray_menu.png — Desni klik na tray ikonicu u Windows sistemskoj traci; baseline — Sama tray ikonica plus identičan meni gornjeg nivoa kao na 54, da se vizuelno potvrdi da je isto stablo svuda.

- [ ] 56 — 56_tick_anatomy.png — Bez menija, samo blizak kadar oboda prstena; baseline, iseci obod otprilike od 10h do 14h (centrirano na pravo solarno podne na vrhu) — Bar dve podebljane bele crtice na neparnim satima (11h, 13h) sa obe strane jedinstvene strelice na 12h/podnevu, bar po jedna kratka siva crtica na parnim satima (10h ili 14h) na svakom kraju, i fina lestvica srednjih/tankih crtica između — sve četiri hijerarhije u jednom kadru.

- [ ] 57 — 57_tick_hover.png — Prevuci miš direktno preko jedne strelice u pojasu crtica (ne preko broja sata ili slova); baseline, bilo koja strelica van 12h/0h daje najbolji (netrivijalan) prikaz — Prevučena strelica plus popup sa Day/Year/Moon očitavanjem: Vreme + Ugao + naziv perioda; Datum + događaj/sezona + redni broj dana/nedelje; redni broj lunacije + % osvetljenosti + naziv faze + dan ciklusa.

- [ ] 58 — 58_pointer_aurora.png — Design ▸ Pointer ▸ Aurora; snimi blizu podneva da se vidi svih pet dnevnih nijansi na luku — Ceo krug: kazaljka bez krakova koja slika sam dan u pojasevima (zora/dan/suton), bez dijamanata, prsten vidljiv oko nje.

- [ ] 59 — 59_palette_aurora_paint.png — Design ▸ Pointer ▸ Aurora; Design ▸ Pointer ▸ Paint paleta (već podrazumevano) — Blizak kadar Aurora pojasa da se jasno vidi Paint sekvenca od 7 nijansi (azurna → zelena → žuta → narandžasta → crvena → tamnocrvena).

- [ ] 60 — 60_palette_aurora_light.png — Design ▸ Pointer ▸ Aurora; Design ▸ Pointer ▸ Light paleta — Isti kadar kao 59, ali Light sekvenca (azurna → cijan → zelena → žuta → crvena → tamnocrvena), za direktno poređenje paint-vs-light.

- [ ] 61 — 61_umbra_coarse.png — Design ▸ Umbra ▸ Coarse (13 nijansi); Design ▸ Umbra ▸ Full kontrast — Ceo krug, vidljivo grublji točak od 13 nijansi sive, pored postojeće Fine (16 nijansi) reference.

- [ ] 62 — 62_umbra_gradient_form.png — Design ▸ Umbra ▸ Gradient; Design ▸ Umbra ▸ Full kontrast — Ceo krug, potpuno neprekidan prelaz bez ijednog vidljivog stepenika.

- [ ] 63 — 63_ring_domy_bronze.png — Design ▸ Ring ▸ DOMY; Design ▸ Ring ▸ Bronze slova — Blizak kadar isti kao 22/23: trougao M/Y/D u bronzi, Omega u srebru (pravilo bronze finiša za akcenat).

- [ ] 64 — 64_ring_numbers_seal.png — Design ▸ Ring ▸ NUMBERS; snimi jednom u Gold finišu, a ako ima vremena i u Silver — jedan snimak je dovoljan za Guide, oba korisna za tekst — Blizak kadar celog prstena, svih šest pozicija (12/16/20/Ω/4/8) sa ciframa umesto slova, svih šest u ISTOM metalu (Seal-ovo pravilo jedan-metal-za-svih-šest).

- [ ] 65 — 65_menu_design_ring.png — Desni klik ▸ Design ▸ Ring, razvijeno ali ništa kliknuto; baseline, poželjno bar jedan sopstveni (custom) prsten već dodat kroz Settings da podmeni pokaže više od tri ugrađene kartice (opciono) — Podmeni Ring: DOMY / MORPH / NUMBERS (+ eventualne custom kartice) iznad separatora, Gold/Silver/Bronze slova ispod njega.

- [ ] 66 — 66_hands_classic.png — Design ▸ Hands ▸ CLASSIC — Blizak kadar centriran na osovinu, sve tri kap-oblik kazaljke jasno vidljive u čitljivom trenutku (npr. ekvivalent ~10:10 na 24h numeračniku) da se vidi razlika u dužinama.

- [ ] 67 — 67_hands_steel.png — Design ▸ Hands ▸ STEEL (već podrazumevano) — Isti kadar i isto vreme kao 66, za direktno poređenje.

- [ ] 68 — 68_menu_design_hands.png — Desni klik ▸ Design ▸ Hands, razvijeno; baseline, poželjno sa već dodatim custom paketom kazaljki kroz Settings da podmeni pokaže 3 stavke, ne 2 — Podmeni Hands: CLASSIC, STEEL (+ eventualni custom paketi), sa aktivnim paketom označenim.

- [ ] 69 — 69_menu_design_size.png — Desni klik ▸ Design ▸ Size, razvijeno; baseline — Svih pet preseta (360/540/720/1080/1440 px) sa 720 označenim kao aktivnim.

- [ ] 70 — 70_size_compare.png — Design ▸ Size, snimljeno tri puta: prečnik = 360, pa 720, pa 1440, isti pointer/tema/lokacija svaki put — Tri snimka celog kruga u pravoj relativnoj razmeri (ne menjati veličinu slika naknadno — snimiti u prirodnoj veličini piksela), poređani od najmanjeg ka najvećem.

- [ ] 71 — 71_menu_theme_earth.png — Desni klik ▸ Design ▸ Earth, razvijeno (Earth je od reorganizacije menija preseljen iz Theme u Design); baseline — Grupa Clean / Atmosphere (radio dugmad), separator, i checkbox Date ispod njega (u tekstu napomenuti da se Date zasivi ispod 540 px).

- [ ] 72 — 72_earth_clean_vs_atmo.png — Design ▸ Earth ▸ Clean, zatim Design ▸ Earth ▸ Atmosphere (već podrazumevano); dva kadra, menja se samo earth_style — Blizak kadar samo na Earth marker, ista sezona i ista dan/noć faza oba puta, da se vidi isključivo razlika u art-u clean-vs-atmosphere.

- [ ] 73 — 73_weekday_planet_signs.png — Primary Slot ▸ Weekday ▸ Arcana ▸ Planets ▸ Sign; tema Weekday = planet_signs — Ceo krug (2-kolonski grid kadar isti kao postojeći 24-28), sedam medaljona sa planetarnim simbolima na kracima.

- [ ] 74 — 74_weekday_egypt.png — Primary Slot ▸ Weekday ▸ Ancient Gods ▸ Egyptian gods; tema Weekday = egypt — Isti kadar kao 73; Ra/Khonsu/Montu/Thoth/Amun/Hathor/Osiris vidljivi.

- [ ] 75 — 75_weekday_slavic.png — Primary Slot ▸ Weekday ▸ Ancient Gods ▸ Slavic gods; tema Weekday = slavic — Isti kadar; Dažbog/Hors/Svetovid/Veles/Perun/Mokoš/Morana vidljivi.

- [ ] 76 — 76_weekday_alchemy.png — Primary Slot ▸ Weekday ▸ Arcana ▸ Alchemy; tema Weekday = alchemy — Isti kadar; sedam metalnih mrtvih priroda (Gold/Silver/Iron/Quicksilver/Tin/Copper/Lead) vidljivo.

- [ ] 77 — 77_weekday_japan.png — Primary Slot ▸ Weekday ▸ Arcana ▸ Japanese week; tema Weekday = japan — Isti kadar; sedam yōbi medaljona sa kanji oznakama vidljivo.

- [ ] 78 — 78_weekday_religion_alt.png — Primary Slot ▸ Weekday ▸ Society ▸ Mysteries; tema Weekday = religion_alt — Isti kadar; Mithraism/Druidism/Zoroastrianism/Shamanism/Sikhism/Babylon/Voodoo vidljivo.

- [ ] 79 — 79_weekday_greek_colored.png — Primary Slot ▸ Weekday ▸ Ancient Gods ▸ Greek gods ▸ Colored; tema Weekday = greek, metal = colored — Isti kadar kao postojeći 25_weekday_greek, da se može direktno uporediti bronzana ploča i ovaj pun-kolor art.

- [ ] 80 — 80_menu_theme_weekday_metal.png — Desni klik ▸ Primary Slot ▸ Weekday ▸ Ancient Gods ▸ Greek gods, razvijeno (metal-teme otvaraju svoj pod-podmeni); baseline — Grupa Gold / Bronze / Silver / Colored ugnježdena ispod Greek gods, da se pokaže da ovaj pod-podmeni postoji samo kod sedam tema sa metalima (Greek, Norse, Professions, Wolf Pack, Bee Hive, Elephant Herd, Cosmos) — ostale teme se aktiviraju jednim klikom.

- [ ] 81 — 81_slot_ascendant.png — Primary Slot ▸ Ascendant ▸ Sign — režim Primary Slot = ascendant, stil = sign — Bedž na poziciji Primary Slot-a sa vidljivo drugačijim znakom nego što bi datum ili Secondary Slot sugerisali — poenta da se Ascendant menja otprilike na svaka dva sata, nezavisno od kalendara.

- [ ] 82 — 82_menu_theme_slots_day.png — Desni klik ▸ Primary Slot, razvijeno (Astrology i Chinese zodiac kao ugnježdeni podmeniji, ne razvijati dalje); baseline — Weekday / Time / Date / Day length / Astrology / Ascendant / Chinese zodiac kao stavke Primary Slot podmenija (Weekday sadrži 21 temu u šest grupa srodstva + Names; tri tekstualna moda zasive dok je Pointer element uključen).

- [ ] 83 — 83_slot_info_time.png — Design ▸ Pointer ▸ Compass (potrebno da bi Secondary Slot uvek bio dostupan); Secondary Slot ▸ Time (već podrazumevani mod) — pointer = Compass (octa), sve ostalo baseline — Ceo krug, digitalno vreme čitljivo u rezervisanom donjem kraku Compass-a.

- [ ] 84 — 84_slot_info_paired_weekday.png — Design ▸ Pointer ▸ Aurora; Elements ▸ Primary Slot uključeno; Elements ▸ Secondary Slot uključeno; Primary Slot ▸ Weekday ▸ Ancient Gods ▸ Norse gods; Secondary Slot ▸ Weekday ▸ Ancient Gods ▸ Greek gods — pointer = Aurora, Primary Slot tema = norse, Secondary Slot mod = weekday sa temom = greek; oba bedža moraju biti uključena istovremeno — Oba donja bedža jedan pored drugog: današnji nordijski bog na jednoj strani, današnji grčki bog na drugoj — da se pokaže da oba slota mogu voditi potpuno nezavisnu temu.

- [ ] 85 — 85_menu_theme_slots_info.png — Desni klik ▸ Secondary Slot, razvijeno (Weekday/Astrology/Ascendant/Chinese zodiac kao ugnježdeni podmeniji, ne razvijati dalje); baseline — Weekday / Time / Date / Day length / Astrology / Ascendant / Chinese zodiac kao stavke Secondary Slot podmenija — ISTOG oblika kao Primary Slot-ov.

- [ ] 86 — 86_colorful_on_off.png — Elements ▸ Colorful, isključeno za drugu polovinu; dva kadra: Colorful uključeno (baseline) i isključeno — Isti region dnevnog/sumračnog luka oba puta — obojene nijanse u jednom, obična bela providnost u drugom.

- [ ] 87 — 87_solar_rotation_off.png — Desni klik ▸ Solar rotation, isključeno (unchecked); snimi u trenutku kad je pravo solarno podne vidljivo pomereno od 12 na podrazumevanoj lokaciji (bilo koji ne-ekvinocijalni-podnevni trenutak u Beogradu radi) — Ceo krug uspravan — 12 i 24 tačno na vrhu i dnu, bez nagiba na zvezdi, Aurori ili Umbri.

- [ ] 88 — 88_tray_click_through.png — Desni klik ▸ Click-through, uključeno (checked); zatim desni klik na TRAY ikonicu (numeračnik više ne prima klikove) — Click-through = on — Tray meni sa vidljivo štiklovanim Click-through, jasno pokazujući da je tray jedini put nazad iz ovog moda.

- [ ] 89 — 89_settings_theme_rotation.png — Settings… ▸ skroluj do "Theme rotation"; Enabled štiklovano, bar 4-5 checkbox-ova tema štiklovano (dovoljno da se vidi grid), "Every" postavljeno na čitljiv broj, bar jedan dropdown za metal teme vidljiv, Follow ring color isključeno da se tri metal-kombinacije prikažu kao omogućene — Cela grupa u kadru: Enabled checkbox, grid checkbox-ova tema, red Every N minuta/sati, dropdown-ovi metala po temi, Follow ring color checkbox.

- [ ] 90 — 90_settings_system.png — Settings… ▸ skroluj do "System" (dno dijaloga); baseline — Sam checkbox "Start with Windows".
