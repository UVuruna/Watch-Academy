"""UI text catalog — translation Phase 2 (owner spec).

Every user-visible CHROME string lives here once: menu items, dialog
labels, tray balloons, hover-legend labels and the name tables. The
ENGLISH string itself is the key — the corpus entry is `ui/<text>`
(data/translations.py) and `ui(overlay, text)` returns the active
language's version, English being the shipped source. Protected brand
terms (DOMY, Trinity/Seasons/Prism/Compass, Paint/Light, Umbra, Aura,
Flame/Chalice/Seal…) stay English inside translated sentences.
"""


def ui(overlay: dict, text: str) -> str:
    """The active language's form of a catalog string ({}-placeholders
    intact — the caller formats); English is the fallback source."""
    return overlay.get(f"ui/{text}", text)


UI_STRINGS: tuple[str, ...] = (
    # --- Menu -----------------------------------------------------------------
    "Design", "Hands",
    "Pointer", "Umbra", "Ring", "Earth", "Weekday",
    # Menu rework (owner 2026-07-13): the two slots at the top level,
    # the Weekday kinship groups.
    "Ancient Gods", "Society", "Arcana", "Image",
    "Size", "Elements", "Legend", "Solar rotation",
    "Settings…", "Time Travel…", "Encyclopedia…", "Guide…",
    "Click-through", "Exit",
    "Encyclopedia", "Astrology", "Chinese zodiac", "← Back",
    "Gods", "Zodiac", "Themes", "Creeds & Mysteries",
    "Fine (16 shades)", "Coarse (13 shades)", "Gradient",
    "Full contrast", "Half contrast", "Light contrast", "Dark contrast",
    "Paint palette", "Light palette",
    # Wheel-pair naming refinements (owner 2026-07-17, ROADMAP 15e): the
    # Seasons pair is Temperaments/Elements, Aurora's own pair is Warm/Cool.
    "Temperaments", "Warm", "Cool",
    # The Calendar pointer (owner 2026-07-16): the wheel pair riding
    # the Paint/Light slot, and its two lighting modes.
    "Calendar", "Almanac",
    "Light the hour (shichen)", "Light the month/sign",
    "Gold letters", "Silver letters",
    "Clean", "Atmosphere", "Date", "Names",
    "The day name written on the weekday bodies.",
    "Moon — below horizon",
    "Planets", "Planet signs", "Greek gods", "Norse gods", "Egyptian gods",
    "Slavic gods", "Alchemy", "Japanese week", "Creeds", "Mysteries",
    "Professions",
    # The theme METALS (bronze-plate themes + the ring finish menu).
    "Gold", "Bronze", "Silver", "Bronze letters", "Follow ring color",
    "Day length",
    # South slot style dropdowns (owner 2026-07-12): Astrology, the
    # Ascendant (the rising sign right now) and the Chinese zodiac
    # open their own submenus.
    "Sign", "Logo", "Constellation", "Text", "Colored", "Ascendant",
    "Moon", "Colorful", "Seconds",
    # Menu tooltips
    "The date written on the Earth marker (shown from {size} px up).",
    "The Earth marker riding the year wheel and showing the date.",
    "The Moon marker riding its cycle and showing the phase.",
    "The weekday bodies — the rotating slots and the center.",
    "The star diamonds. Off: the Aura colors stay, only the pointer disappears.",
    "The Aura palette hues. Off: the day and twilight arcs are drawn as plain white transparency.",
    "The seconds hand. Off: it is not drawn and the dial ticks once per minute.",
    "The information display. On the Compass and the Seasons "
    "it lives in the center (the 24h arm belongs to the "
    "Sunday pair); with the pointer off it sits at the dial "
    "bottom — alone at the center, or at 21h beside the day "
    "slot at 3h.",
    "All hover texts. Off: the dial shows nothing on hover — combined with Click-through it has zero interaction.",
    "On: the star points at true solar noon. Off: Star, Aura and Umbra stand upright (12/24 at the top) for reading exact planet and season positions.",
    "The dial takes no clicks at all (they pass to the desktop); hover info still works. Turn it back off here in the tray.",
    # THE ARCHETYPE MODE (owner sealed package 2026-07-16) — the
    # toggle pair beside Solar rotation and the hover pending line
    # (new strings ship untranslated; the pre-build Translation
    # session covers them).
    "Archetype", "Earth weekday",
    "The diamonds carry the active wheel's archetype "
    "figures; the hour hand lights the one whose "
    "hour-space it is in. The weekday model and the slots "
    "step aside while it runs.",
    "The abbreviated day (TUE, THU…) written under the "
    "Earth marker's date while the Archetype mode runs.",
    "The Canon has already named this seat; its article is still "
    "being written.",
    # --- Settings dialog --------------------------------------------------------
    "Location", "Opacity", "Element sizes", "Custom ring", "Language",
    # The custom diameter slider (owner 2026-07-17, ROADMAP 15e).
    "Diameter",
    "Palette — {pointer} {style}",
    "Clock tint — dial, hands and Umbra (letters excluded)",
    "Custom hands", "Hours", "Minutes", "Seconds", "Browse…",
    "Add hands", "Pivot X", "Pivot Y", "center",
    "Z-order (bottom → top)",
    "Rotation center from the LEFT edge in pixels of your image — leave 'center' for symmetric hands.",
    "Rotation center ABOVE the image bottom in pixels — the hand must point UP.",
    "PNG images pointing UP. Colored art grays out so the clock tint can recolor it; the tip-to-pivot length sets every size automatically.",
    "{n} hand set(s) saved",
    "Added '{name}' — find it under Design ▸ Hands",
    "Search", "City name…", "Continent", "Subregion", "Country", "Region",
    "City", "Latitude", "Longitude", "Timezone",
    "not found", "{n} found",
    "Star", "Aura — sunlight", "Aura — twilight", "Skin default", "Default",
    "Ring letters", "Hover enlarge",
    "Reset to preset", "Custom…", "Gray (default)", "the untouched art",
    "Unique name", "Add ring", "{n} custom ring(s) saved",
    "Added '{name}' — OK saves it; find it under Design ▸ Ring",
    "Flame — Masculine ({n} letters)", "Chalice — Feminine ({n} letters)",
    "Seal — Union ({n} letters)",
    "Latin", "Greek", "Numbers", "Symbols",
    "Top", "Top Right", "Bottom Right", "Bottom", "Bottom Left", "Top Left",
    "Right", "Left",
    "North", "North-East", "East", "South-East",
    "South", "South-West", "West", "North-West",
    # Aurora palette chips speak in day phases (Dawn/Dusk are above).
    "Morning", "Forenoon", "Noon", "Afternoon", "Evening",
    "{name} — original",
    "Theme rotation", "Every", "minutes", "hours",
    "System", "Start with Windows",
    "Back to English — the shipped original texts",
    "The originals above the line ship inside the app. Any other language translates itself in the background on first pick (internet needed once) and then works offline.",
    # Ring tint color names (tooltips) + the two group labels (owner
    # 2026-07-15: the palette split into Lighter and Darker).
    "Lighter", "Darker",
    "Gray", "Gold", "Silver", "Copper", "Purple", "Ocean",
    "Naples Yellow", "Sunglow", "Mikado Yellow", "Satin Gold", "Golden Brown",
    "Charcoal", "Glaucous", "Slate Gray", "Black Coral", "Steel",
    "Roman Silver", "Cadet Gray", "Deep Pine", "Sage Steel", "Smoke",
    "Ebony", "Smoky Plum", "Periwinkle", "Lavender Gray", "Espresso",
    "Anthracite", "Granite", "Dim Gray", "Stone", "Nevada", "Aluminium",
    # The FIGURE ROSTER (owner 2026-07-15) + the Pantheon names, the
    # reworked Creeds and the wolf rank parentheticals.
    "Figures", "Planetary", "Pantheon", "Ancient religions",
    "Poseidon (Ποσειδῶν)",
    "Artemis (Ἄρτεμις)",
    "Athena (Ἀθηνᾶ)",
    "Apollo (Ἀπόλλων)",
    "Hera (Ἥρα)",
    "Demeter (Δημήτηρ)",
    "Hel", "Frigg", "Freyr", "Isis", "Horus", "Anubis", "Bastet",
    "Svarog", "Lada", "Hades", "The Wanderer",
    "Gaia", "Yggdrasil", "Triglav", "The Pharaoh", "The Polymath",
    "The Holy Trinity", "The Ninth Circle",
    "Eleusinian Mysteries", "Satanism",
    "Leader (Alpha) · Omega", "Hunter (Gamma)", "Scout (Delta)",
    # The fashion darks (owner 2026-07-15: subtle wardrobe hues).
    "Pewter", "Iron", "Graphite", "Gunmetal", "Petrol", "Navy",
    "Oxford Blue", "Dark Olive", "Aubergine", "Bordeaux",
    # --- Time Travel / Guide ----------------------------------------------------
    "Moment:", "Latitude:", "Longitude:",
    "The dial shows this situation for {n} seconds, then returns to the present.",
    "← Previous", "Next →",
    # The Encyclopedia reader chrome (owner 2026-07-14: Home top-left,
    # Download saves the open entry's image and text).
    "Home", "Download",
    # The art-source pick (owner 2026-07-14: Gemini vs ChatGPT).
    "Artwork",
    # The hidden-mode unlock balloon (owner 2026-07-14).
    "Hidden mode unlocked",
    "The Four Greetings await in the Encyclopedia — Trinity and Seasons.",
    # Time Travel quick jumps (owner 2026-07-14; round two shortened
    # the turning points to arrow labels built from Sun/Moon).
    "Quick Jump",
    "North Pole", "South Pole", "Greenwich",
    # DEEP TIME (Session 16, owner 2026-07-17): the reworked Quick
    # Jump tree, the BCE moment editor, the coverage/precision lines
    # and the year-line Settings group. English ships; the SR bundle
    # catches up in the TRANSLATION session (owner policy 2026-07-16).
    "Eclipse", "Year", "Month", "Day", "Century", "Millennium",
    "Location",
    "Needs the Deep Time data pack (full installation).",
    "CE", "BCE", "AD", "BC",
    "Coverage: {first} … {last}",
    "Precision: minute-exact (core years {first}–{last}).",
    "Precision: events exact; the local clock drifts ±hours at the "
    "far extremes (ΔT).",
    "Precision: beyond the data — only era lengths are known "
    "(Laskar), no dates.",
    "Time Travel covers {span} — beyond the Deep Time span only era "
    "lengths are known (Laskar), no exact dates.",
    "Time Travel covers {span} for now — the Deep Time data pack "
    "extends it to {deep_first}…{deep_last} (not installed).",
    "Quick Jump cities", "Add", "Cities", "Remove selected",
    "Each city appears in Quick Jump ▸ Location and moves the "
    "observer there — the traveled moment stays.",
    "Calendar eras", "Era labels", "Third calendar",
    "Write the era after positive years too (2026 CE)",
    "Years in legends read as official · Anno Lucis (A.L. = CE + "
    "4079, the measured light era) — the third calendar joins that "
    "line.",
    "Ab Urbe Condita (Rome)", "Byzantine Anno Mundi",
    "Hebrew Anno Mundi", "Anno Hegirae (Islamic)",
    "Year starts 1 September (5509 BCE epoch).",
    "Year starts at Tishri (autumn); civil convention CE + 3760.",
    "Lunar years — displayed via the AH ≈ (CE − 622) × 33/32 "
    "approximation; exact AH needs lunisolar math.",
    # NOW (owner 2026-07-15): back to the present — in the Quick Jump
    # menu and as the Time Travel dialog's left button.
    "Now", "OK", "Cancel",
    "Back to the present — the simulation ends immediately.",
    # The hidden REPORT (owner 2026-07-15): function efficiency
    # statistics behind the session unlock.
    "Report", "Function", "Calls", "Average", "Min", "Max", "Total",
    "Last", "Reset", "Close",
    "Top functions by total time",
    "No measurements yet — use the clock a little.",
    "Select a row to watch its recent durations.",
    # The unified SLOT size slider and the rotation-group dropdown
    # (owner 2026-07-14).
    "Slot", "None", "Custom",
    # The 1st/2nd/3rd Slot system (owner 2026-07-14): superscript
    # labels, the Complications dropdown and the per-slot Enable.
    "1ˢᵗ Slot", "2ⁿᵈ Slot", "3ʳᵈ Slot",
    "Complications", "Digital Time", "Enable",
    "The slots enable in order — 1st, then 2nd, then 3rd.",
    # The complication PLATE styles (owner A/B spec 2026-07-15).
    "Theme background", "Classic black",
    "Settings", "Time Travel", "Guide",
    # --- Tray balloons / error boxes ---------------------------------------------
    "Translating",
    "Preparing {language} — the clock keeps running; texts switch when ready.",
    "Translation incomplete",
    "{error} — finished parts are shown; pick the language again in Settings to resume.",
    "Translation ready", "{language} is active.",
    "Settings could not be saved",
    # --- Hover legend labels (the compositor) --------------------------------------
    "Sunrise", "Sunset", "Dawn", "Dusk", "Night",
    # Owner formatting round 2026-07-12: bold labels and section titles.
    "Angle", "Season", "Phase", "Moonrise", "Moonset",
    "Morning Twilight", "Evening Twilight",
    "With Twilight", "Complete Dark",
    # Owner 2026-07-12 ("add that info somewhere, in a few words"):
    # the twilight band names its astronomical definition.
    "Civil twilight (Sun 6° below the horizon)",
    "Illumination",
    "Day {day} of {total}",
    "{ordinal} Day - {ordinal_week} Week",
    "{season} {ordinal} of {total} Days",
    "Heart:", "Meteorological {season}", "From", "To",
    # Owner formatting round 2026-07-13: the turning-point hover labels
    # its day length, the season blocks their span length.
    "Daylight", "Duration",
    "Wet season", "Dry season", "(1st half)", "(2nd half)",
    "Day", "Days", "Year", "{element} {animal}",
    # The ring tick-band hover + the Moon hover lunation (owner
    # 2026-07-12): which moon of the calendar year is running.
    "{ordinal} Moon of {year}",
    # --- Name tables ---------------------------------------------------------------
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday",
    "Sunday",
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
    "Jan", "Feb", "Mar", "Apr", "Jun", "Jul", "Aug", "Sep", "Oct",
    "Nov", "Dec",
    "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
    "Full Moon", "Waning Gibbous", "Third Quarter", "Waning Crescent",
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
    "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    "Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat",
    "Monkey", "Rooster", "Dog", "Pig",
    "Wood", "Fire", "Water", "Metal",
    # The Tetramorph three-side hover columns (owner 2026-07-17): the
    # creature + the evangelist + the element (Fire/Water above, Earth in
    # the menu, Air new).
    "Air", "The Evangelist", "The Element",
    # The Earth label quartet (owner 2026-07-18, ROADMAP 15h): "Date &
    # Weekday" is the OLD combined "Full Date" meaning, renamed now that
    # a true Full Date (date + year) exists below.
    "Date & Weekday", "Full Date",
    "Summer", "Autumn", "Winter", "Spring",
    "Summer Solstice", "Winter Solstice", "Spring Equinox", "Autumn Equinox",
    "June Solstice", "December Solstice", "March Equinox", "September Equinox",
    "Faith", "Hope", "Love",
    # Encyclopedia expansion (owner 2026-07-13): the new groups/topics
    # and the cross-cure emblem names (Love already lives above).
    "The Clock", "The Week", "The Instrument", "The Inner Wheel",
    "Virtues", "Sins", "Moods",
    # The Judas–Lucifer scale (owner 2026-07-13).
    "The Two Triangles", "Lucifer", "Judas", "The Union",
    # The comparative wheel article leading the Moods topic (2026-07-14)
    # and the 8+1 event mood closing it.
    "The Wheel of Moods", "The Ninth Mood",
    # Look-arrow captions (owner 2026-07-13: kinship groups + the
    # astrology/planets look names; the metals live above already).
    "Canon", "Signs", "Logo & Constellation", "Animals", "Religions",
    # The Trinity topic title (coverage gap caught 2026-07-14 — the
    # gallery card showed raw English).
    "Trinity",
    # The animal societies (owner 2026-07-13): theme titles, the
    # encyclopedia group, the Seasons topic and every role name.
    "Wolf Pack", "Bee Hive", "Elephant Herd", "Animal Societies",
    "Seasons",
    # The text-wave themes (owner 2026-07-14): titles, the Scripture
    # group, the Planets Art option and every display/face name.
    "Bible", "Bible II", "Bible Dark", "Cosmos", "Scripture", "Art",
    "Ancient of Days · Son", "Ancient of Days", "Son", "Mary", "David",
    "Moses", "Solomon", "Adam & Eve", "Joseph",
    "Abraham · Isaac", "Abraham", "Isaac", "Jonah", "Samson", "Jacob",
    "Noah", "Ruth", "Job",
    "Lucifer · Judas", "Lilith", "Goliath", "The Serpent", "Herod",
    "Delilah", "Cain",
    "Sun · Black Hole", "Black Hole", "Nebula", "Supernova", "Pulsar",
    "Galaxy", "Binary Stars", "Comet",
    # The Inner Wheel dial themes' dual titles (single names above).
    "Justice · Humility", "Pride · Servility", "Glory · Awe",
    # The Ninth entries closing the topics (owner 8+1 doctrine).
    "Sigma", "The Swarm", "The Graveyard", "The Big Bang", "Hades",
    "Baldur", "Set", "Crnobog", "The Philosopher's Stone", "The Jester",
    "The Unknown God", "The Lost Mystery", "Melchizedek", "Legion",
    "The Cat", "Ophiuchus",
    # The Nine Intelligences topic.
    "The Nine Intelligences", "Bodily-Kinesthetic", "Interpersonal",
    "Linguistic", "Naturalist", "Logical-Mathematical", "Musical",
    "Existential", "Intrapersonal", "Spatial",
    # The article SUBHEAD vocabulary (owner 2026-07-14): the fixed
    # eight — [[Marker]] lines in the corpus render as bold headings.
    "The Figure", "The Plate", "On the Dial", "The Hour", "The Story",
    "The Lesson", "The Sky", "The Ninth",
    "Alpha · Omega", "Luna", "Hunter", "Scout", "Beta", "Mate", "Elder",
    "Alpha", "Omega",
    "Queen · Cleaner", "Nurse", "Guard", "Builder", "Drone", "Forager",
    "Queen", "Cleaner",
    "Matriarch · Memory", "Allomother", "Musth", "Caller", "Mentor",
    "Reunion", "Matriarch", "Memory",
    "Justice", "Humility", "Serenity", "Courage", "Wisdom",
    "Generosity", "Patience",
    "Pride", "Servility", "Fear", "Wrath", "Greed", "Excess",
    "Jealousy", "Envy",
    "Glory", "Awe", "Calm", "Zeal", "Sorrow", "Joy", "Passion",
    "Renewal",
    # Entity display names (weekday hover titles; planets reuse Sun…Saturn)
    "Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
    "Helios", "Selene", "Ares", "Hermes", "Zeus", "Aphrodite", "Cronus",
    "Sól", "Máni", "Tyr", "Odin", "Thor", "Freya", "Loki",
    "Ra", "Khonsu", "Montu", "Thoth", "Amun", "Hathor", "Osiris",
    "Christianity", "Buddhism", "Freemasonry", "Taoism", "Hinduism",
    "Islam", "Judaism",
    "Egypt", "Druidism", "Zoroastrianism", "Shamanism", "Sikhism",
    "Babylon", "Voodoo",
    "Ruler", "Ruler · Servant", "Physician", "Soldier", "Merchant",
    "Priest", "Artist", "Farmer",
    # --- The Observatory (Session 17, owner 2026-07-16) --------------------------
    # The statistics window chrome — dark charts over the long ephemeris
    # data. English ships; the pre-build Translation session localizes.
    "Observatory", "Observatory…", "A.L.",
    "Season durations", "The light − dark envelope", "Eclipse timeline",
    "Day length over the year",
    "light − dark", "light − dark (days)", "days", "day of year",
    "day length", "magnitude", "eclipses per bucket", "year",
    "Light", "Dark", "Solar", "Lunar", "now",
    "Anno Lucis", "Age of Darkness", "light peak", "dark peak",
    "Nearest solar and lunar eclipses around the moment "
    "(exact instants from the full installation).",
    "Eclipse density over the span — {solar}/{lunar} per century "
    "(solar/lunar). Install the full pack for exact instants.",
)
