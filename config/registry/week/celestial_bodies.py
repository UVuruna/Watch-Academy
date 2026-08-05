"""THE WEEK REGISTRY — CELESTIAL BODIES.

The planets in their three depictions, the deep sky, and the world itself — the casts whose members are not persons.

One entry per theme, the shape [the package](__init__.py) documents.
This module is DATA and imports only the COMPUTED sentinel; the split
follows the project's own hierarchy (`taxonomy.WEEK_GROUPS`, the same
grouping the asset tree and the Encyclopedia halls use), so a theme's
entry sits in the file its art sits under.

Layer: config — pure.
"""

from config.registry.sentinel import COMPUTED

THEMES = {
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
            "name": 'Zealandia', "plate": '../earth/zealandia.png',
            "alt": 'Pangea', "alt_plate": '../earth/pangea.png',
            "mechanism": 'easter_egg',
        },
    },
}
