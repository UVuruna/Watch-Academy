"""THE WEEK REGISTRY — MYTHOLOGIES.

The four pantheons that name the weekdays in their own tongues, plus the Olympians' bestiary and the Chinese court.

One entry per theme, the shape [the package](__init__.py) documents.
This module is DATA and imports only the COMPUTED sentinel; the split
follows the project's own hierarchy (`taxonomy.WEEK_GROUPS`, the same
grouping the asset tree and the Encyclopedia halls use), so a theme's
entry sits in the file its art sits under.

Layer: config — pure.
"""

from config.registry.sentinel import COMPUTED

THEMES = {
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
}
