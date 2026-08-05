"""The registry's one sentinel.

`COMPUTED` marks a value the registry REFUSES to freeze: the
Continents' seat stems ARE the dial's own Earth faces, built from
`continents.CONTINENTS_REGIONS` at derivation time (Rule #19 — compute,
don't generate). Writing them out would be the same mapping in a second
place, and the second place is always the one that goes stale.

Its own module so every group table in [week/](week/__init__.py) can
import it without importing its siblings.

Layer: config — pure, imports nothing.
"""

COMPUTED = "<computed>"
