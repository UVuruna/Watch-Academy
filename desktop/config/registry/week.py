"""THE WEEK REGISTRY — the 6+3 kind.

Six weekday seats, then Sunday's three: the Ruler who holds the centre
by day, the Servant who holds it by night, and the Ninth who takes the
seat inside the solar half-hour windows. A theme with no Ninth runs
dual-only. 35 themes today.

**The shape of one entry.** Required: `title`, `art`, `articles`,
`blurbs`, `seats` (the six weekdays), `sunday`. Optional and meaningful
by their absence: `metals` (a full-colour theme wears none), `ninth`
(dual-only themes have none), `pantheon` (a second roster), and
`title_plate` (only where the register/look differs from
primary/colored).

    'norse': {
        "title": 'Norse gods', "art": 'norse/primary/bronze',
        "articles": 'norse', "blurbs": 'norse',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Mani', "stem": 'Mani'},
            ...
        },
        "sunday": {
            "name": 'Sol', "ruler": 'Sol', "servant": 'Skoll',
            "stem": 'Sol', "servant_plate": 'norse/primary/bronze/Skoll',
        },
        "ninth": {"name": 'Yggdrasil', "plate": '...'},
    }

**A seat is keyed by the ENGLISH DAY NAME** and carries its planetary
`body` as the seat's second name — both conventions are canon here
(owner 2026-08-04), so neither has to be translated in anyone's head.

**An occupant is always a LIST where it can rotate.** `rotates` names
the whole roster, canonical member first, and the declared order IS the
rotation order — load-bearing for the Power cast, whose Throne, Mirror
and Ninth each hold two members and must land on the same index on any
given day.

**DEPICTIONS ARE NOT THEMES** (owner decree 2026-08-04): several ways of
drawing the SAME figures in the SAME seats with the SAME text are one
theme wearing several looks. **The STORY decides** — the Gregorian and
the Slavic months hold identical spans and remain two themes, exactly as
the Greek and the Norse gods hold identical days and remain two.

**ONE FILE, DELIBERATELY** (owner ruling 2026-08-05). This module is a
DIRECTORY: thirty-five sibling entries of one kind, read by looking one
up, never by reading top to bottom. Splitting it across group files was
tried for a day and reverted — it made one subject live in eight places
and a reader chase imports to compare two themes. THE STRUCTURE LAW's
threshold was re-measured instead (`tests/test_structure_law.py`): it
counts LOGIC, and a declarative table is not logic. Long is not the
same as complex.

Layer: config — pure DATA. Nothing here imports anything but the
sentinel, which is what lets `constants` and `pantheon` both derive from
it without a cycle.
"""

from config.registry.sentinel import COMPUTED


# ═══════════════════════════ THE MENU ═══════════════════════════
# The picker's top entries and its kinship groups, in display order.
# A theme's group is DERIVED from this table and declared nowhere else.
MENU_TOP = ('planets',)

MENU = (
    ('Ancient Gods', ('egypt', 'greek', 'norse', 'slavic', 'age_of_heroes', 'celestial_court')),
    ('Society', ('profession', 'corporate', 'religion', 'religion_alt')),
    ('Scripture', ('bible', 'bible2', 'bible_dark')),
    ('Gaming', ('wow_alliance', 'wow_horde', 'wow_evil', 'cp_gangs', 'cp_street', 'cp_corpo')),
    ('Films', ('sw_jedi', 'sw_sith', 'sw_dyad')),
    ('Animals', ('wolf', 'elephant', 'bee')),
    ('The Inner Wheel', ('virtues', 'sins', 'moods')),
    ('Arcana', ('alchemy', 'japan', 'cosmos', 'continents')),
)

# ═══════════════════════════ THE THEMES ═══════════════════════════
# key -> the whole contract, in the dial's own registration order
# (what `constants.WEEKDAY_THEMES` has always been). The picker's
# grouping is a display decision and lives in MENU above.
WEEK = {
    'planets': {
        "title": 'Planets',
        "art": None,
        "articles": 'planets',
        "blurbs": 'day',
        "seats": {
            'monday': {"body": 'moon', "name": None, "stem": None},
            'tuesday': {"body": 'mars', "name": None, "stem": None},
            'wednesday': {"body": 'mercury', "name": None, "stem": None},
            'thursday': {"body": 'jupiter', "name": None, "stem": None},
            'friday': {"body": 'venus', "name": None, "stem": None},
            'saturday': {"body": 'saturn', "name": None, "stem": None},
        },
        "sunday": {
            "name": None,
            "ruler": 'Sun', "servant": 'Eclipsed Sun',
            "stem": None, "servant_plate": 'planets/primary/photo/Sun_Eclipse',
        },
        "title_plate": ('primary', 'photo'),
    },
    # The owner's planet GLYPHS (☿ ♃ …) — same entities as "planets",
    # body-named files, planet display names.
    'planet_signs': {
        "title": 'Planet signs',
        "art": 'planets/primary/sign',
        "articles": 'planets',
        "blurbs": 'day',
        "seats": {
            'monday': {"body": 'moon', "name": 'Moon', "stem": 'Moon'},
            'tuesday': {"body": 'mars', "name": 'Mars', "stem": 'Mars'},
            'wednesday': {"body": 'mercury', "name": 'Mercury', "stem": 'Mercury'},
            'thursday': {"body": 'jupiter', "name": 'Jupiter', "stem": 'Jupiter'},
            'friday': {"body": 'venus', "name": 'Venus', "stem": 'Venus'},
            'saturday': {"body": 'saturn', "name": 'Saturn', "stem": 'Saturn'},
        },
        "sunday": {
            "name": 'Sun',
            "ruler": 'Sun', "servant": 'Eclipsed Sun',
            "stem": 'Sun', "servant_plate": 'planets/primary/sign/Sun_Eclipse',
        },
        "title_plate": ('primary', 'sign'),
    },
    # Display names carry the NATIVE script (owner 2026-07-12: "da
    # koristimo ta slova" — like the Japanese kanji and the Slavic
    # diacritics); the files keep plain ASCII stems via the explicit
    # overrides below.
    'greek': {
        "title": 'Greek gods',
        "art": 'greek/primary/bronze',
        "articles": 'greek',
        "blurbs": 'greek',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Selene (Σελήνη)', "stem": 'Selene'},
            'tuesday': {"body": 'mars', "name": 'Ares (Ἄρης)', "stem": 'Ares'},
            'wednesday': {"body": 'mercury', "name": 'Hermes (Ἑρμῆς)', "stem": 'Hermes'},
            'thursday': {"body": 'jupiter', "name": 'Zeus (Ζεύς)', "stem": 'Zeus'},
            'friday': {"body": 'venus', "name": 'Aphrodite (Ἀφροδίτη)', "stem": 'Aphrodite'},
            'saturday': {"body": 'saturn', "name": 'Cronus (Κρόνος)', "stem": 'Cronus'},
        },
        "sunday": {
            "name": 'Helios (Ἥλιος)',
            "ruler": 'Helios', "servant": 'Phaethon',
            "stem": 'Helios', "servant_plate": 'greek/primary/bronze/Phaethon',
        },
        "ninth": {
            "name": 'Gaia', "plate": 'greek/pantheon/bronze/Gaia.png',
        },
        "pantheon": {
            "articles": 'greek_pantheon',
            "dual_names": ('Zeus', 'Hades'),
            "dual": ('greek/pantheon/bronze/Hades',),
            "seats": {
                'sunday': (('greek/pantheon/bronze/Zeus', 'greek/primary/bronze/Zeus'), 'Zeus (Ζεύς)'),
                'monday': (('greek/pantheon/bronze/Poseidon',), 'Poseidon (Ποσειδῶν)'),
                'tuesday': (('greek/pantheon/bronze/Artemis',), 'Artemis (Ἄρτεμις)'),
                'wednesday': (('greek/pantheon/bronze/Athena',), 'Athena (Ἀθηνᾶ)'),
                'thursday': (('greek/pantheon/bronze/Apollo',), 'Apollo (Ἀπόλλων)'),
                'friday': (('greek/pantheon/bronze/Hera',), 'Hera (Ἥρα)'),
                'saturday': (('greek/pantheon/bronze/Demeter',), 'Demeter (Δημήτηρ)'),
            },
        },
    },
    'norse': {
        "title": 'Norse gods',
        "art": 'norse/primary/bronze',
        "articles": 'norse',
        "blurbs": 'norse',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Máni', "stem": 'Mani'},
            'tuesday': {"body": 'mars', "name": 'Tyr (Týr)', "stem": 'Tyr'},
            'wednesday': {"body": 'mercury', "name": 'Odin (Óðinn)', "stem": 'Odin'},
            'thursday': {"body": 'jupiter', "name": 'Thor (Þórr)', "stem": 'Thor'},
            'friday': {"body": 'venus', "name": 'Freya (Freyja)', "stem": 'Freya'},
            'saturday': {"body": 'saturn', "name": 'Loki', "stem": 'Loki'},
        },
        "sunday": {
            "name": 'Sól',
            "ruler": 'Sól', "servant": 'Skoll',
            "stem": 'Sol', "servant_plate": 'norse/primary/bronze/Skoll',
        },
        "ninth": {
            "name": 'Yggdrasil', "plate": 'norse/pantheon/bronze/Yggdrasil.png',
        },
        "pantheon": {
            "articles": 'norse_pantheon',
            "dual_names": ('Odin', 'The Wanderer'),
            "dual": ('norse/primary/bronze/Odin',),
            "seats": {
                'sunday': (('norse/pantheon/bronze/Odin',), 'Odin (Óðinn)'),
                'monday': (('norse/pantheon/bronze/Hel',), 'Hel'),
                'tuesday': (('norse/primary/bronze/Thor',), 'Thor (Þórr)'),
                'wednesday': (('norse/primary/bronze/Loki',), 'Loki'),
                'thursday': (('norse/primary/bronze/Tyr',), 'Tyr (Týr)'),
                'friday': (('norse/pantheon/bronze/Frigg',), 'Frigg'),
                'saturday': (('norse/pantheon/bronze/Freyr',), 'Freyr'),
            },
        },
    },
    # Egyptian gods (owner art 2026-07-11, per the approved mapping): Ra's
    # Sunday, Khonsu the moon-walker, Montu the war falcon, Thoth the
    # scribe on the messenger's day, Amun the king of gods, Hathor love
    # and beauty, Osiris — harvest, patience and rebirth on Saturn's day.
    'egypt': {
        "title": 'Egyptian gods',
        "art": 'egypt/primary/bronze',
        "articles": 'egypt',
        "blurbs": 'egypt',
        "seats": {
            'monday': {"body": 'moon', "name": 'Khonsu', "stem": 'Khonsu'},
            'tuesday': {"body": 'mars', "name": 'Montu', "stem": 'Montu'},
            'wednesday': {"body": 'mercury', "name": 'Thoth', "stem": 'Thoth'},
            'thursday': {"body": 'jupiter', "name": 'Amun', "stem": 'Amun'},
            'friday': {"body": 'venus', "name": 'Hathor', "stem": 'Hathor'},
            'saturday': {"body": 'saturn', "name": 'Osiris', "stem": 'Osiris'},
        },
        "sunday": {
            "name": 'Ra',
            "ruler": 'Ra', "servant": 'Afu-Ra',
            "stem": 'Ra', "servant_plate": 'egypt/primary/bronze/Afu_Ra',
        },
        "ninth": {
            "name": 'The Pharaoh', "plate": 'egypt/pantheon/bronze/Pharaoh.png',
        },
        "pantheon": {
            "articles": 'egypt_pantheon',
            "dual_names": ('Ra', 'Afu-Ra'),
            "dual": ('egypt/primary/bronze/Afu_Ra',),
            "seats": {
                'sunday': (('egypt/primary/bronze/Ra',), 'Ra'),
                'monday': (('egypt/pantheon/bronze/Isis',), 'Isis'),
                'tuesday': (('egypt/pantheon/bronze/Horus',), 'Horus'),
                'wednesday': (('egypt/primary/bronze/Thoth',), 'Thoth'),
                'thursday': (('egypt/pantheon/bronze/Anubis',), 'Anubis'),
                'friday': (('egypt/pantheon/bronze/Bastet',), 'Bastet'),
                'saturday': (('egypt/primary/bronze/Osiris',), 'Osiris'),
            },
        },
    },
    # Slavic gods (owner art 2026-07-12, per the approved mapping): Dažbog
    # the giving sun, Hors the night-walker, Svetovid's four faces and
    # white war-horse on Tuesday, Veles the horned trader- trickster
    # mirroring Odin and Hermes, Perun's oak and thunder at noon, Mokoš
    # spinning on the day her cult kept as Friday, Morana — winter drowned
    # each spring — on the arm of Renewal.
    'slavic': {
        "title": 'Slavic gods',
        "art": 'slavic/primary/bronze',
        "articles": 'slavic',
        "blurbs": 'slavic',
        "seats": {
            'monday': {"body": 'moon', "name": 'Hors', "stem": 'Hors'},
            'tuesday': {"body": 'mars', "name": 'Svetovid', "stem": 'Svetovid'},
            'wednesday': {"body": 'mercury', "name": 'Veles', "stem": 'Veles'},
            'thursday': {"body": 'jupiter', "name": 'Perun', "stem": 'Perun'},
            'friday': {"body": 'venus', "name": 'Mokoš', "stem": 'Mokos'},
            'saturday': {"body": 'saturn', "name": 'Morana', "stem": 'Morana'},
        },
        "sunday": {
            "name": 'Dažbog',
            "ruler": 'Young Dažbog', "servant": 'Old Dažbog',
            "stem": 'Dazbog', "servant_plate": 'slavic/primary/bronze/Dazbog_Old',
        },
        "ninth": {
            "name": 'Triglav', "plate": 'slavic/primary/bronze/Triglav.png',
        },
        "pantheon": {
            "articles": 'slavic_pantheon',
            "dual_names": ('Perun', 'Veles'),
            "dual": ('slavic/primary/bronze/Veles',),
            "seats": {
                'sunday': (('slavic/primary/bronze/Perun',), 'Perun'),
                'monday': (('slavic/primary/bronze/Mokos',), 'Mokoš'),
                'tuesday': (('slavic/primary/bronze/Svetovid',), 'Svetovid'),
                'wednesday': (('slavic/pantheon/bronze/Svarog',), 'Svarog'),
                'thursday': (('slavic/primary/bronze/Dazbog',), 'Dažbog'),
                'friday': (('slavic/pantheon/bronze/Lada',), 'Lada'),
                'saturday': (('slavic/primary/bronze/Morana',), 'Morana'),
            },
        },
    },
    # The seven metals of alchemy (owner art 2026-07-12): the classical
    # planet-metal correspondence — every medallion the same still life of
    # bars, nuggets and coiled wire, each wearing its own metal.
    'alchemy': {
        "title": 'Alchemy',
        "art": 'alchemy/primary/colored',
        "articles": 'alchemy',
        "blurbs": 'alchemy',
        "seats": {
            'monday': {"body": 'moon', "name": 'Silver', "stem": 'Silver'},
            'tuesday': {"body": 'mars', "name": 'Iron', "stem": 'Iron'},
            'wednesday': {"body": 'mercury', "name": 'Quicksilver', "stem": 'Mercury'},
            'thursday': {"body": 'jupiter', "name": 'Tin', "stem": 'Tin'},
            'friday': {"body": 'venus', "name": 'Copper', "stem": 'Copper'},
            'saturday': {"body": 'saturn', "name": 'Lead', "stem": 'Lead'},
        },
        "sunday": {
            "name": 'Gold',
            "ruler": 'Gold', "servant": 'Raw Ore',
            "stem": 'Gold', "servant_plate": 'alchemy/primary/colored/Ore',
        },
        "ninth": {
            "name": "The Philosopher's Stone", "plate": 'alchemy/primary/colored/Stone.png',
        },
    },
    # The Japanese week (owner art 2026-07-12, Gemini from our prompts):
    # the yōbi day names ARE the planetary week — sun, moon, then the five
    # Wu Xing element stars (fire=Mars, water=Mercury, wood= Jupiter,
    # metal=Venus, earth=Saturn). Display names KEEP the kanji (owner
    # instruction); files are folded ASCII overrides.
    'japan': {
        "title": 'Japanese week',
        "art": 'japan/primary/colored',
        "articles": 'japan',
        "blurbs": 'japan',
        "seats": {
            'monday': {"body": 'moon', "name": 'Getsuyōbi (月曜日)', "stem": 'Getsuyobi'},
            'tuesday': {"body": 'mars', "name": 'Kayōbi (火曜日)', "stem": 'Kayobi'},
            'wednesday': {"body": 'mercury', "name": 'Suiyōbi (水曜日)', "stem": 'Suiyobi'},
            'thursday': {"body": 'jupiter', "name": 'Mokuyōbi (木曜日)', "stem": 'Mokuyobi'},
            'friday': {"body": 'venus', "name": "Kin'yōbi (金曜日)", "stem": 'Kinyobi'},
            'saturday': {"body": 'saturn', "name": 'Doyōbi (土曜日)', "stem": 'Doyobi'},
        },
        "sunday": {
            "name": 'Nichiyōbi (日曜日)',
            "ruler": 'Amaterasu', "servant": 'Ama-no-Iwato',
            "stem": 'Nichiyobi', "servant_plate": 'japan/primary/colored/Ama_No_Iwato',
        },
    },
    # NARRATIVE-FIRST remap (owner decision 2026-07-12): each religion
    # sits on the day its OWN canon points to, not its rest day —
    # Freemasonry's quest for Light under the All-Seeing Eye takes the Sun
    # (its Sunday DOUBLE = the rough vs the perfect ashlar); Islam's
    # calendar IS the moon (Quran 2:189); Buddhism wins the war-day
    # without weapons (Mara, Dhammapada 103); Christianity's forgiving
    # love lands on Venus's Friday (Good Friday, agape).
    'religion': {
        "title": 'Creeds',
        "art": 'creeds/primary/colored',
        "articles": 'religion',
        "blurbs": 'religion',
        "seats": {
            'monday': {"body": 'moon', "name": 'Islam', "stem": 'Islam'},
            'tuesday': {"body": 'mars', "name": 'Buddhism', "stem": 'Buddhism'},
            'wednesday': {"body": 'mercury', "name": 'Taoism', "stem": 'Taoism'},
            'thursday': {"body": 'jupiter', "name": 'Hinduism', "stem": 'Hinduism'},
            'friday': {"body": 'venus', "name": 'Sikhism', "stem": 'Sikhism'},
            'saturday': {"body": 'saturn', "name": 'Judaism', "stem": 'Judaism'},
        },
        "sunday": {
            "name": 'Christianity',
            "ruler": 'Christianity', "servant": 'Satanism',
            "stem": 'Christianity', "servant_plate": 'creeds/primary/colored/Satanism',
        },
        "ninth": {
            "name": 'Freemasonry', "plate": 'creeds/primary/colored/Freemasonry.png',
        },
    },
    # The ALTERNATE religion set — each on the day it fits best (canon in
    # SYMBOLISM.md; Egypt and Babylon per the owner's 2026-07-10 art: Ra's
    # Sunday, Ishtar IS Venus and Babylon invented the 7-day week).
    'religion_alt': {
        "title": 'Ancient religions',
        "art": 'creeds/secondary/colored',
        "articles": 'religion_alt',
        "blurbs": 'religion_alt',
        "seats": {
            'monday': {"body": 'moon', "name": 'Druidism', "stem": 'Druidism'},
            'tuesday': {"body": 'mars', "name": 'Zoroastrianism', "stem": 'Zoroastrianism'},
            'wednesday': {"body": 'mercury', "name": 'Shamanism', "stem": 'Shamanism'},
            'thursday': {"body": 'jupiter', "name": 'Eleusinian Mysteries', "stem": 'Eleusis'},
            'friday': {"body": 'venus', "name": 'Babylon', "stem": 'Babylon'},
            'saturday': {"body": 'saturn', "name": 'Voodoo', "stem": 'Voodoo'},
        },
        "sunday": {
            "name": 'Mithraism',
            "ruler": 'Mithraism', "servant": 'Corax',
            "stem": 'Mithraism', "servant_plate": 'creeds/secondary/colored/Corax',
        },
        "ninth": {
            "name": 'The Unknown God', "plate": 'creeds/secondary/colored/Unknown_God.png',
        },
        "title_plate": ('secondary', 'colored'),
    },
    'profession': {
        "title": 'Professions',
        "art": 'profession/primary/bronze',
        "articles": 'profession',
        "blurbs": 'profession',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Physician', "stem": 'Physician'},
            'tuesday': {"body": 'mars', "name": 'Soldier', "stem": 'Soldier'},
            'wednesday': {"body": 'mercury', "name": 'Merchant', "stem": 'Merchant'},
            'thursday': {"body": 'jupiter', "name": 'Priest', "stem": 'Priest'},
            'friday': {"body": 'venus', "name": 'Artist', "stem": 'Artist'},
            'saturday': {"body": 'saturn', "name": 'Farmer', "stem": 'Farmer'},
        },
        "sunday": {
            "name": 'Ruler · Servant',
            "ruler": 'Ruler', "servant": 'Servant',
            "stem": 'Ruler', "servant_plate": 'profession/primary/bronze/Servant_Dual',
        },
        "ninth": {
            "name": 'The Polymath', "plate": 'profession/primary/bronze/Polymath.png',
        },
    },
    # THE ANIMAL SOCIETIES (owner 2026-07-13) — three orders of order: the
    # pack ranks, the hive works by age (the career IS the clock), the
    # herd remembers (the leader is the one who holds the map).
    'wolf': {
        "title": 'Wolf Pack',
        "art": 'wolf/primary/bronze',
        "articles": 'wolf',
        "blurbs": 'day',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Luna', "stem": 'Luna'},
            'tuesday': {"body": 'mars', "name": 'Hunter (Gamma)', "stem": 'Hunter'},
            'wednesday': {"body": 'mercury', "name": 'Scout (Delta)', "stem": 'Scout'},
            'thursday': {"body": 'jupiter', "name": 'Beta', "stem": 'Beta'},
            'friday': {"body": 'venus', "name": 'Mate', "stem": 'Mate'},
            'saturday': {"body": 'saturn', "name": 'Elder', "stem": 'Elder'},
        },
        "sunday": {
            "name": 'Leader (Alpha) · Omega',
            "ruler": 'Alpha', "servant": 'Omega',
            "stem": 'Alpha', "servant_plate": 'wolf/primary/bronze/Omega',
        },
        "ninth": {
            "name": 'Sigma', "plate": 'wolf/primary/bronze/Sigma.png',
        },
    },
    'bee': {
        "title": 'Bee Hive',
        "art": 'bee/primary/bronze',
        "articles": 'bee',
        "blurbs": 'day',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Nurse', "stem": 'Nurse'},
            'tuesday': {"body": 'mars', "name": 'Guard', "stem": 'Guard'},
            'wednesday': {"body": 'mercury', "name": 'Scout', "stem": 'Scout'},
            'thursday': {"body": 'jupiter', "name": 'Builder', "stem": 'Builder'},
            'friday': {"body": 'venus', "name": 'Drone', "stem": 'Drone'},
            'saturday': {"body": 'saturn', "name": 'Forager', "stem": 'Forager'},
        },
        "sunday": {
            "name": 'Queen · Cleaner',
            "ruler": 'Queen', "servant": 'Cleaner',
            "stem": 'Queen', "servant_plate": 'bee/primary/bronze/Cleaner',
        },
        "ninth": {
            "name": 'The Swarm', "plate": 'bee/primary/bronze/Swarm.png',
        },
    },
    'elephant': {
        "title": 'Elephant Herd',
        "art": 'elephant/primary/bronze',
        "articles": 'elephant',
        "blurbs": 'day',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Allomother', "stem": 'Allomother'},
            'tuesday': {"body": 'mars', "name": 'Musth', "stem": 'Musth'},
            'wednesday': {"body": 'mercury', "name": 'Caller', "stem": 'Caller'},
            'thursday': {"body": 'jupiter', "name": 'Mentor', "stem": 'Mentor'},
            'friday': {"body": 'venus', "name": 'Reunion', "stem": 'Reunion'},
            'saturday': {"body": 'saturn', "name": 'Elder', "stem": 'Elder'},
        },
        "sunday": {
            "name": 'Matriarch · Memory',
            "ruler": 'Matriarch', "servant": 'Memory',
            "stem": 'Matriarch', "servant_plate": 'elephant/primary/bronze/Memory',
        },
        "ninth": {
            "name": 'The Graveyard', "plate": 'elephant/primary/bronze/Graveyard.png',
        },
    },
    # The SCRIPTURE family (owner 2026-07-14): three stained-glass sets.
    'bible': {
        "title": 'Bible',
        "art": 'bible/primary/colored',
        "articles": 'bible',
        "blurbs": 'day',
        "seats": {
            'monday': {"body": 'moon', "name": 'Mary', "stem": 'Mary'},
            'tuesday': {"body": 'mars', "name": 'David', "stem": 'David'},
            'wednesday': {"body": 'mercury', "name": 'Moses', "stem": 'Moses'},
            'thursday': {"body": 'jupiter', "name": 'Solomon', "stem": 'Solomon'},
            'friday': {"body": 'venus', "name": 'Adam & Eve', "stem": 'Adam_And_Eve'},
            'saturday': {"body": 'saturn', "name": 'Joseph', "stem": 'Joseph'},
        },
        "sunday": {
            "name": 'Ancient of Days · Son',
            "ruler": 'Ancient of Days', "servant": 'Son',
            "stem": 'Ancient_Of_Days', "servant_plate": 'bible/primary/colored/Son_Servant',
        },
        "ninth": {
            "name": 'The Holy Trinity', "plate": 'bible/primary/colored/Holy_Trinity.png',
        },
    },
    'bible2': {
        "title": 'Bible II',
        "art": 'bible/secondary/colored',
        "articles": 'bible2',
        "blurbs": 'day',
        "seats": {
            'monday': {"body": 'moon', "name": 'Jonah', "stem": 'Jonah'},
            'tuesday': {"body": 'mars', "name": 'Samson', "stem": 'Samson'},
            'wednesday': {"body": 'mercury', "name": 'Jacob', "stem": 'Jacob'},
            'thursday': {"body": 'jupiter', "name": 'Noah', "stem": 'Noah'},
            'friday': {"body": 'venus', "name": 'Ruth', "stem": 'Ruth'},
            'saturday': {"body": 'saturn', "name": 'Job', "stem": 'Job'},
        },
        "sunday": {
            "name": 'Abraham · Isaac',
            "ruler": 'Abraham', "servant": 'Isaac',
            "stem": 'Abraham', "servant_plate": 'bible/secondary/colored/Isaac',
        },
        "ninth": {
            "name": 'Melchizedek', "plate": 'bible/secondary/colored/Melchizedek.png',
        },
        "title_plate": ('secondary', 'colored'),
    },
    'bible_dark': {
        "title": 'Bible Dark',
        "art": 'bible/dark/colored',
        "articles": 'bible_dark',
        "blurbs": 'day',
        "seats": {
            'monday': {"body": 'moon', "name": 'Lilith', "stem": 'Lilith'},
            'tuesday': {"body": 'mars', "name": 'Goliath', "stem": 'Goliath'},
            'wednesday': {"body": 'mercury', "name": 'The Serpent', "stem": 'Serpent'},
            'thursday': {"body": 'jupiter', "name": 'Herod', "stem": 'Herod'},
            'friday': {"body": 'venus', "name": 'Delilah', "stem": 'Delilah'},
            'saturday': {"body": 'saturn', "name": 'Cain', "stem": 'Cain'},
        },
        "sunday": {
            "name": 'Lucifer · Judas',
            "ruler": 'Lucifer', "servant": 'Judas',
            "stem": 'Lucifer', "servant_plate": 'bible/dark/colored/Judas',
        },
        "ninth": {
            "name": 'The Ninth Circle', "plate": 'bible/dark/colored/Ninth_Circle.png',
        },
        "title_plate": ('dark', 'colored'),
    },
    # The DEEP SKY (owner 2026-07-14): star-chart medallions.
    'cosmos': {
        "title": 'Cosmos',
        "art": 'cosmos/primary/bronze',
        "articles": 'cosmos',
        "blurbs": 'day',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Nebula', "stem": 'Nebula'},
            'tuesday': {"body": 'mars', "name": 'Supernova', "stem": 'Supernova'},
            'wednesday': {"body": 'mercury', "name": 'Pulsar', "stem": 'Pulsar'},
            'thursday': {"body": 'jupiter', "name": 'Galaxy', "stem": 'Galaxy'},
            'friday': {"body": 'venus', "name": 'Binary Stars', "stem": 'Binary_Stars'},
            'saturday': {"body": 'saturn', "name": 'Comet', "stem": 'Comet'},
        },
        "sunday": {
            "name": 'Sun · Black Hole',
            "ruler": 'Sun', "servant": 'Black Hole',
            "stem": 'Sun', "servant_plate": 'cosmos/primary/bronze/Black_Hole',
        },
        "ninth": {
            "name": 'The Big Bang', "plate": 'cosmos/primary/bronze/Big_Bang.png',
        },
    },
    # The Planets MEDALLION look — same entities, bronze art.
    'planets_art': {
        "title": None,
        "art": 'planets/primary/art',
        "articles": 'planets',
        "blurbs": 'day',
        "metals": ('gold', 'bronze', 'silver'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Moon', "stem": 'Moon'},
            'tuesday': {"body": 'mars', "name": 'Mars', "stem": 'Mars'},
            'wednesday': {"body": 'mercury', "name": 'Mercury', "stem": 'Mercury'},
            'thursday': {"body": 'jupiter', "name": 'Jupiter', "stem": 'Jupiter'},
            'friday': {"body": 'venus', "name": 'Venus', "stem": 'Venus'},
            'saturday': {"body": 'saturn', "name": 'Saturn', "stem": 'Saturn'},
        },
        "sunday": {
            "name": 'Sun',
            "ruler": 'Sun', "servant": 'Eclipsed Sun',
            "stem": 'Sun', "servant_plate": 'planets/primary/art/Sun_Eclipse',
        },
        "title_plate": ('primary', 'art'),
    },
    # THE POLAR DUAL (owner-sealed matrix 2026-07-21): ANTARCTICA the
    # Ruler — a true continent, real rock under the ice — and the ARCTIC
    # the Servant — walkable ice with no land beneath, reality and its
    # shadow. The two live in eternal antiphase (polar day on one is polar
    # night on the other): the Ruler/Servant solar-window law made
    # planetary.
    'continents': {
        "title": 'Continents',
        "art": '../earth',
        "articles": 'continents',
        "blurbs": 'day',
        "seats": {
            'monday': {"body": 'moon', "name": 'Oceania', "stem": COMPUTED},
            'tuesday': {"body": 'mars', "name": 'Europe', "stem": COMPUTED},
            'wednesday': {"body": 'mercury', "name": 'Asia', "stem": COMPUTED},
            'thursday': {"body": 'jupiter', "name": 'Africa', "stem": COMPUTED},
            'friday': {"body": 'venus', "name": 'South America', "stem": COMPUTED},
            'saturday': {"body": 'saturn', "name": 'North America', "stem": COMPUTED},
        },
        "sunday": {
            "name": 'Antarctica',
            "ruler": 'Antarctica', "servant": 'Arctic',
            "stem": COMPUTED, "servant_plate": COMPUTED,
        },
        "ninth": {
            # THE CONTINENTS MATRIX NAMES (owner order 2026-08-14): the
            # deep-time faces joined the earth family's
            # `earth_{style}_{region}_{phase}` naming; these two plates
            # pin the ATMO DAY face (CONTINENTS_PREVIEW_STYLE) until the
            # style/phase-aware ninth resolver lands (future round,
            # continents_prompts.md).
            "name": 'Zealandia', "plate": '../earth/earth_atmo_zealandia_day.png',
            "alt": 'Pangea', "alt_plate": '../earth/earth_atmo_pangea_day.png',
            "mechanism": 'easter_egg',
        },
    },
    # THE INNER WHEEL on the dial (owner 2026-07-14): the days ARE their
    # virtues / vices / hour-moods.
    'virtues': {
        "title": 'Virtues',
        "art": '../emblem/virtue/primary/colored',
        "articles": 'virtues',
        "blurbs": 'day',
        "seats": {
            'monday': {"body": 'moon', "name": 'Serenity', "stem": 'Serenity'},
            'tuesday': {"body": 'mars', "name": 'Courage', "stem": 'Courage'},
            'wednesday': {"body": 'mercury', "name": 'Wisdom', "stem": 'Wisdom'},
            'thursday': {"body": 'jupiter', "name": 'Generosity', "stem": 'Generosity'},
            'friday': {"body": 'venus', "name": 'Love', "stem": 'Love'},
            'saturday': {"body": 'saturn', "name": 'Patience', "stem": 'Patience'},
        },
        "sunday": {
            "name": 'Justice · Humility',
            "ruler": 'Justice', "servant": 'Humility',
            "stem": 'Justice', "servant_plate": '../emblem/virtue/primary/colored/Humility',
        },
    },
    'sins': {
        "title": 'Sins',
        "art": '../emblem/sin/primary/colored',
        "articles": 'sins',
        "blurbs": 'day',
        "seats": {
            'monday': {"body": 'moon', "name": 'Fear', "stem": 'Fear'},
            'tuesday': {"body": 'mars', "name": 'Wrath', "stem": 'Wrath'},
            'wednesday': {"body": 'mercury', "name": 'Greed', "stem": 'Greed'},
            'thursday': {"body": 'jupiter', "name": 'Excess', "stem": 'Excess'},
            'friday': {"body": 'venus', "name": 'Jealousy', "stem": 'Jealousy'},
            'saturday': {"body": 'saturn', "name": 'Envy', "stem": 'Envy'},
        },
        "sunday": {
            "name": 'Pride · Servility',
            "ruler": 'Pride', "servant": 'Servility',
            "stem": 'Pride', "servant_plate": '../emblem/sin/primary/colored/Servility',
        },
    },
    'moods': {
        "title": 'Moods',
        "art": '../emblem/mood/primary/colored',
        "articles": 'moods',
        "blurbs": 'day',
        "seats": {
            'monday': {"body": 'moon', "name": 'Calm', "stem": 'Calm'},
            'tuesday': {"body": 'mars', "name": 'Zeal', "stem": 'Zeal'},
            'wednesday': {"body": 'mercury', "name": 'Sorrow', "stem": 'Sorrow'},
            'thursday': {"body": 'jupiter', "name": 'Joy', "stem": 'Joy'},
            'friday': {"body": 'venus', "name": 'Passion', "stem": 'Passion'},
            'saturday': {"body": 'saturn', "name": 'Renewal', "stem": 'Renewal'},
        },
        "sunday": {
            "name": 'Glory · Awe',
            "ruler": 'Glory', "servant": 'Awe',
            "stem": 'Glory', "servant_plate": '../emblem/mood/primary/colored/Awe',
        },
    },
    # COMPLETION WAVE I (Session 31, 2026-07-29). Three casts sealed in
    # their own prompt sheets long before the wiring: the Olympians'
    # bestiary seated by the VICE of each arm rather than the virtue
    # (research/prompts/monsters/), the Chinese court drawn from folk
    # myth, the Three Kingdoms and Journey to the West
    # (research/prompts/chinese/), and the executive committee — the one
    # cast in the book whose members are OFFICES rather than persons
    # (research/prompts/corporate/). COMPLETION WAVE I (Session 31). Three
    # duals of one house rather than three oppositions: two literal
    # brothers (both children of Typhon and Echidna), a Sage and his
    # perfect counterfeit, and the two offices company law itself
    # recommends be held apart.
    'age_of_heroes': {
        "title": 'Greek Monsters',
        "art": 'age_of_heroes/primary/bronze',
        "articles": 'age_of_heroes',
        "blurbs": 'age_of_heroes',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Medusa', "stem": 'Medusa'},
            'tuesday': {"body": 'mars', "name": 'Minotaur', "stem": 'Minotaur'},
            'wednesday': {"body": 'mercury', "name": 'Sphinx', "stem": 'Sphinx'},
            'thursday': {"body": 'jupiter', "name": 'Erymanthian Boar', "stem": 'Erymanthian_Boar'},
            'friday': {"body": 'venus', "name": 'Sirens', "stem": 'Sirens'},
            'saturday': {"body": 'saturn', "name": 'Hydra', "stem": 'Hydra'},
        },
        "sunday": {
            "name": 'Nemean Lion · Cerberus',
            "ruler": 'Nemean Lion', "servant": 'Cerberus',
            "stem": 'Nemean_Lion', "servant_plate": 'age_of_heroes/primary/bronze/Cerberus',
        },
        "ninth": {
            "name": 'Pegasus', "plate": 'age_of_heroes/primary/bronze/Pegasus.png',
        },
    },
    'celestial_court': {
        "title": 'Chinese Mythology',
        "art": 'celestial_court/primary/bronze',
        "articles": 'celestial_court',
        "blurbs": 'celestial_court',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": "Chang'e", "stem": 'ChangE'},
            'tuesday': {"body": 'mars', "name": 'Erlang Shen', "stem": 'Erlang_Shen'},
            'wednesday': {"body": 'mercury', "name": 'Guan Yu', "stem": 'Guan_Yu'},
            'thursday': {"body": 'jupiter', "name": 'Zhu Bajie', "stem": 'Zhu_Bajie'},
            'friday': {"body": 'venus', "name": 'Zhinü', "stem": 'Zhinu'},
            'saturday': {"body": 'saturn', "name": 'Shennong', "stem": 'Shennong'},
        },
        "sunday": {
            "name": 'Sun Wukong · Six-Eared Macaque',
            "ruler": 'Sun Wukong', "servant": 'The Six-Eared Macaque',
            "stem": 'Sun_Wukong', "servant_plate": 'celestial_court/primary/bronze/Six_Eared_Macaque',
        },
        "ninth": {
            "name": 'Buddha', "plate": 'celestial_court/primary/bronze/Buddha.png',
        },
    },
    'corporate': {
        "title": 'The Corporation',
        "art": 'corporate/primary/bronze',
        "articles": 'corporate',
        "blurbs": 'corporate',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'CHRO', "stem": 'CHRO'},
            'tuesday': {"body": 'mars', "name": 'COO', "stem": 'COO'},
            'wednesday': {"body": 'mercury', "name": 'CFO', "stem": 'CFO'},
            'thursday': {"body": 'jupiter', "name": 'CMO', "stem": 'CMO'},
            'friday': {"body": 'venus', "name": 'CDO', "stem": 'CDO'},
            'saturday': {"body": 'saturn', "name": 'CTO', "stem": 'CTO'},
        },
        "sunday": {
            "name": 'CEO · Chairman',
            "ruler": 'CEO', "servant": 'Chairman of the Board',
            "stem": 'CEO', "servant_plate": 'corporate/primary/bronze/Chairman',
        },
        "ninth": {
            "name": 'The Founder', "plate": 'corporate/primary/bronze/Founder.png',
        },
    },
    # COMPLETION WAVE II (Session 32, 2026-07-29). The three World of
    # Warcraft casts, rosters owner-sealed 2026-07-22 in
    # research/prompts/wow/wow_prompts.md: the SAME nine seats held three
    # times over, with the arm bundle fixed and only the person changing
    # (CUBE.md Charter rule 5 — three different people holding one office,
    # never one character read three ways). The Alliance and the Horde are
    # seated by the arm's VIRTUE, the Evil cast by the VICE that virtue is
    # named against. COMPLETION WAVE II (Session 32). Three duals of one
    # house rather than three oppositions, exactly as the sheet argues
    # them: two kings of the same alliance, a Warchief and the successor
    # he appointed himself, and two men who made the identical bargain and
    # were answered differently for it.
    'wow_alliance': {
        "title": 'Warcraft Alliance',
        "art": 'wow_alliance/primary/bronze',
        "articles": 'wow_alliance',
        "blurbs": 'wow_alliance',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Anduin', "stem": 'Anduin'},
            'tuesday': {"body": 'mars', "name": 'Muradin Bronzebeard', "stem": 'Muradin'},
            'wednesday': {"body": 'mercury', "name": 'Khadgar', "stem": 'Khadgar'},
            'thursday': {"body": 'jupiter', "name": 'Uther the Lightbringer', "stem": 'Uther'},
            'friday': {"body": 'venus', "name": 'Jaina', "stem": 'Jaina'},
            'saturday': {"body": 'saturn', "name": 'Malfurion', "stem": 'Malfurion'},
        },
        "sunday": {
            "name": 'Varian Wrynn · Genn Greymane',
            "ruler": 'Varian Wrynn', "servant": 'Genn Greymane',
            "stem": 'Varian', "servant_plate": 'wow_alliance/primary/bronze/Genn',
        },
        "ninth": {
            "name": 'Turalyon', "plate": 'wow_alliance/primary/bronze/Turalyon.png',
        },
    },
    'wow_horde': {
        "title": 'Warcraft Horde',
        "art": 'wow_horde/primary/bronze',
        "articles": 'wow_horde',
        "blurbs": 'wow_horde',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Baine', "stem": 'Baine'},
            'tuesday': {"body": 'mars', "name": 'Grommash Hellscream', "stem": 'Grommash'},
            'wednesday': {"body": 'mercury', "name": 'Gallywix', "stem": 'Gallywix'},
            'thursday': {"body": 'jupiter', "name": "Vol'jin", "stem": 'Voljin'},
            'friday': {"body": 'venus', "name": 'Draka', "stem": 'Draka'},
            'saturday': {"body": 'saturn', "name": 'Cairne', "stem": 'Cairne'},
        },
        "sunday": {
            "name": 'Thrall · Garrosh',
            "ruler": 'Thrall', "servant": 'Garrosh Hellscream',
            "stem": 'Thrall', "servant_plate": 'wow_horde/primary/bronze/Garrosh',
        },
        "ninth": {
            "name": 'Rexxar', "plate": 'wow_horde/primary/bronze/Rexxar.png',
        },
    },
    'wow_evil': {
        "title": 'Warcraft Evil',
        "art": 'wow_evil/primary/bronze',
        "articles": 'wow_evil',
        "blurbs": 'wow_evil',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": "Kel'Thuzad", "stem": 'Kel_Thuzad'},
            'tuesday': {"body": 'mars', "name": 'Mannoroth', "stem": 'Mannoroth'},
            'wednesday': {"body": 'mercury', "name": "Gul'dan", "stem": 'Guldan'},
            'thursday': {"body": 'jupiter', "name": "Kil'jaeden the Deceiver", "stem": 'Kiljaeden'},
            'friday': {"body": 'venus', "name": 'Sylvanas', "stem": 'Sylvanas'},
            'saturday': {"body": 'saturn', "name": 'Deathwing', "stem": 'Deathwing'},
        },
        "sunday": {
            "name": 'Arthas · Illidan',
            "ruler": 'Arthas, the Lich King', "servant": 'Illidan Stormrage',
            "stem": 'Arthas', "servant_plate": 'wow_evil/primary/bronze/Illidan',
        },
        "ninth": {
            "name": 'Medivh', "plate": 'wow_evil/primary/bronze/Medivh.png',
        },
    },
    # COMPLETION WAVE II, second half (Session 32, 2026-07-29). The three
    # Cyberpunk 2077 casts, rosters owner-sealed 2026-07-22 in
    # research/prompts/cyberpunk/cyberpunk_prompts.md. THE ROSTER SEATS'
    # DISPLAY LAW: where a seat holds several figures
    # (`WEEKDAY_SEAT_ROSTERS` below) the display name lists them all,
    # separated by the same "·" the Sunday dual already uses. The art
    # rotates daily and the label does not, so a per-figure label would go
    # stale the moment the plate turned; a label naming the WHOLE roster
    # is true on every day of it, and the seat's article argues every
    # member. SUNDAY is the one exception and keeps the Ruler · Servant
    # law every other theme obeys — its rotating partners are named in the
    # two face texts instead. COMPLETION WAVE II, Cyberpunk half (Session
    # 32). Three duals of one house rather than three oppositions, as the
    # sheet argues them: the two corporations that fought the Fourth
    # Corporate War and were left reflecting each other, a legend and the
    # woman who refused the job that made him one, and a founder against
    # the son who strangled him and then sat in the chair.
    'cp_gangs': {
        "title": 'Cyberpunk Gangs',
        "art": 'cp_gangs/primary/bronze',
        "articles": 'cp_gangs',
        "blurbs": 'cp_gangs',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Aldecaldos · Mox', "stem": 'Aldecaldos', "rotates": ('Aldecaldos', 'Mox')},
            'tuesday': {"body": 'mars', "name": 'Maelstrom · Barghest · Wraiths', "stem": 'Maelstrom', "rotates": ('Maelstrom', 'Barghest', 'Wraiths')},
            'wednesday': {"body": 'mercury', "name": 'Voodoo Boys · 6th Street', "stem": 'Voodoo_Boys', "rotates": ('Voodoo_Boys', '6th_Street')},
            'thursday': {"body": 'jupiter', "name": 'Tyger Claws', "stem": 'Tyger_Claws'},
            'friday': {"body": 'venus', "name": 'Valentinos', "stem": 'Valentinos'},
            'saturday': {"body": 'saturn', "name": 'Animals · Scavengers', "stem": 'Animals', "rotates": ('Animals', 'Scavengers')},
        },
        "sunday": {
            "name": 'Arasaka · Militech',
            "ruler": 'Arasaka', "servant": 'Militech',
            "stem": 'Arasaka', "servant_plate": 'cp_gangs/primary/bronze/Militech',
        },
        "ninth": {
            "name": 'NetWatch', "plate": 'cp_gangs/primary/bronze/Netwatch.png',
        },
    },
    'cp_street': {
        "title": 'Cyberpunk Street',
        "art": 'cp_street/primary/bronze',
        "articles": 'cp_street',
        "blurbs": 'cp_street',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Viktor Vektor', "stem": 'Viktor'},
            'tuesday': {"body": 'mars', "name": 'Jackie · Panam · River', "stem": 'Jackie', "rotates": ('Jackie', 'Panam', 'River')},
            'wednesday': {"body": 'mercury', "name": 'Wakako · Padre', "stem": 'Wakako', "rotates": ('Wakako', 'Padre')},
            'thursday': {"body": 'jupiter', "name": 'Misty', "stem": 'Misty'},
            'friday': {"body": 'venus', "name": 'Kerry · Lizzy Wizzy', "stem": 'Kerry', "rotates": ('Kerry', 'Lizzy_Wizzy')},
            'saturday': {"body": 'saturn', "name": 'Judy', "stem": 'Judy'},
        },
        "sunday": {
            "name": 'Johnny Silverhand · Rogue',
            "ruler": 'Johnny Silverhand', "servant": 'Rogue',
            "stem": 'Johnny', "servant_plate": 'cp_street/primary/bronze/Rogue',
        },
        "ninth": {
            "name": 'V', "plate": 'cp_street/primary/bronze/V.png',
        },
    },
    'cp_corpo': {
        "title": 'Cyberpunk Power',
        "art": 'cp_corpo/primary/bronze',
        "articles": 'cp_corpo',
        "blurbs": 'cp_corpo',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Songbird', "stem": 'Songbird'},
            'tuesday': {"body": 'mars', "name": 'Adam Smasher', "stem": 'Adam_Smasher'},
            'wednesday': {"body": 'mercury', "name": 'Dexter DeShawn', "stem": 'Dexter'},
            'thursday': {"body": 'jupiter', "name": 'Solomon Reed', "stem": 'Solomon'},
            'friday': {"body": 'venus', "name": 'Evelyn Parker', "stem": 'Evelyn'},
            'saturday': {"body": 'saturn', "name": 'Takemura', "stem": 'Takemura'},
        },
        "sunday": {
            "name": 'Saburo Arasaka · Yorinobu',
            "ruler": 'Saburo Arasaka', "servant": 'Yorinobu',
            "stem": 'Saburo_Arasaka', "servant_plate": 'cp_corpo/primary/bronze/Yorinobu',
            # THE WEEKLY MANDATE turns the Throne, the Mirror and the
            # Ninth TOGETHER on the ISO week's parity, so the Servant
            # seat carries a roster of its own — the only one in the
            # registry that does.
            "rotates": ('Saburo_Arasaka', 'Rosalind_Myers'),
            "servant_rotates": ('Yorinobu', 'Kurt_Hansen'),
        },
        "ninth": {
            "name": 'Alt Cunningham', "plate": 'cp_corpo/primary/bronze/Alt_Cunningham.png',
            "mechanism": 'term_weekly',
            "rotates": ('Alt_Cunningham', 'Rache_Bartmoss'),
        },
    },
    # COMPLETION WAVE III (Session 33, 2026-07-29). The three Star Wars
    # casts, rosters owner-sealed 2026-07-22 in
    # research/prompts/starwars/starwars_prompts.md. The same nine seats a
    # third time, and the wave where the repeat rule is most visible:
    # Anakin holds the Sith Mirror and the Jedi Mirror, Leia the Jedi
    # Tuesday and the Dyad Thursday, Han the Jedi Wednesday and the Dyad
    # Friday — three people at two ages each, six seats, six independent
    # arguments (CUBE.md Charter rule 5). The Dyad's Tuesday and Wednesday
    # follow the ROSTER SEATS' DISPLAY LAW stated above: the label names
    # every member because the plate turns and the label does not.
    # COMPLETION WAVE III (Session 33). Three duals of one house rather
    # than three oppositions, exactly as the sheet argues them: a son and
    # the father he refused to execute, a master and the apprentice he
    # assembled from a nine-year-old, and the one pair in the whole
    # instrument whose SOURCE material calls them a single power in two
    # bodies.
    'sw_jedi': {
        "title": 'Star Wars Jedi',
        "art": 'sw_jedi/primary/bronze',
        "articles": 'sw_jedi',
        "blurbs": 'sw_jedi',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Obi-Wan Kenobi', "stem": 'Obi_Wan'},
            'tuesday': {"body": 'mars', "name": 'General Leia Organa', "stem": 'Leia'},
            'wednesday': {"body": 'mercury', "name": 'Han Solo', "stem": 'Han'},
            'thursday': {"body": 'jupiter', "name": 'Qui-Gon Jinn', "stem": 'Qui_Gon'},
            'friday': {"body": 'venus', "name": 'Padmé Amidala', "stem": 'Padme'},
            'saturday': {"body": 'saturn', "name": 'Chewbacca', "stem": 'Chewbacca'},
        },
        "sunday": {
            "name": 'Young Luke · Vader',
            "ruler": 'Young Luke', "servant": 'Vader, the Father',
            "stem": 'Luke', "servant_plate": 'sw_jedi/primary/bronze/Vader',
        },
        "ninth": {
            "name": 'Yoda', "plate": 'sw_jedi/primary/bronze/Yoda.png',
        },
    },
    'sw_sith': {
        "title": 'Star Wars Sith',
        "art": 'sw_sith/primary/bronze',
        "articles": 'sw_sith',
        "blurbs": 'sw_sith',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Grand Moff Tarkin', "stem": 'Tarkin'},
            'tuesday': {"body": 'mars', "name": 'General Grievous', "stem": 'Grievous'},
            'wednesday': {"body": 'mercury', "name": 'Jabba the Hutt', "stem": 'Jabba'},
            'thursday': {"body": 'jupiter', "name": 'Count Dooku', "stem": 'Dooku'},
            'friday': {"body": 'venus', "name": 'Maul', "stem": 'Maul'},
            'saturday': {"body": 'saturn', "name": 'Boba Fett', "stem": 'Boba_Fett'},
        },
        "sunday": {
            "name": 'Palpatine · Anakin',
            "ruler": 'Palpatine', "servant": 'Anakin',
            "stem": 'Palpatine', "servant_plate": 'sw_sith/primary/bronze/Anakin',
        },
        "ninth": {
            "name": 'Darth Plagueis', "plate": 'sw_sith/primary/bronze/Plagueis.png',
        },
    },
    # COMPLETION WAVE III (Session 33, 2026-07-29). The Star Wars Dyad's
    # rotating PEOPLE seats — Tuesday and Wednesday, ordinary two-way
    # pairs. THE NINTH'S MECHANISM IS RESOLVED (owner verdict 2026-07-29,
    # SEALED, superseding Session 33's PROVISIONAL date rotation): the
    # Ninth is a DAYLIGHT/NIGHT switch, not a seat roster — "the duality
    # of that theme pulling the actors to one of two sides." Day shows The
    # Ghosts (`constants.WEEKDAY_THEME_NINTHS["sw_dyad"]`, the
    # canonical/good face), night shows Exegol
    # (`constants.WEEKDAY_THEME_NINTH_NIGHT`) — dispatched through
    # `constants.NINTH_MECHANISMS["sw_dyad"] == "daynight"` by
    # `render.ninths.theme_ninth`/`ninth_alt_active` and `render.
    # compositor._center_ninth_alt`, reading the SAME `TickState.
    # is_daylight` `center_face` already reads. The "ninth" entry that
    # used to live here is GONE — see `research/theme_staging.md` for the
    # closed provisional note.
    'sw_dyad': {
        "title": 'Star Wars Dyad',
        "art": 'sw_dyad/primary/bronze',
        "articles": 'sw_dyad',
        "blurbs": 'sw_dyad',
        "metals": ('gold', 'bronze', 'silver', 'colored'),
        "seats": {
            'monday': {"body": 'moon', "name": 'Rose Tico', "stem": 'Rose'},
            'tuesday': {"body": 'mars', "name": 'Finn · Phasma', "stem": 'Finn', "rotates": ('Finn', 'Phasma')},
            'wednesday': {"body": 'mercury', "name": 'Maz Kanata · DJ', "stem": 'Maz', "rotates": ('Maz', 'DJ')},
            'thursday': {"body": 'jupiter', "name": 'Old Leia', "stem": 'Leia'},
            'friday': {"body": 'venus', "name": 'Old Han', "stem": 'Han'},
            'saturday': {"body": 'saturn', "name": 'General Hux', "stem": 'Hux'},
        },
        "sunday": {
            "name": 'Rey · Kylo Ren',
            "ruler": 'Rey', "servant": 'Kylo Ren',
            "stem": 'Rey', "servant_plate": 'sw_dyad/primary/bronze/Kylo',
        },
        "ninth": {
            "name": 'The Ghosts', "plate": 'sw_dyad/primary/bronze/Ghosts.png',
            "alt": 'Exegol', "alt_plate": 'sw_dyad/primary/bronze/Exegol.png',
            "mechanism": 'daynight',
        },
    },
}
