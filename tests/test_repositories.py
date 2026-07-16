"""Repository behavior against the LIVE Database/*.json files."""

import pytest

from data.locations import LocationRepository
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository


@pytest.fixture(scope="module")
def locations():
    repo = LocationRepository()
    repo.load()
    yield repo
    repo.release()


class TestLocations:
    def test_top_level_is_five_continents(self, locations):
        names = {node.name for node in locations.children()}
        assert names == {"Africa", "Americas", "Asia", "Europe", "Oceania"}
        assert all(not node.is_city for node in locations.children())

    def test_mixed_depth_walk_matches_audit(self, locations):
        """The audited shape after the 2026-07 curation (macro regions
        for the 9 chaotic countries, Tokyo's Shibuya-ku duplicate
        removed): 241 countries, 121 MIXED (city leaves and admin dicts
        in the same children mapping), 45,649 cities."""
        countries = mixed = cities = 0
        for continent in locations.children():
            for subregion in locations.children((continent.name,)):
                path = (continent.name, subregion.name)
                for country in locations.children(path):
                    countries += 1
                    kinds = set()
                    for child in locations.children(path + (country.name,)):
                        if child.is_city:
                            kinds.add("city")
                            cities += 1
                        else:
                            kinds.add("admin")
                            cities += sum(
                                1
                                for leaf in locations.children(
                                    path + (country.name, child.name)
                                )
                                if leaf.is_city
                            )
                    if kinds == {"city", "admin"}:
                        mixed += 1
        assert countries == 241
        assert mixed == 121
        assert cities == 45_649

    def test_macro_region_curation(self, locations):
        """The 9 chaotic countries were re-nested under a small set of
        standard macro regions (owner-approved agent curation): London
        now sits under UK/London; Tokyo under Japan/Kanto."""
        uk = ("Europe", "Northern Europe", "United Kingdom")
        uk_regions = [n.name for n in locations.children(uk) if not n.is_city]
        assert len(uk_regions) == 12                 # ITL1, was 186 admins
        london = [
            n for n in locations.children(uk + ("London",)) if n.name == "London"
        ]
        assert london and london[0].is_city
        japan = ("Asia", "Eastern Asia", "Japan")
        jp_regions = [n.name for n in locations.children(japan) if not n.is_city]
        assert sorted(jp_regions) == [
            "Chubu", "Chugoku", "Hokkaido", "Kansai",
            "Kanto", "Kyushu", "Shikoku", "Tohoku",
        ]
        tokyo_kids = locations.children(japan + ("Kanto",))
        names = {n.name for n in tokyo_kids}
        assert "Tokyo" in names and "Shibuya" in names
        assert "Shibuya-ku" not in names             # duplicate removed

    def test_admin_nested_sample_from_audit(self, locations):
        ada = [
            node
            for node in locations.children(
                ("Europe", "Southern Europe", "Serbia", "Banat")
            )
            if node.name == "Ada"
        ]
        assert ada and ada[0].is_city
        assert ada[0].record.timezone == "Europe/Belgrade"

    def test_find_city_folds_diacritics(self, locations):
        """The DB stores ASCII transliterations; native spellings must
        still match (combining marks AND single-codepoint letters)."""
        nis = [r for r in locations.find_city("Niš") if "Serbia" in r.path]
        assert nis and nis[0].name == "Nis"
        tromso = locations.find_city("Tromsø")
        assert tromso and tromso[0].name == "Tromso"

    def test_release_and_reload_cycle(self, locations):
        locations.release()
        assert len(locations.children()) == 5  # auto-reloads lazily

    def test_find_city_belgrade(self, locations):
        serbian = [
            record
            for record in locations.find_city("Belgrade")
            if "Serbia" in record.path
        ]
        assert len(serbian) == 1
        assert serbian[0].timezone == "Europe/Belgrade"
        assert serbian[0].latitude == pytest.approx(44.8, abs=0.3)

    def test_unknown_path_fails_loudly(self, locations):
        with pytest.raises(KeyError, match="Atlantis"):
            locations.children(("Europe", "Atlantis"))


class TestCoverageErrors:
    def test_seasons_out_of_range(self):
        with pytest.raises(ValueError, match="1560-2640"):
            SeasonsRepository().year_anchors(1500)

    def test_moon_out_of_range(self):
        with pytest.raises(ValueError, match="1551-2649"):
            MoonPhaseRepository().moon_window(1400)


class TestCoverage:
    """coverage() reads the span straight from the bundled data (Rule #4
    — no hardcoded 1560/2640), so Time Travel can validate before the day
    build (owner 2026-07-16)."""

    def test_seasons_coverage_matches_data(self):
        assert SeasonsRepository().coverage() == (1560, 2640)

    def test_moon_coverage_matches_data(self):
        assert MoonPhaseRepository().coverage() == (1551, 2649)

    def test_error_message_matches_coverage(self):
        # The out-of-range message names exactly what coverage() reports.
        first, last = SeasonsRepository().coverage()
        with pytest.raises(ValueError, match=f"{first}-{last}"):
            SeasonsRepository().year_anchors(first - 1)
