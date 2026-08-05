"""THE WEEK REGISTRY — FILMS.

The Star Wars trio — three casts, and the wave where one person holds two seats at two ages.

One entry per theme, the shape [the package](__init__.py) documents.
This module is DATA and imports only the COMPUTED sentinel; the split
follows the project's own hierarchy (`taxonomy.WEEK_GROUPS`, the same
grouping the asset tree and the Encyclopedia halls use), so a theme's
entry sits in the file its art sits under.

Layer: config — pure.
"""

from config.registry.sentinel import COMPUTED

THEMES = {
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
