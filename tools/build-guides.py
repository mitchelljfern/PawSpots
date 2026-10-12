#!/usr/bin/env python3
"""Render the park guides.

Reads every data/guides/*.json (format: data/guides/SCHEMA.md) and writes

    guides/index.html            the hub: search, filter, every guide card
    guides/<slug>/index.html     one page per park
    sitemap.xml                  home + hub + every guide

Run from anywhere:  python3 tools/build-guides.py
No dependencies. The pages link guides/guides.css and guides/guides.js, which
are hand-written and not touched here.
"""
import glob
import html
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "guides")
OUT = os.path.join(ROOT, "guides")
SITE = "https://pawspots.netlify.app"

# ----------------------------------------------------------------- helpers
def esc(s):
    return html.escape(str(s), quote=True)

def attr(s):
    return html.escape(str(s), quote=True)

def img(raw, w, h=None, q=80):
    """Unsplash hotlink with the imgix params we want. raw already has ixid."""
    p = f"&auto=format&fit=crop&w={w}&q={q}"
    if h:
        p += f"&h={h}"
    return raw + p

def maps_url(q):
    from urllib.parse import quote_plus
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(q)

# ----------------------------------------------------------------- icons
PAW = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><ellipse cx="12" cy="15.8" rx="5.1" ry="4.3"/><circle cx="5.9" cy="10.8" r="2.1"/><circle cx="9.9" cy="7.6" r="2.25"/><circle cx="14.1" cy="7.6" r="2.25"/><circle cx="18.1" cy="10.8" r="2.1"/></svg>'
LOGO_PAW = '<svg width="18" height="18" viewBox="0 0 24 24" fill="#fff" aria-hidden="true"><ellipse cx="12" cy="15.8" rx="5.1" ry="4.3"/><circle cx="5.9" cy="10.8" r="2.1"/><circle cx="9.9" cy="7.6" r="2.25"/><circle cx="14.1" cy="7.6" r="2.25"/><circle cx="18.1" cy="10.8" r="2.1"/></svg>'

def ic(name, size=20, sw=2.1):
    paths = {
        "map": '<path d="M12 21s-7-5.5-7-11a7 7 0 0 1 14 0c0 5.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
        "book": '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5V5.5M8 7h8M8 11h6"/>',
        "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
        "x": '<path d="M6 6l12 12M18 6 6 18"/>',
        "check": '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
        "minus": '<path d="M6 12h12"/>',
        "ban": '<circle cx="12" cy="12" r="8.5"/><path d="m6.5 6.5 11 11"/>',
        "trail": '<path d="M5 20c2-4 2-8 5-10s2-6 6-7"/><path d="M13 20c1-2 1-4 3-5s3-1 4-2"/><circle cx="7" cy="5" r="1.6"/>',
        "tent": '<path d="M3.5 20 12 4l8.5 16z"/><path d="M12 20v-7l-3.5 7M12 13l3.5 7"/>',
        "bed": '<path d="M3 18V8M3 14h18v4M3 11h8V8h7a3 3 0 0 1 3 3v3"/>',
        "water": '<path d="M3 15c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5M3 19c2 0 2-1.5 4-1.5s2 1.5 4 1.5 2-1.5 4-1.5 2 1.5 4 1.5M12 4s4 4.5 4 7a4 4 0 0 1-8 0c0-2.5 4-7 4-7z"/>',
        "leash": '<circle cx="7" cy="7" r="3"/><path d="M9.5 8.5C13 11 15 14 15 18.5a2.5 2.5 0 0 1-5 0"/>',
        "ticket": '<path d="M3 9V6h18v3a2 2 0 0 0 0 4v3H3v-3a2 2 0 0 0 0-4zM10 6v12"/>',
        "flag": '<path d="M5 21V4M5 4h11l-2 4 2 4H5"/>',
        "pin": '<path d="M12 21s-7-5.5-7-11a7 7 0 0 1 14 0c0 5.5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
        "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
        "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
        "warn": '<path d="M12 3 2.5 20h19z"/><path d="M12 10v4M12 17h.01"/>',
        "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
        "bear": '<circle cx="7" cy="7" r="2.5"/><circle cx="17" cy="7" r="2.5"/><path d="M5.5 13a6.5 6.5 0 0 1 13 0v2a6.5 6.5 0 0 1-13 0z"/><circle cx="12" cy="15" r="1.6"/>',
        "bag": '<path d="M6 8h12l1 13H5zM9 8V6a3 3 0 0 1 6 0v2"/>',
        "cross": '<path d="M12 7v10M7 12h10"/><rect x="3" y="3" width="18" height="18" rx="4"/>',
        "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
        "share": '<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="m8.2 10.8 7.6-4.6M8.2 13.2l7.6 4.6"/>',
        "up": '<path d="m6 14 6-6 6 6"/>',
        "ext": '<path d="M14 4h6v6M20 4l-9 9M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/>',
        "home": '<path d="m3 11 9-7 9 7v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    }
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>')

GLANCE = {
    "trails":  ("Hiking trails", "trail"),
    "camping": ("Camping", "tent"),
    "lodging": ("Lodging in park", "bed"),
    "water":   ("Beaches & water", "water"),
    "leash":   ("Leash", "leash"),
    "fee":     ("Fees", "ticket"),
}
STATUS_WORD = {"yes": "Yes", "some": "Some", "no": "No", "rule": "Rule", "info": "Info"}
STATUS_ICON = {"yes": "check", "some": "minus", "no": "ban"}
SCORE_WORD = {1: "Very limited", 2: "Limited", 3: "Moderate", 4: "Good", 5: "Excellent"}

def paws(score):
    out = []
    for i in range(1, 6):
        out.append(PAW if i <= score else PAW.replace('<svg ', '<svg class="off" '))
    return f'<span class="paws" aria-hidden="true">{"".join(out)}</span>'

def score_html(g, with_of=True):
    s = int(g["score"])
    label = g.get("scoreLabel") or SCORE_WORD[s]
    of = f' <span class="of">{s} of 5</span>' if with_of else ""
    return (f'<span class="score s{s}">{paws(s)}<span class="lab">{esc(label)}</span>{of}'
            f'<span class="sr-only">Dog-friendliness {s} out of 5, {esc(label)}</span></span>')

# ----------------------------------------------------------------- validation
REQUIRED = ["slug", "name", "shortName", "type", "designation", "region", "nearestTowns", "tagline",
            "summary", "score", "verdict", "photo", "glance", "allowed", "notAllowed", "hikes",
            "hangouts", "rules", "stay", "seasons", "wildlife", "checklist", "vets", "sources",
            "official", "verified"]

def validate(g, path):
    missing = [k for k in REQUIRED if k not in g]
    if missing:
        sys.exit(f"{path}: missing {missing}")
    if g["type"] not in ("national", "state"):
        sys.exit(f"{path}: type must be national or state")
    if not 1 <= int(g["score"]) <= 5:
        sys.exit(f"{path}: score must be 1-5")
    keys = [t["key"] for t in g["glance"]]
    if keys != list(GLANCE):
        sys.exit(f"{path}: glance keys must be {list(GLANCE)}, got {keys}")
    for t in g["glance"]:
        if t["status"] not in STATUS_WORD:
            sys.exit(f"{path}: bad glance status {t['status']}")
    for k in ("raw", "author", "authorUrl", "link", "alt"):
        if not g["photo"].get(k):
            sys.exit(f"{path}: photo.{k} missing")
    if not re.fullmatch(r"[a-z0-9-]+", g["slug"]) or g["slug"] != os.path.basename(path)[:-5]:
        sys.exit(f"{path}: slug must match the file name")

# ----------------------------------------------------------------- shell
def head(title, desc, url, image, image_alt, rel, extra=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{attr(desc)}">
<meta name="color-scheme" content="light">
<meta name="theme-color" content="#317a45">
<link rel="icon" href="{rel}favicon.svg" type="image/svg+xml">
<link rel="icon" href="{rel}favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="{rel}apple-touch-icon.png">
<link rel="canonical" href="{attr(url)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="PawSpots">
<meta property="og:url" content="{attr(url)}">
<meta property="og:title" content="{attr(title)}">
<meta property="og:description" content="{attr(desc)}">
<meta property="og:image" content="{attr(image)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{attr(image_alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{attr(title)}">
<meta name="twitter:description" content="{attr(desc)}">
<meta name="twitter:image" content="{attr(image)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}guides/guides.css">
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""

def topbar(rel, current):
    cur_map = ' aria-current="page"' if current == "map" else ""
    cur_g = ' aria-current="page"' if current == "guides" else ""
    return f"""<header class="topbar">
  <a class="logo" href="{rel}"><span class="mark">{LOGO_PAW}</span><span>PawSpots</span></a>
  <nav class="nav" aria-label="Site">
    <a href="{rel}"{cur_map}>{ic('map', 16)}Map</a>
    <a href="{rel}guides/"{cur_g}>{ic('book', 16)}Guides</a>
  </nav>
  <button class="textsize" id="textsize" type="button" aria-pressed="false" aria-label="Text size. Tap to change.">Aa</button>
</header>
"""

def foot(rel):
    return f"""<footer class="sitefoot">
  <p>Park rules change. Every guide links to the official page, and the dates on each page say when it was last checked. <a href="{rel}">Back to the PawSpots map</a>.</p>
  <p>Photos from <a href="https://unsplash.com/?utm_source=pawspots&amp;utm_medium=referral" rel="noopener">Unsplash</a>, credited on each page.</p>
</footer>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script src="{rel}guides/guides.js" defer></script>
</body>
</html>
"""

# ----------------------------------------------------------------- guide page
def section(id_, title, icon, colour=""):
    cls = f' class="{colour}"' if colour else ""
    return f'<section class="sec" id="{id_}" aria-labelledby="{id_}-h"><h2 id="{id_}-h"{cls}><span class="ic">{ic(icon, 20)}</span>{esc(title)}</h2>'

def guide_page(g):
    rel = "../../"
    url = f"{SITE}/guides/{g['slug']}/"
    p = g["photo"]
    og = img(p["raw"], 1200, 630)
    title = f"Dogs at {g['shortName']}: where they can go, camping and rules"
    desc = f"{g['tagline']} {g['verdict']}"
    srcset = ", ".join(f"{img(p['raw'], w, round(w*9/16))} {w}w" for w in (640, 960, 1400, 2000))
    towns = ", ".join(g["nearestTowns"])
    s = int(g["score"])
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": title, "description": desc, "image": og, "dateModified": date.today().isoformat(),
        "author": {"@type": "Organization", "name": "PawSpots"},
        "publisher": {"@type": "Organization", "name": "PawSpots"},
        "mainEntityOfPage": url,
        "about": {"@type": "Park", "name": g["name"]},
    })
    crumbs = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "PawSpots", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Park guides", "item": SITE + "/guides/"},
            {"@type": "ListItem", "position": 3, "name": g["name"], "item": url},
        ]})
    extra = f'<script type="application/ld+json">{ld}</script>\n<script type="application/ld+json">{crumbs}</script>\n'

    h = [head(title + " | PawSpots Guides", desc, url, og, p["alt"], rel, extra), topbar(rel, "guides")]
    h.append(f"""<main id="main">
<div class="hero">
  <img src="{attr(img(p['raw'], 1400, 788))}" srcset="{attr(srcset)}" sizes="100vw" alt="{attr(p['alt'])}" fetchpriority="high" decoding="async">
  <div class="in">
    <span class="badge {g['type']}">{esc(g['designation'])}</span>
    <h1>{esc(g['name'])}</h1>
    <p class="tagline">{esc(g['tagline'])}</p>
  </div>
</div>
<div class="wrap">
  <p class="credit">Photo by <a href="{attr(p['authorUrl'])}?utm_source=pawspots&amp;utm_medium=referral" rel="noopener">{esc(p['author'])}</a> on <a href="https://unsplash.com/?utm_source=pawspots&amp;utm_medium=referral" rel="noopener">Unsplash</a></p>

  <section class="card verdict" aria-labelledby="verdict-h">
    <h2 id="verdict-h" class="sr-only">Dog-friendliness</h2>
    {score_html(g)}
    <p>{esc(g['verdict'])}</p>
    <p class="towns">{ic('pin', 15)} Nearest towns: {esc(towns)}</p>
  </section>

  <section class="glance" aria-labelledby="glance-h">
    <h2 id="glance-h">At a glance</h2>
    <ul class="tiles">""")
    for t in g["glance"]:
        label, icon = GLANCE[t["key"]]
        st = t["status"]
        word = STATUS_WORD[st]
        mark = ic(STATUS_ICON[st], 18, 2.6) if st in STATUS_ICON else ""
        h.append(f"""
      <li class="tile {st}"><span class="ic">{ic(icon, 20)}</span><span class="lab">{esc(label)}</span><span class="st">{mark}{esc(word) if st in STATUS_ICON else esc(t['note'])}</span>{f'<span class="nt">{esc(t["note"])}</span>' if st in STATUS_ICON else ''}</li>""")
    h.append("""
    </ul>
  </section>
</div>
""")
    # jump nav
    jumps = [("go", "Where dogs can go"), ("no", "Not allowed"), ("walks", "Walks"), ("hangout", "Hang out"),
             ("rules", "Rules"), ("stay", "Camping & stay"), ("seasons", "Seasons"), ("wildlife", "Wildlife"),
             ("pack", "Packing list"), ("vets", "Vets"), ("sources", "Sources")]
    h.append('<nav class="jump" aria-label="Sections"><ul>' + "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in jumps) + "</ul></nav>\n")
    h.append('<div class="wrap">\n')

    # summary + allowed
    h.append(section("go", "Where dogs can go", "check"))
    h.append(f'<p class="lede">{esc(g["summary"])}</p><ul class="ynlist yes">')
    for a in g["allowed"]:
        h.append(f'<li><span class="mk">{ic("check", 16, 2.8)}</span><div><b>{esc(a["name"])}</b><p>{esc(a["detail"])}</p></div></li>')
    h.append("</ul></section>\n")

    # not allowed
    h.append(section("no", "Where dogs are not allowed", "ban", "red"))
    h.append('<ul class="ynlist no">')
    for a in g["notAllowed"]:
        h.append(f'<li><span class="mk">{ic("x", 16, 2.8)}</span><div><b>{esc(a["name"])}</b><p>{esc(a["detail"])}</p></div></li>')
    h.append("</ul></section>\n")

    # hikes
    h.append(section("walks", "Dog-friendly walks", "trail"))
    if g["hikes"]:
        h.append('<p class="lede">Every walk here is one your dog is allowed on. Distances are round trip unless it says loop.</p><ul class="hikes">')
        for k in g["hikes"]:
            diff = k.get("difficulty", "")
            dcls = diff.lower().split()[0] if diff else ""
            h.append(f"""<li class="card hike"><h3>{esc(k['name'])}</h3>
  <div class="stats"><span class="stat">{ic('trail', 14)}{esc(k.get('distance',''))}</span><span class="stat {dcls}">{esc(diff)}</span><span class="stat">{esc(k.get('surface',''))}</span></div>
  <p>{esc(k['why'])}</p>
  <a class="btn small" href="{attr(maps_url(k.get('maps') or k['name'] + ' ' + g['name']))}" target="_blank" rel="noopener">{ic('pin', 16)}Open in Maps</a></li>""")
        h.append("</ul>")
    else:
        h.append(f'<p class="nohike">{ic("warn", 20)} There are no trails open to dogs here. See the hang-out spots below and the nearby alternatives in the camping and stay section.</p>')
    h.append("</section>\n")

    # hangouts
    h.append(section("hangout", "Good places to hang out", "sun"))
    h.append('<ul class="spots">')
    for sp in g["hangouts"]:
        h.append(f'<li><span class="mk">{PAW.replace("<svg ", "<svg width=18 height=18 ")}</span><div><b>{esc(sp["name"])}</b><p>{esc(sp["why"])}</p></div></li>')
    h.append("</ul></section>\n")

    # rules
    h.append(section("rules", "The rules, in plain words", "list"))
    h.append('<ol class="rules">' + "".join(f"<li>{esc(r)}</li>" for r in g["rules"]) + "</ol></section>\n")

    # stay
    st = g["stay"]
    h.append(section("stay", "Camping and places to stay", "tent"))
    h.append('<div class="stay">')
    if st.get("camping"):
        h.append(f'<div><h3>{ic("tent", 18)}Camping with your dog</h3><ul>')
        for c in st["camping"]:
            off = ' class="off"' if c["name"].lower().startswith(("not allowed", "no dogs", "no pets")) else ""
            h.append(f'<li{off}><b>{esc(c["name"])}</b><span>{esc(c["note"])}</span></li>')
        h.append("</ul></div>")
    if st.get("lodging"):
        h.append(f'<div><h3>{ic("bed", 18)}Pet-friendly lodging</h3><ul>')
        for c in st["lodging"]:
            h.append(f'<li><b>{esc(c["name"])}</b><span>{esc(c["note"])}</span></li>')
        h.append("</ul></div>")
    if st.get("boarding"):
        h.append(f'<div><h3>{ic("home", 18)}Boarding and dog-sitting</h3><p class="note">For the parts of the park your dog cannot visit.</p><ul>')
        for c in st["boarding"]:
            h.append(f'<li><b>{esc(c["name"])}</b><span>{esc(c["note"])}</span></li>')
        h.append("</ul></div>")
    h.append("</div></section>\n")

    # seasons
    h.append(section("seasons", "When to go", "clock", "amber"))
    h.append('<ul class="seasons">')
    for se in g["seasons"]:
        lvl = se.get("level", "info")
        icon = {"info": "info", "warn": "warn", "danger": "warn"}[lvl]
        h.append(f'<li class="{lvl}"><span class="mk">{ic(icon, 18)}</span><div><b>{esc(se["title"])}</b><p>{esc(se["detail"])}</p></div></li>')
    h.append("</ul></section>\n")

    # wildlife
    h.append(section("wildlife", "Wildlife and hazards", "bear", "amber"))
    h.append('<ul class="plain">' + "".join(f'<li>{ic("warn", 16)}<span>{esc(w)}</span></li>' for w in g["wildlife"]) + "</ul></section>\n")

    # checklist
    h.append(section("pack", "Packing list", "bag", "blue"))
    h.append('<p class="lede">Tick things off as you pack. Your phone remembers the list.</p><ul class="check">')
    for i, c in enumerate(g["checklist"]):
        h.append(f'<li><label><input type="checkbox"><span>{esc(c)}</span></label></li>')
    h.append("</ul></section>\n")

    # vets
    h.append(section("vets", "If something goes wrong", "cross", "red"))
    h.append('<p class="lede">Nearby vets, from our research. Call ahead, and search for emergency hours.</p><ul class="vets">')
    for v in g["vets"]:
        q = f"{v['name']} {v['town']}"
        h.append(f'<li><div><b>{esc(v["name"])}</b><span>{esc(v["town"])}</span></div><a class="btn small" href="{attr(maps_url(q))}" target="_blank" rel="noopener">{ic("pin", 15)}Map</a></li>')
    h.append("</ul>")
    h.append(f'<a class="btn vetcta" href="{attr(maps_url("emergency vet near " + g["nearestTowns"][0] + " CA"))}" target="_blank" rel="noopener">{ic("search", 18)}Find an emergency vet near {esc(g["nearestTowns"][0])}</a>')
    h.append("</section>\n")

    # sources
    h.append(section("sources", "Sources and when we checked", "link"))
    h.append(f'<p class="lede">Last checked {esc(g["verified"])}.</p><ul class="sources">')
    for src in g["sources"]:
        h.append(f'<li><a href="{attr(src["url"])}" rel="noopener" target="_blank">{esc(src["label"])} {ic("ext", 13)}</a></li>')
    h.append("</ul>")
    h.append(f"""<div class="verify"><b>{ic('warn', 18)} Rules change. Check before you go.</b>
<p>Superintendents can close an area to dogs at any time, for example when birds are nesting or after a fire. The official page is the final word.</p>
<a class="btn small" href="{attr(g['official'])}" target="_blank" rel="noopener">Official pet rules for {esc(g['shortName'])} {ic('ext', 14)}</a></div>
</section>
<div class="pagefoot">
  <button class="btn primary" type="button" data-share="Dogs at {attr(g['shortName'])}: where they can go, camping and rules">{ic('share', 18)}Share this guide</button>
  <a class="btn" href="../">{ic('book', 18)}All park guides</a>
</div>
</div>
</main>
<button class="backtop" id="backtop" type="button" aria-label="Back to top">{ic('up', 20)}</button>
""")
    h.append(foot(rel))
    return "".join(h)

# ----------------------------------------------------------------- hub
HUB_PHOTO = None  # set in main() from hub-photo.json if present

def hub_page(guides):
    rel = "../"
    url = f"{SITE}/guides/"
    n_nat = sum(1 for g in guides if g["type"] == "national")
    n_st = len(guides) - n_nat
    title = "Dog-friendly park guides for California | PawSpots"
    desc = (f"Where dogs can and cannot go in {n_nat} national parks and {n_st} state parks in California: "
            "trails, beaches, campgrounds, lodging and the rules, in plain words.")
    hp = HUB_PHOTO
    og = img(hp["raw"], 1200, 630) if hp else f"{SITE}/og.png"
    og_alt = hp["alt"] if hp else "PawSpots park guides"
    h = [head(title, desc, url, og, og_alt, rel), topbar(rel, "guides")]
    h.append(f"""<main id="main" class="hub">
<section class="hub-hero">
  <div class="wrap">
    <h1>Park guides for dog owners</h1>
    <p>Every park has its own rules, and most of them are confusing. These guides say where your dog can go, where they cannot, and what to do about it. One park per page, written for a phone.</p>
    <form class="searchbox" role="search" onsubmit="return false">
      {ic('search', 20)}
      <label class="sr-only" for="q">Search parks by name, region or town</label>
      <input id="q" type="search" placeholder="Search a park, region or town" autocomplete="off" autocorrect="off" spellcheck="false">
      <button class="clear" id="qclear" type="button" aria-label="Clear search" hidden>{ic('x', 18)}</button>
    </form>
  </div>
</section>
<div class="filters">
  <div class="wrap" role="group" aria-label="Filter guides">
    <button class="chip" type="button" data-type="all" aria-pressed="true">All <span class="n">{len(guides)}</span></button>
    <button class="chip" type="button" data-type="national" aria-pressed="false">National parks <span class="n">{n_nat}</span></button>
    <button class="chip" type="button" data-type="state" aria-pressed="false">State parks <span class="n">{n_st}</span></button>
    <div class="sortwrap"><label for="sort">Sort</label><select id="sort"><option value="name">A to Z</option><option value="score">Most dog-friendly</option></select></div>
  </div>
</div>
<div class="wrap">
  <section class="card explain" aria-labelledby="explain-h">
    <h2 id="explain-h">The short version of park rules</h2>
    <ul>
      <li>{ic('check', 18, 2.6)}<span><b>National parks:</b> dogs stay on paved roads, in campgrounds and picnic areas. Trails are almost always off limits.</span></li>
      <li>{ic('check', 18, 2.6)}<span><b>California state parks:</b> the same by default, but each park sets its own exceptions. Some open beaches and fire roads; some ban dogs entirely.</span></li>
      <li>{ic('check', 18, 2.6)}<span><b>Everywhere:</b> a leash of 6 feet or less, never leave the dog alone, and pick up after them.</span></li>
      <li>{ic('check', 18, 2.6)}<span><b>The paw score</b> on each card rates how much of the park your dog can actually enjoy, from 1 (banned) to 5 (most trails and beaches).</span></li>
    </ul>
  </section>
  <p class="count" id="count" aria-live="polite"></p>
  <ul class="grid" id="grid">""")
    for g in sorted(guides, key=lambda x: x["name"]):
        p = g["photo"]
        hay = " ".join([g["name"], g["shortName"], g["designation"], g["region"], g["tagline"]] + g["nearestTowns"])
        src = img(p["raw"], 800, 500)
        srcset = f"{img(p['raw'], 480, 300)} 480w, {img(p['raw'], 800, 500)} 800w, {img(p['raw'], 1200, 750)} 1200w"
        h.append(f"""
    <li><a class="gcard" href="{g['slug']}/" data-type="{g['type']}" data-score="{int(g['score'])}" data-name="{attr(g['name'])}" data-hay="{attr(hay)}">
      <div class="img"><img src="{attr(src)}" srcset="{attr(srcset)}" sizes="(min-width:1100px) 33vw, (min-width:720px) 50vw, 100vw" alt="{attr(p['alt'])}" loading="lazy" decoding="async"><span class="badge {g['type']}">{esc(g['designation'])}</span></div>
      <div class="body"><h2>{esc(g['name'])}</h2><p class="tag">{esc(g['tagline'])}</p>
      <div class="foot">{score_html(g, with_of=False)}<span class="region">{esc(g['region'])}</span></div></div>
    </a></li>""")
    h.append("""
  </ul>
  <div class="empty" id="empty" hidden><b>No parks match</b>Try a park name, a region like "Sierra Nevada", or a town.</div>
</div>
</main>
""")
    h.append(foot(rel))
    return "".join(h)

# ----------------------------------------------------------------- sitemap
def sitemap(guides):
    today = date.today().isoformat()
    rows = [f"<url><loc>{SITE}/</loc><changefreq>weekly</changefreq></url>",
            f"<url><loc>{SITE}/guides/</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq></url>"]
    for g in sorted(guides, key=lambda x: x["slug"]):
        rows.append(f"<url><loc>{SITE}/guides/{g['slug']}/</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq></url>")
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n"

# ----------------------------------------------------------------- main
def main():
    global HUB_PHOTO
    files = sorted(glob.glob(os.path.join(DATA, "*.json")))
    guides = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            g = json.load(fh)
        if os.path.basename(f) == "hub-photo.json":
            HUB_PHOTO = g
            continue
        validate(g, f)
        guides.append(g)
    if not guides:
        sys.exit("no guides found")
    for g in guides:
        d = os.path.join(OUT, g["slug"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(guide_page(g))
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(hub_page(guides))
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(sitemap(guides))
    print(f"wrote {len(guides)} guides, guides/index.html and sitemap.xml")

if __name__ == "__main__":
    main()
