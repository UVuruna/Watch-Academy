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

**The split.** The entries live one file per GROUP, following the
project's own hierarchy (`taxonomy.WEEK_GROUPS` — the same grouping the
asset tree and the Encyclopedia halls use), so a theme's entry sits in
the file its art sits under. `ORDER` below is the dial's own
registration order and is independent of that layout: it is what
`constants.WEEKDAY_THEMES` has always been, and the picker's grouping
lives in `MENU`.

Layer: config — pure DATA. Nothing here imports anything but the
sentinel, which is what lets `constants` and `pantheon` both derive from
it without a cycle.
"""

from config.registry.sentinel import COMPUTED
from config.registry.week import (
    celestial_bodies, crafts, faith, films, gaming, inner_wheel, myth,
    societies,
)

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
# THE REGISTRATION ORDER — what the dial has always listed, kept here
# rather than falling out of the file layout: the group modules are a
# STRUCTURE decision, and a structure decision must never silently
# reorder a user-visible list.
ORDER = (
    'planets',
    'planet_signs',
    'greek',
    'norse',
    'egypt',
    'slavic',
    'alchemy',
    'japan',
    'religion',
    'religion_alt',
    'profession',
    'wolf',
    'bee',
    'elephant',
    'bible',
    'bible2',
    'bible_dark',
    'cosmos',
    'planets_art',
    'continents',
    'virtues',
    'sins',
    'moods',
    'age_of_heroes',
    'celestial_court',
    'corporate',
    'wow_alliance',
    'wow_horde',
    'wow_evil',
    'cp_gangs',
    'cp_street',
    'cp_corpo',
    'sw_jedi',
    'sw_sith',
    'sw_dyad',
)

_GROUPS = (celestial_bodies, myth, faith, crafts, societies, inner_wheel,
           gaming, films)
_ALL = {key: entry for group in _GROUPS for key, entry in group.THEMES.items()}

# ONE assignment, ORDER's order — a theme missing from its group module
# raises here rather than vanishing quietly from the dial.
WEEK = {key: _ALL[key] for key in ORDER}
