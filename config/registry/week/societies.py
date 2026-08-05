"""THE WEEK REGISTRY — ANIMAL SOCIETIES.

Three orders of order: the pack ranks, the hive works by age, the herd remembers.

One entry per theme, the shape [the package](__init__.py) documents.
This module is DATA and imports only the COMPUTED sentinel; the split
follows the project's own hierarchy (`taxonomy.WEEK_GROUPS`, the same
grouping the asset tree and the Encyclopedia halls use), so a theme's
entry sits in the file its art sits under.

Layer: config — pure.
"""

from config.registry.sentinel import COMPUTED

THEMES = {
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
}
