"""THE WEEK REGISTRY — GAMING.

Two franchises, six casts: the same nine seats held by different people, which is the repeat rule at its plainest.

One entry per theme, the shape [the package](__init__.py) documents.
This module is DATA and imports only the COMPUTED sentinel; the split
follows the project's own hierarchy (`taxonomy.WEEK_GROUPS`, the same
grouping the asset tree and the Encyclopedia halls use), so a theme's
entry sits in the file its art sits under.

Layer: config — pure.
"""

from config.registry.sentinel import COMPUTED

THEMES = {
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
}
