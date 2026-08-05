"""THE WEEK REGISTRY — FAITH.

The creeds seated by their OWN canon rather than their rest day, and the three Scripture sets.

One entry per theme, the shape [the package](__init__.py) documents.
This module is DATA and imports only the COMPUTED sentinel; the split
follows the project's own hierarchy (`taxonomy.WEEK_GROUPS`, the same
grouping the asset tree and the Encyclopedia halls use), so a theme's
entry sits in the file its art sits under.

Layer: config — pure.
"""

from config.registry.sentinel import COMPUTED

THEMES = {
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
}
