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
    "Primary Slot", "Secondary Slot",
    "Ancient Gods", "Society", "Arcana", "Image",
    "Size", "Elements", "Legend", "Solar rotation",
    "Settings…", "Time Travel…", "Encyclopedia…", "Guide…",
    "Click-through", "Exit",
    "Encyclopedia", "Astrology", "Chinese zodiac", "← Back",
    "Gods", "Zodiac", "Themes", "Creeds & Mysteries",
    "Fine (16 shades)", "Coarse (13 shades)", "Gradient",
    "Full contrast", "Half contrast", "Light contrast", "Dark contrast",
    "Paint palette", "Light palette",
    "Gold letters", "Silver letters",
    "Clean", "Atmosphere", "Date", "Names",
    "The day name written on the weekday bodies.",
    "Moon — below horizon",
    "Planets", "Planet signs", "Greek gods", "Norse gods", "Egyptian gods",
    "Slavic gods", "Alchemy", "Japanese week", "Creeds", "Mysteries",
    "Professions",
    # The theme METALS (bronze-plate themes + the ring finish menu).
    "Gold", "Bronze", "Silver", "Bronze letters", "Follow ring color",
    "Time", "Day length",
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
    # --- Settings dialog --------------------------------------------------------
    "Location", "Opacity", "Element sizes", "Custom ring", "Language",
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
    # Ring tint color names (tooltips)
    "Gray", "Gold", "Silver", "Copper", "Purple", "Ocean",
    "Naples Yellow", "Sunglow", "Mikado Yellow", "Satin Gold", "Golden Brown",
    "Charcoal", "Glaucous", "Slate Gray", "Black Coral", "Steel",
    "Roman Silver", "Cadet Gray", "Deep Pine", "Sage Steel", "Smoke",
    "Ebony", "Smoky Plum", "Periwinkle", "Lavender Gray", "Espresso",
    "Anthracite", "Granite", "Dim Gray", "Stone", "Nevada", "Aluminium",
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
    "The Four Greetings await in the Encyclopedia — Trinity.",
    # Time Travel quick jumps (owner 2026-07-14; round two shortened
    # the turning points to arrow labels built from Sun/Moon).
    "Quick Jump",
    "North Pole", "South Pole", "Greenwich",
    # The unified SLOT size slider and the rotation-group dropdown
    # (owner 2026-07-14).
    "Slot", "None", "Custom",
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
)
