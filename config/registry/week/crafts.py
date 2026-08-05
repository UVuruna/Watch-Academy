"""THE WEEK REGISTRY — CULTURES & CRAFTS.

The seven metals, the Japanese week, and the offices people hold — trade and boardroom alike.

One entry per theme, the shape [the package](__init__.py) documents.
This module is DATA and imports only the COMPUTED sentinel; the split
follows the project's own hierarchy (`taxonomy.WEEK_GROUPS`, the same
grouping the asset tree and the Encyclopedia halls use), so a theme's
entry sits in the file its art sits under.

Layer: config — pure.
"""

from config.registry.sentinel import COMPUTED

THEMES = {
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
}
