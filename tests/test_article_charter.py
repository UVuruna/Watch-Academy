"""THE ARTICLE CHARTER, rule 4 — NO SCENE DESCRIPTION (owner 2026-07-26).

CUBE.md's Article Charter forbids an article from describing what its
image shows. Session 21 enforced that too NARROWLY — it removed only the
sentences that talked about the ART ASSET ("his Scale window", "no new
glass is cut") and left the STAGING of the figure standing everywhere:
"On the blue pre-dawn arm of Calm stands Jesus…", "At the apex, in spring
green, stands The Child…", "The drawing catches him in a rare state,
seated…", and the whole `[[The Plate]]` movement, whose only job was to
inventory the owner's medallion artwork.

Session 22 (2026-07-27) reworked the WHOLE corpus — every article of
`Database/symbolism.json` and every page of `Database/encyclopedia.json`
— from narration into argument. This module keeps it that way:

1. `test_the_removed_staging_phrases_never_return` pins the exact
   sentences that were deleted, so a future edit cannot restore them.
2. `test_no_article_narrates_its_picture` is the standing corpus lint.

WHY THE LINT IS SHAPED THE WAY IT IS (read before widening it). The bare
words "stands" and "standing" are NOT banned, and must not be: this
corpus uses them constantly as legitimate doctrine — a seat on the dial
("Courage stands at 18h", "she stands on the orange arm of Zeal"), the
geometry of the wheel ("nothing stands opposite the center"), astronomy
("the sun stands directly overhead at local noon"), the definition of awe
("the feeling of standing under something larger than yourself") and the
plain idioms ("stands for", "standing in for", "long-standing"). Banning
the word outright would produce a lint nobody can keep green, which is
worse than no lint at all. What IS banned is the construction that can
only mean a picture is being described: the art asset named, the frame
narrated, a depiction verb, the INVERTED subject the owner caught
("stands Jesus", "stands The Child"), a pose, or a position inside a
frame. Quotations are exempt — scripture says "God standeth in the
congregation" and "an angel of the Lord standing on the right side of
the altar", and a quote is copied, never written.
"""

import json
import re

import pytest

from config import paths

# --------------------------------------------------------------------- #
# The law
# --------------------------------------------------------------------- #

#: Curated staging patterns. Every one of them was lifted from prose the
#: Session 22 rework deleted; none of them has a legitimate reading in an
#: article. Keep this list tight — see the module docstring.
BANNED_PATTERNS = (
    # The article names the art asset standing beside it. NOTE: "emblem"
    # is deliberately NOT here — it legitimately means a heraldic sign
    # ("the EYE OF PROVIDENCE, the emblem Annuit Coeptis favors").
    ("art asset named", re.compile(
        r"\[\[The Plate\]\]"
        r"|\bmedallions?\b|\brondels?\b|\bwoodcuts?\b|\bcameos?\b"
        r"|\b(?:the|his|her|its|their) (?:drawing|plate|badge)\b",
        re.IGNORECASE)),
    # The article narrates the frame instead of the argument.
    ("picture frame narrated", re.compile(
        r"\bin the (?:image|picture|drawing|frame|panel|background"
        r"|foreground|upper corner)\b"
        r"|\bthe (?:image|picture|glass|window) shows\b",
        re.IGNORECASE)),
    # Depiction verbs.
    ("depiction verb", re.compile(
        r"\bdepict(?:s|ed|ing)?\b|\bpictured\b|\bportrayed\b",
        re.IGNORECASE)),
    # THE OWNER'S OWN PROOF: the figure staged by inversion — a locative
    # opener, the verb, then the figure. Case-sensitive on purpose: the
    # capital is what marks the inverted subject.
    ("figure staged", re.compile(r"\b(?:stands|sits)\s+(?:the\s+)?[A-Z]")),
    # A pose, which only a picture has.
    ("pose narrated", re.compile(
        r"\bkneel(?:s|ing)?\b|\bglowers\b|\bstrides\b"
        r"|\bgazes (?:out|down|up)\b",
        re.IGNORECASE)),
    # A position inside the frame.
    ("frame position", re.compile(
        r"\bat (?:his|her|its|their) feet\b"
        r"|\bbehind (?:him|her|them)\b"
        r"|\bin (?:his|her|its) (?:raised )?(?:hand|hands|palm|fist)\b"
        r"|\bon (?:his|her) (?:head|brow|shoulder)\b",
        re.IGNORECASE)),
)

#: Legitimate idioms that would otherwise trip a pattern above. Kept
#: deliberately short — every entry is an idiom of DOCTRINE, never of a
#: picture. A new entry here needs a reason written beside it.
ALLOWED_IDIOMS = (
    re.compile(r"\bstands? for\b", re.IGNORECASE),        # "S stands for Sigma"
    re.compile(r"\bstands? in for\b", re.IGNORECASE),     # substitution
    re.compile(r"\bstanding in for\b", re.IGNORECASE),
    re.compile(r"\blong-standing\b", re.IGNORECASE),
)

#: Schema notes and machine comments, not articles — they are allowed to
#: talk about the art because that is their whole subject.
_NOTE_KEYS = ("about", "note", "articles_note", "zodiac_articles_note",
              "trio_articles_note", "chinese_articles_note",
              "chinese_elements_note")


def _leaves(node, path=()):
    if isinstance(node, str):
        yield path, node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from _leaves(value, path + (key,))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _leaves(value, path + (index,))


def _corpus():
    """Every prose leaf of both databases, minus the schema notes."""
    for name in ("symbolism.json", "encyclopedia.json"):
        data = json.loads(
            (paths.database_dir() / name).read_text(encoding="utf-8")
        )
        for path, text in _leaves(data):
            if any(str(step) in _NOTE_KEYS for step in path):
                continue
            yield f"{name}:{'/'.join(str(step) for step in path)}", text


def _quoted_spans(text):
    """Quotations are copied, not written — rule 4 does not reach them.

    Double quotes mark a quotation outright. Single quotes only do when a
    source follows immediately — that is the corpus's second citation
    habit ("…and on her head a crown of twelve stars' (Revelation 12:1)")
    and the narrow form keeps stray apostrophes from pairing up and
    exempting real prose.
    """
    spans = [(m.start(), m.end()) for m in re.finditer(r'"[^"]*"', text)]
    spans += [(m.start(), m.end())
              for m in re.finditer(r"'[^']{20,}'(?=\s*\()", text)]
    return spans


def staging_offences(text):
    """Every rule-4 violation in one leaf, as (rule, matched text)."""
    quoted = _quoted_spans(text)
    found = []
    for rule, pattern in BANNED_PATTERNS:
        for match in pattern.finditer(text):
            if any(lo <= match.start() < hi for lo, hi in quoted):
                continue
            window = text[max(0, match.start() - 12):match.end() + 14]
            if any(idiom.search(window) for idiom in ALLOWED_IDIOMS):
                continue
            found.append((rule, match.group(0)))
    return found


# --------------------------------------------------------------------- #
# 1. The pin — the exact phrases Session 22 removed
# --------------------------------------------------------------------- #

#: One characteristic phrase per reworked article, verbatim as it stood
#: before the rework. Generated from the diff, so each entry is proof
#: that a specific article was cleaned — and a tripwire if it comes back.
REMOVED_PHRASES = (
    'with its own fire, and the image',
    'The medallion holds nothing back: a seething',
    'small pink prominence flares at the rim,',
    'perfect portrait of the passion it stands',
    'In the drawing he drives the quadriga,',
    'The medallion drives him across dark, star-scattered',
    "The plate matches Helios's finish exactly —",
    'The drawing seats her in a crown',
    'The drawing is honest about it: he',
    'The drawing catches him in a rare',
    'The drawing gives him the full regalia',
    'is loved; the apple in her hand',
    'The crowned titan glowers from a stone',
    'Sol stands in full scale armor with',
    'The medallion casts her in full scale',
    "The plate keeps Sol's own bronze relief",
    'Across the dial at 16h stands Tyr:',
    'ember has two faces, and the image',
    'wisdom, the spear Gungnir in his fist',
    'waist and the cape flaring behind him.',
    'The image tells the truth the Roman',
    'but plain fact: the goddess already stands',
    'over a small fire at his feet',
    'The medallion sets a glowing white cross',
    'The plate keeps the same grapevine-and-fish rim',
    'Path - with a silver Buddha seated',
    'Around the rim eight bagua trigrams alternate',
    "a name for that adjacency: the medallion's",
    'leaves and small stars circle the rim.',
    "and the ruler's discipline is to sit",
    'world he rules small enough to sit',
    "The plate matches the Ruler's bronze relief",
    'lit or unlit — and the image',
    'The Soldier stands square in scale armor,',
    'the sake of what sleeps behind him.',
    'The scale in his raised hand is',
    '— and the hand-balance in his fist',
    'The Priest — the Teacher — stands',
    'open book turned outward in his hand',
    'The two masks behind him are his',
    'and tragedy masks already hanging behind him',
    '— and the sickle in his fist',
    '— the sickle already in his fist',
    'The rim alternates silver torches with small',
    "and the wheat sheaf at the medallion's",
    "owner's medallion restores dignity to the emblem",
    'field: Mithras in his Phrygian cap kneels',
    'turning the wheel of the year stands',
    "The medallion is the tauroctony, the cult's",
    'The plate keeps the bronze-and-gold relief and',
    'set in its heart; beneath it strides',
    'The medallion gives him in polished gold',
    'The medallion gives him in polished gold',
    "The plate keeps Ra-Horakhty's gold-and-silver relief and",
    'On the medallion, know him by the',
    'longest road: straight above at noon stands',
    'Behind him the field is deep royal',
    'collar covers her shoulders, and the rim',
    'The rim answers him in kind, wheat',
    "color to mean rebirth, and the medallion's",
    'and gold fill the field behind him,',
    'The medallion paints him a radiant youth',
    'The plate keeps the silver-and-bronze relief and',
    'full and back again; in his hand',
    'In his hand he held a horn',
    'coils through the roots at his feet',
    "and runes, and a bull's head glowers",
    'In her raised hand she turns a',
    'coiled in the frost at her feet,',
    'The rim is a ring of sun',
    'The medallion casts it as a still',
    "The plate keeps gold's polished border, the",
    'Around the rim runs a full sequence',
    'is no bluer blue on the plate.',
    "The rim is a soldier's rack —",
    'beads across the top of the plate,',
    "The rim is Jupiter's own regalia: crowns",
    'The rim is entirely Venus: ♀ hand-mirrors,',
    'The rim tells you exactly whose metal',
    'across that orb the black Yatagarasu stands',
    'alone, and the rising-sun fan behind her',
    'The medallion blazes gold: a rising-sun fan',
    'The plate keeps the gold relief, sunburst',
    'its wide crescent horns curving up, sits',
    'gold throughout: a round polished mirror stands',
    'with fitted stone, and in the foreground',
    'Behind her a round patch of comb',
    'and the gilded hexagon disc behind her',
    'The medallion holds her at the living',
    'Directly above her stands one dark, empty',
    'Straight across the dial at 16h stands',
    "three times her size at the plate's",
    'working afternoon — the board she stands',
    'after cleaning, nursing, and building behind her,',
    'the last bee at the door standing',
    'top a small engraved sun mark stands,',
    "Small at the plate's bottom, tiny and",
    'The gilded disc behind her head is',
    "and the herd's whole file behind her",
    'The bronze plate holds her mid-stride at',
    'in the grass; the young matriarch stands',
    'yet a mother of her own, standing',
    'The Musth stands mid-fury in weathered bronze',
    'Straight up the axis at noon stands',
    'Straight down the axis at midnight sits',
    'Across the dial at 08h stands the',
    'Across the dial at 20h stands the',
    'The Elder, kneeling to dig a water',
    'best, and his eyes in the plate',
    'seat fits him more plainly: the medallion',
    'a duty he happens to be standing',
    "The plate matches Alpha's bronze relief and",
    'link this theme makes, and the plate',
    'him, snow bursting from both their strides',
    'Straight up the axis at 12h stands',
    'Straight down the axis at 0h sits',
    'Straight across the dial at 08h stands',
    'The Elder sits apart, and the plate',
    'The plate reads them side by side.',
    'the ancient robe than for the kneeling',
    'The plate sets him exactly so: enthroned',
    'scene begins — but that same kneeling',
    'The plate holds her in deep Marian',
    'the Calm hold; the mandorla behind her',
    'The plate catches him mid-swing: the sling',
    'Straight up the axis at noon sits',
    'Straight down the axis at midnight sits',
    'The plate holds them hand in hand',
    'The plate stands him in his coat',
    "Abraham stands at Moriah's altar of stacked",
    'On the seasons cross Abraham stands at',
    "The medallion sets him at Moriah's altar",
    "The plate matches Abraham's tracery and golden",
    'Straight across the dial at 16h stands',
    'On the seasons cross Samson stands at',
    'Straight up the axis at noon stands',
    'Noah stands at the open door of',
    'On the seasons cross Noah stands at',
    'Across the dial at 08h stands Job,',
    'On the seasons cross Ruth stands at',
    'Across the dial at 20h stands Ruth,',
    'On the seasons cross Job stands at',
    'from his brow, while high behind him',
    'On the seasons cross Lucifer stands at',
    'instant it is seen, and behind him',
    'The plate sits him alone on bare',
    'kept against: the shape at the window',
    'On the seasons cross Lilith stands at',
    'hand away: the shield walks behind him',
    'On the seasons cross Goliath stands at',
    'does: the one figure that can sit',
    'Herod sits alone on his throne, both',
    'is generous with the light he sits',
    'Delilah sits with a pair of bronze',
    'On the seasons cross Delilah stands at',
    'No violence sits in the frame —',
    'On the seasons cross Cain stands at',
    'crown he already owns, the other kneels',
    'The medallion casts it as a living',
    "The plate matches the Sun's bronze relief",
    'or if dreaded — and the image',
    'One plate blazes; the other kneels.',
    'dial: a world small enough to sit',
    'The one who stands at the center',
    'The engraved sunburst field behind him is',
    'still lake of the base article, silver light standing',
    'The badge stands a lone figure firm',
    'once, and it takes both virtues standing',
    'love wearing armor — the shield stands',
    'Straight up the axis at noon sits',
    'The medallion pours an open golden hand',
    'The medallion cups two hands together into',
    'The medallion kneels a farmer in a',
    "On the Compass Patience's kneeling farmer shifts",
    "the dark like a puppet's — kneeling",
    'The medallion catches the exact moment the',
    'The badge draws the difference in one',
    'The badge shows the whole mechanism in',
    'The badge shows its own aftermath: a',
    'for a right to burn whoever stands',
    'raised long after the thing behind him',
    "The badge's joke is exact: grasping hands",
    'The badge shows the argument already lost:',
    'The badge shows the grip made visible:',
    'into that same posture: the heart standing',
    'The badge draws the wall low on',
    "that seam: at the wheel's center sit",
    'hours do, because they cannot even stand',
    'read from the opposite height: the plate',
    'The plate holds the whole mood in',
    "growth that is the waiting's reward, standing",
    'The plate stacks two kinds of exertion',
    'The plate holds it in a single',
    'The plate scatters rather than shines: a',
    'The plate is caught mid-gesture rather than',
    'The plate needs only one small fact',
    'The drawing gives him the full regalia',
    'The medallion holds him crowned and enthroned,',
    "The plate keeps the Sunday set's own",
    'The drawing shows him rising chest-deep where',
    'The drawing catches her mid-stride through dense',
    'The drawing shows her in calm, unhurried',
    'The drawing stands him radiant beside the',
    'The drawing seats her in full queenly',
    'The drawing seats her with a sheaf',
    "the traveler's cowl; his traded eye-socket sits",
    'The medallion sets him upon Hlidskjalf, the',
    'The plate reuses the standing wanderer-sage exactly',
    'rises out of cold mist behind her;',
    'waist and the cape flaring behind him.',
    'over a small fire at his feet',
    'Frigg stands composed and regal, and nothing',
    'rests small and bright at his feet,',
    'argument for the seat: Freyr already stands',
    'Storm-clouds boil around him, mountains stand below,',
    'The medallion keeps him exactly as the',
    'coiled through the roots at his feet',
    'her lap, full sheaves of wheat stand',
    'Banked coals glow behind him like a',
    'trailing bridal ribbon coil at her feet.',
    'in the noon yellow of Joy, stands',
    'He sits at the PRESENT — the',
    'the red evening arm of Passion sits',
    'walks the earth in Job and stands',
    'the blue pre-dawn arm of Calm stands',
    'At the apex, in spring green, stands',
    'already given to the woman — stands',
    "paint trio, the guardian's color — stands",
    'her warms the house, and he stands',
    'At the center stands the Throne —',
    'On the summer arm of fire stands',
    'On the autumn arm of earth stands',
    'On the winter arm of water stands',
    'On the spring arm of air stands',
    'At the center stands the Throne —',
    'At the top, in yellow, stands The',
    'On the orange arm of Zeal stands',
    'Courage is the virtue that stands between',
    'At the bottom, in purple Sorrow, sits',
    'On the green arm of Renewal stands',
    'poured out, once climbing and once kneeling.',
    'The cure stands across the wheel: Gratitude',
    "It is being someone's working light: standing",
    'Fear conjugated, the sentry who never stands',
    'At noon, the throne hour, stands the',
    'God stands at midnight on the creation',
    'Preserver he is the office that stands',
    '— so that judgment and creation stand',
    '— what fermented in the dark stands',
    'walks the earth in Job and stands',
    "The seat binds to yellow's standing readings",
    'Patronage answers a standing question of the',
    'Standing directly opposite Loyalty, it states the',
    'when the loyal party has no standing',
    "The owner's bull stands inside a dark",
    "The owner's lion strides in profile, mane",
    'as the bright star in her hand.',
    "The owner's figure kneels on one knee,",
    'the wheel turns, and the water-bearer kneels',
    "owner's medallion gives the whole animal, seated",
    'The medallion shows the great head with',
    'The medallion holds the head in profile',
    'The medallion coils the whole body into',
    'The medallion gives the bearded head with',
    'The medallion carries the head in profile,',
    "owner's medallion shows the whole dog standing",
    'The medallion may be the warmest of',
    'stone and engraving untouched, so the plate',
    'The medallion sets him on his own',
    "The badge answers Justice's throne with a",
    'The emblem holds its whole mood in',
    'The emblem is a single held line:',
    "The badge's owl needs no lantern to",
    'The medallion is pure verb — one',
    'The emblem builds a nest rather than',
    'The badge plants two ages at once:',
    'The medallion catches him mid-lie: gazing into',
    'The badge draws the difference from Humility',
    "The emblem's real monster is a shadow",
    'spear broken, only a bare fist wreathed',
    "The badge's joke is exact — a",
    "The emblem's table has already lost the",
    "The badge's rose is the same one",
    "The emblem's wall is deliberately low, easy",
    'a glance: six hours around the rim,',
    "The medallion's proof is the missing shadow",
    'The emblem holds its whole mood in',
    'The badge stacks two kinds of exertion',
    "The emblem's single tear is amethyst, not",
    "The badge's light does not merely shine,",
    "The emblem's hands never actually meet —",
    'The badge needs only one small green',
    'face at the bottom of the plate:',
    'The badge reads exactly this balance: a',
    'The badge shows it plainly: a wheat',
    'The badge is that fire made literal:',
    'The badge holds the stillness whole: one',
    "The badge reads the belt's own weather",
    "The badge trades the Wet season's silver",
    'The badge marks this distinction rather than',
    'The badge borrows the shape of that',
    'The badge answers gold with silver: a',
    'in metal rather than pigment: the badge',
    'rock outcrop where an alpha would stand',
    'The plate holds that departure at its',
    'The plate paints the legend rather than',
    'The plate stages that first instant as',
    'The plate finds him seated on a',
    'sun, Skoll forever a jump behind her',
    'a plate on this dial either, stands',
    'no distaff — only a bare standing',
    'The plate holds a single small stone,',
    'The plate shows him holding up a',
    'The plate keeps that emptiness rather than',
    'The plate keeps the secret rather than',
    'The plate keeps him in robes that',
    'The plate finds him calm now rather',
    'The plate paints the loss rather than',
    'to share one plate because Ophiuchus stands',
    'The plate raises her waist-high out of',
    'The plate gives him in the golden',
    'The medallion gives the whole disc to',
    'is how this plate outranks the seated',
    'The plate keeps the golden compasses held',
    'The plate seats a single robed master',
    "The plate keeps the set's own stained-glass",
    'The plate looks straight down on Cocytus',
    'whole instrument depends on and never depicts',
    'a half-wreath of laurel along the rim,',
    'image is a bull of dharma standing',
    'Signs / Art arrows above the medallion',
    'the wolf forever a stride behind her,',
    'his patient last day; Thoth alone sits',
    "claims Wednesday's forge, giving Dažbog now sits",
    "A star-chart medallion per day: the Nebula's Monday birth-cloud, the Supernova's Tuesday violence, the Pulsar's Wednesday precise beat, the Galaxy's Thursday vast wheel, Binary Stars' Friday orbit, the Comet's Saturday long return — the sky's OWN objects standing in for the myths every other theme tells.",
    'opposite it on the dark cross stands',
)


def test_the_removed_staging_phrases_never_return():
    """Every phrase Session 22 deleted stays deleted."""
    assert REMOVED_PHRASES, "the pin list must not be empty"
    blob = "\n".join(text for _, text in _corpus())
    returned = [phrase for phrase in REMOVED_PHRASES if phrase in blob]
    assert returned == [], f"{len(returned)} deleted phrases came back"


def test_the_owners_two_proofs_are_gone():
    """The two sentences the owner pointed at on the live pages — the
    Prism/Trinity Jesus and the Family's Child — and the seats they
    argued, which must survive the rework."""
    from data.symbolism import SymbolismRepository

    repo = SymbolismRepository()
    jesus = " ".join(
        repo.archetype_article("archetype_trinity_paint", "jesus")["rows"]
    )
    assert "stands Jesus" not in jesus
    assert "blue pre-dawn arm of Calm" in jesus       # the seat survives
    assert "WEAKNESS" in jesus                        # the quality survives
    assert "(Matthew 16:24)" in jesus                 # the quote survives

    child = " ".join(
        repo.archetype_article("archetype_trinity_light", "child")["rows"]
    )
    assert "At the apex, in spring green, stands" not in child
    assert "spring green" in child                    # the colour survives
    assert "STRIVE FOR" in child                      # the doctrine survives


# --------------------------------------------------------------------- #
# 2. The standing corpus lint
# --------------------------------------------------------------------- #

def test_no_article_narrates_its_picture():
    """CHARTER RULE 4 over the WHOLE corpus: no article, legend blurb or
    Encyclopedia page describes the artwork beside it."""
    offenders = []
    for where, text in _corpus():
        for rule, hit in staging_offences(text):
            offenders.append(f"{where}: [{rule}] {hit!r}")
    assert offenders == [], (
        f"{len(offenders)} scene descriptions:\n  "
        + "\n  ".join(offenders[:40])
    )


def test_no_article_keeps_a_plate_movement():
    """`[[The Plate]]` existed only to inventory the owner's medallions.
    Session 22 removed all 153 of them; the movement is retired."""
    plates = [where for where, text in _corpus() if "[[The Plate]]" in text]
    assert plates == []


@pytest.mark.parametrize("rule,sample,expected", (
    ("figure staged", "On the blue arm of Calm stands Jesus — Weakness.", 1),
    ("figure staged", "At the apex, in spring green, stands The Child.", 1),
    ("art asset named", "The owner's medallion casts the still life.", 1),
    ("pose narrated", "a farmer kneeling to sow a single seed", 1),
    ("frame position", "a vulture waits at his left, and at his feet a wheel", 1),
    # …and the doctrine the law explicitly allows must stay clean.
    ("allowed", "The blue arm is the gaze that stays behind.", 0),
    ("allowed", "The apex seat is the one the two below strive for.", 0),
    ("allowed", "Judas holds the blue arm, and his quality is WEAKNESS.", 0),
    ("allowed", "On the seasons cross Courage stands at 18h — Autumn.", 0),
    ("allowed", "the sun stands directly overhead at local noon", 0),
    ("allowed", "the feeling of standing under something larger", 0),
    ("allowed", "S stands for Sigma, the sum of the host.", 0),
    ("allowed", '"God standeth in the congregation of the mighty"', 0),
))
def test_the_lint_catches_staging_and_spares_doctrine(rule, sample, expected):
    """The lint is only worth keeping if it has no false positives — the
    owner's own allowed/forbidden examples, both directions."""
    assert len(staging_offences(sample)) == expected, sample
