"""CLI selftest — print the full computed clock state for any city and
any moment, without launching the widget:

    python -m core --city Belgrade
    python -m core --city Tromso --at 2026-01-15T12:00
    python -m core --lat 78.2232 --lng 15.6267 --tz Europe/Oslo --at 2026-12-21T12:00

The --at time-travel flag is the practical way to eyeball DST, polar and
solstice states.
"""

import argparse
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import astral

from config import constants
from core.clock_state import build_day_context, build_tick_state
from data.locations import LocationRepository
from data.moon_phases import MoonPhaseRepository
from data.seasons import SeasonsRepository


def _fmt(event: datetime | None) -> str:
    return event.strftime("%H:%M:%S") if event else "—"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m core", description="DOMY Watch computation selftest"
    )
    parser.add_argument("--city", help="city name from the bundled locations database")
    parser.add_argument("--lat", type=float, help="latitude (with --lng and --tz)")
    parser.add_argument("--lng", type=float, help="longitude")
    parser.add_argument("--tz", help="IANA timezone name")
    parser.add_argument("--at", help="local ISO datetime (default: now)")
    args = parser.parse_args()

    manual = (args.lat, args.lng, args.tz)
    if args.city and any(value is not None for value in manual):
        parser.error("--city conflicts with --lat/--lng/--tz — use one or the other")
    if args.city:
        matches = LocationRepository().find_city(args.city)
        if not matches:
            raise SystemExit(f"no city named {args.city!r} in the locations database")
        record = matches[0]
        latitude, longitude, tz_name = record.latitude, record.longitude, record.timezone
        print(f"City:       {' / '.join(record.path)}  ({len(matches)} match(es))")
    elif args.lat is not None and args.lng is not None and args.tz:
        lat_low, lat_high = constants.LATITUDE_RANGE
        lng_low, lng_high = constants.LONGITUDE_RANGE
        if not lat_low <= args.lat <= lat_high:
            parser.error(f"--lat must be within {lat_low}..{lat_high}")
        if not lng_low <= args.lng <= lng_high:
            parser.error(f"--lng must be within {lng_low}..{lng_high}")
        latitude, longitude, tz_name = args.lat, args.lng, args.tz
        print(f"Position:   {latitude}, {longitude}")
    else:
        parser.error("provide --city NAME, or --lat --lng --tz")

    try:
        tz = ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        parser.error(f"unknown IANA timezone: {tz_name!r}")
    if args.at:
        try:
            now = datetime.fromisoformat(args.at)
        except ValueError:
            parser.error(f"--at must be an ISO datetime (e.g. 2026-06-21T12:00), got {args.at!r}")
        now = now.replace(tzinfo=tz) if now.tzinfo is None else now.astimezone(tz)
    else:
        now = datetime.now(tz)

    observer = astral.Observer(latitude=latitude, longitude=longitude)
    anchors = SeasonsRepository().year_anchors(now.year)
    window = MoonPhaseRepository().moon_window(now.year)
    day = build_day_context(now, observer, anchors, window)
    tick = build_tick_state(now, day)

    body = constants.WEEKDAY_BODIES[day.weekday_index]
    print(f"Moment:     {now.isoformat()}  (UTC offset {day.utc_offset})")
    print(f"Weekday:    {now.strftime('%A')}  ->  {body}")
    print(f"Regime:     {day.sun.regime.value}")
    print(f"Dawn:       {_fmt(day.sun.dawn)}")
    print(f"Sunrise:    {_fmt(day.sun.sunrise)}")
    print(f"Solar noon: {_fmt(day.sun.noon)}")
    print(f"Sunset:     {_fmt(day.sun.sunset)}")
    print(f"Dusk:       {_fmt(day.sun.dusk)}")
    print(f"Star:       {day.star_rotation:+.2f} deg")
    print(f"Hour hand:  {tick.hour_angle:.2f} deg")
    print(f"Minute hand:{tick.minute_angle:7.2f} deg")
    print(f"Year angle: {tick.year_angle:.2f} deg  (0 = summer solstice at top)")
    print(
        f"Moon:       fraction {day.moon_fraction:.4f}, "
        f"illumination {day.moon_illumination * 100:.1f}%"
    )


if __name__ == "__main__":
    main()
