#!/usr/bin/env python3
"""Rebuild the PLACES array in index.html from the CSVs in data/.

    python3 tools/import-places.py

Reads data/*.csv plus tools/coordinates.json and rewrites everything between the
PLACES:START and PLACES:END markers in index.html. The page stays a single
self-contained file with no build step — this is a one-shot importer you run
when the CSVs change, not part of serving the site.

Every mapping decision from CSV column to app field lives here, so the reasoning
is reviewable rather than buried in hand-edited data.
"""

import csv
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
COORDS = json.loads((ROOT / "tools/coordinates.json").read_text())

# Photo credits, keyed by slug. The CC BY / CC BY-SA licences on several of these
# only permit publication with the author credited, so the credit travels with
# the photo into the page rather than living in a file nobody renders.
PHOTOS = {k: v for k, v in json.loads((ROOT / "tools/photos.json").read_text()).items()
          if not k.startswith("_")}
BY_PLACE = {v["place"]: dict(v, slug=k) for k, v in PHOTOS.items()}

# Venues the CSV files as "Restaurant" that are really breweries, taprooms or
# bars. Only affects which icon shows on the pin and which chip filters them in.
BARS = {
    "Liberty Sports Bar & Grill", "Distant Brewing", "Mammoth Brewing Co.",
    "Lakanuki", "Mountain Rambler Brewery", "T-Bar Social Club",
    "Stone Brewing World Bistro & Gardens",
}

TYPE_FROM_CSV = {"Restaurant": "restaurant", "Hotel": "hotel",
                 "Dog Park": "park", "Pet Store": "store"}

# Note fragments that are the spreadsheet talking about itself — where a rating
# came from, what Google calls the place, a correction to an earlier row. Useful
# to whoever maintains the CSV, meaningless to someone choosing a lunch spot.
# Caveats a visitor would want ("verify before visiting", "seasonal") are kept.
NOISE = re.compile(
    r"(rating\b|listed\b|now listed|corrected\b|no google|low review|"
    r"not yet rated|varies by location$|opened nov 2024$|highest-rated|lowest-rated)", re.I)


def yes(value):
    """CSV columns are free text. Anything starting 'Yes' counts; 'Partial',
    'No', 'Varies' and 'N/A' do not — a half-shaded patio should not show the
    same badge as a fully shaded one."""
    return (value or "").strip().lower().startswith("yes")


def num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def city_of(address):
    """'2816 Historic Decatur Rd Unit 116, San Diego, CA 92106' -> 'San Diego'."""
    parts = [p.strip() for p in (address or "").split(",")]
    if len(parts) >= 3:
        return parts[-2]
    # A couple of rows give a landmark rather than a street address.
    return re.sub(r"\s*\(.*?\)", "", parts[0]).strip()


def sentence(text):
    """Normalise a CSV fragment into a sentence. Only the first character is
    touched — .capitalize() would flatten 'OC Raw' to 'Oc raw'."""
    text = (text or "").strip().rstrip(".")
    if not text:
        return ""
    return text[0].upper() + text[1:] + "."


def clean(name):
    """Trim the CSV's parenthetical disambiguators from display names."""
    return re.sub(r"\s*\((cabins|Kimpton Shorebreak|Yorba Park|Huntington Central Park)\)", "", name).strip()


def js(value):
    return json.dumps(value, ensure_ascii=False)


def food_and_lodging():
    rows = []
    with open(ROOT / "data/dogfriendly-california.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if not r.get("Name"):
                continue
            name = r["Name"].strip()
            kind = TYPE_FROM_CSV[r["Type"].strip()]
            if kind == "restaurant" and name in BARS:
                kind = "bar"

            seating = r["Seating / Dogs Allowed"]
            # California keeps dogs out of indoor food-service areas, so these
            # are patio-only unless the row explicitly says dogs go inside.
            friendly = "full" if kind == "hotel" or "INDOORS" in seating else "patio"

            amen = []
            if yes(r["Water Bowls"]):
                amen.append("water")
            if yes(r["Dog Menu"]):
                amen.append("menu")
            if yes(r["Free Treats"]):
                amen.append("treats")
            if yes(r["Shaded Patio"]):
                amen.append("shade")
            if yes(r["Off-Leash Area"]):
                amen.append("offleash")
            # Hotel rows put bedding in the Water Bowls column ("Yes - plus bed,
            # mat, courtesy bags"), which is where the dog-bed signal lives.
            if kind == "hotel" and re.search(r"bed|mat\b|bedding", r["Water Bowls"], re.I):
                amen.append("beds")

            blurb = []
            menu = r["Dog Menu"].strip()
            if yes(menu):
                detail = menu.split("-", 1)[1].strip() if "-" in menu else ""
                blurb.append(sentence("Dog menu" + (f": {detail}" if detail else "")))
            blurb.append(sentence(seating))
            for note in r["Notes"].split(";"):
                note = note.strip()
                if note and not NOISE.match(note):
                    blurb.append(sentence(note))

            fee = r["Pet Fee / Limits"].strip()
            rows.append(dict(
                name=clean(name), type=kind, friendly=friendly, amen=amen,
                addr=r["Location"].strip(), rating=num(r["Google Rating"]),
                reviews=num(r["Google Reviews"]),
                fee=None if fee in ("", "N/A") else fee,
                blurb=" ".join(b for b in blurb if b),
                featured=yes(menu), key=name,
            ))
    return rows


def parks_and_stores():
    rows = []
    with open(ROOT / "data/petstores-dogparks.csv", newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if not r.get("Name"):
                continue
            name = r["Name"].strip()
            kind = TYPE_FROM_CSV[r["Type"].strip()]

            amen = []
            if kind == "park":
                # Every dog park here is an off-leash area; that is the point.
                amen.append("offleash")
                if yes(r["Water"]):
                    amen.append("water")
                if yes(r["Shade"]):
                    amen.append("shade")
                if yes(r["Fenced"]):
                    amen.append("fenced")
                if yes(r["Separate Small/Large Areas"]):
                    amen.append("smalldog")
            else:
                if yes(r["Self-Serve Dog Wash"]):
                    amen.append("wash")
                if yes(r["Raw Food / Fresh Treats"]):
                    amen.append("raw")

            blurb = []
            if kind == "park":
                surface = r["Surface"].strip()
                if surface and surface != "N/A":
                    blurb.append(sentence(f"Surface: {surface}"))
                if not yes(r["Water"]):
                    blurb.append("Bring your own water.")
            else:
                for col in ("Self-Serve Dog Wash", "Raw Food / Fresh Treats"):
                    v = r[col].strip()
                    if "-" in v and yes(v):
                        blurb.append(sentence(v.split("-", 1)[1].strip()))
            for note in r["Notes"].split(";"):
                note = note.strip()
                if note and not NOISE.match(note):
                    blurb.append(sentence(note))

            # A park earns the amber paw when it has the full kit: fenced, a
            # separate small-dog area, shade and water.
            featured = kind == "park" and {"fenced", "smalldog", "shade", "water"} <= set(amen)
            rows.append(dict(
                name=clean(name), type=kind, friendly="full", amen=amen,
                addr=r["Location"].strip(), rating=num(r["Google Rating"]),
                reviews=num(r["Google Reviews"]), fee=None,
                blurb=" ".join(b for b in blurb if b),
                featured=featured, key=name,
            ))
    return rows


def render(places):
    unmatched = set(BY_PLACE) - {p["key"] for p in places}
    if unmatched:
        raise SystemExit(f"Photos reference unknown places: {sorted(unmatched)}")
    out = []
    for i, p in enumerate(places, start=1):
        if p["key"] not in COORDS:
            raise SystemExit(f"No coordinates for {p['key']!r} — add it to tools/coordinates.json")
        lat, lng = COORDS[p["key"]]
        fields = [
            f"id:{i}", f"name:{js(p['name'])}", f"type:{js(p['type'])}",
            f"city:{js(city_of(p['addr']))}", f"addr:{js(p['addr'])}",
            f"lat:{lat}", f"lng:{lng}",
        ]
        if p["rating"] is not None:
            fields.append(f"rating:{p['rating']:g}")
            fields.append(f"reviews:{int(p['reviews'] or 0)}")
        fields += [f"friendly:{js(p['friendly'])}", f"amen:{js(p['amen'])}",
                   f"featured:{js(p['featured'])}"]
        if p["fee"]:
            fields.append(f"fee:{js(p['fee'])}")
        photo = BY_PLACE.get(p["key"])
        if photo:
            fields.append(f"photo:{js(photo['slug'])}")
            fields.append(f"alt:{js(photo['alt'])}")
            credit = {"a": photo["author"], "l": photo["license"], "u": photo["source"]}
            fields.append(f"credit:{js(credit)}")
        out.append(" {" + ",".join(fields) + ",\n  blurb:" + js(p["blurb"]) + "}")
    return "const PLACES = [\n" + ",\n".join(out) + "\n];"


def main():
    places = food_and_lodging() + parks_and_stores()
    block = render(places)

    page = ROOT / "index.html"
    src = page.read_text()
    start, end = "/* PLACES:START */", "/* PLACES:END */"
    a, b = src.index(start), src.index(end)
    page.write_text(src[:a] + start + "\n" + block + "\n" + src[b:])

    rated = sum(1 for p in places if p["rating"] is not None)
    by_type = {}
    for p in places:
        by_type[p["type"]] = by_type.get(p["type"], 0) + 1
    print(f"{len(places)} places -> index.html")
    print(f"  with photos: {sum(1 for p in places if p['key'] in BY_PLACE)}")
    print(f"  rated: {rated}   featured: {sum(1 for p in places if p['featured'])}")
    print("  " + "  ".join(f"{k}: {v}" for k, v in sorted(by_type.items())))


if __name__ == "__main__":
    main()
