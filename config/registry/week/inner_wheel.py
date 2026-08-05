"""THE WEEK REGISTRY — THE INNER WHEEL.

The days ARE their virtues, their sins, their hour-moods — the emblem families raised to weekday themes.

One entry per theme, the shape [the package](__init__.py) documents.
This module is DATA and imports only the COMPUTED sentinel; the split
follows the project's own hierarchy (`taxonomy.WEEK_GROUPS`, the same
grouping the asset tree and the Encyclopedia halls use), so a theme's
entry sits in the file its art sits under.

Layer: config — pure.
"""

from config.registry.sentinel import COMPUTED

THEMES = {
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
}
