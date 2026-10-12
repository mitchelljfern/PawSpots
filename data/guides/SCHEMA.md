# Guide data format

Each file in `data/guides/` is one park guide. `tools/build-guides.py` renders
them into `guides/<slug>/index.html` plus the hub at `guides/index.html`.

Write for a phone screen and for every age: short sentences, plain words,
no jargon. Every fact must come from the official park page or a reliable
recent source; when sources disagree, say so in the text ("check before you go").

```jsonc
{
  "slug": "yosemite-national-park",          // folder name, lowercase, hyphens
  "name": "Yosemite National Park",
  "shortName": "Yosemite",
  "type": "national",                         // "national" | "state"
  "designation": "National Park",             // shown as a badge: National Park, National Seashore,
                                              // National Recreation Area, State Park, State Beach,
                                              // State Natural Reserve, State Historic Park ...
  "region": "Sierra Nevada",                  // Sierra Nevada | Desert | Central Coast | Bay Area |
                                              // North Coast | Southern California | Far North | Lake Tahoe
  "nearestTowns": ["Mariposa", "Oakhurst"],
  "tagline": "Huge views from paved paths — but almost no trails.",   // <= 70 chars, card subtitle
  "summary": "Two or three sentences, from a dog owner's point of view.",
  "score": 2,                                 // 1-5 dog-friendliness
  "scoreLabel": "Limited",                    // 1 Very limited, 2 Limited, 3 Moderate, 4 Good, 5 Excellent
  "verdict": "One sentence: should you bring the dog, and for what kind of trip?",

  "photo": {                                  // from the Unsplash search tool: pick a landscape,
    "id": "ndN00KmbJ1c",                      // iconic view of THIS park, no close-up faces
    "raw": "https://images.unsplash.com/photo-...?ixid=...&ixlib=rb-4.1.0",   // urls.raw exactly
    "alt": "El Capitan rising above a meadow in Yosemite Valley",
    "author": "Adam Kool",
    "authorUrl": "https://unsplash.com/@adamkool",
    "link": "https://unsplash.com/photos/el-capitan-in-yosemite-national-park-ndN00KmbJ1c"
  },

  "glance": [                                 // exactly these six, in this order
    {"key": "trails",  "status": "no",   "note": "Paved paths and one meadow loop only"},
    {"key": "camping", "status": "yes",  "note": "Most drive-in campgrounds"},
    {"key": "lodging", "status": "no",   "note": "No pets in any in-park lodge"},
    {"key": "water",   "status": "some", "note": "Riverbanks reachable from paved paths"},
    {"key": "leash",   "status": "rule", "note": "6 ft max, at all times"},
    {"key": "fee",     "status": "info", "note": "No pet fee; $35 park entry per car"}
  ],
  // status: "yes" (green) | "some" (amber) | "no" (red) | "rule" | "info" (neutral)

  "allowed":    [{"name": "Paved paths in Yosemite Valley", "detail": "One or two sentences."}],
  "notAllowed": [{"name": "Every unpaved trail", "detail": "..."}],

  "hikes": [                                  // 2-6 real dog-legal walks; if none, leave []
    {"name": "Wawona Meadow Loop", "distance": "3.5 mi loop", "difficulty": "Easy",
     "surface": "Dirt road", "why": "Why it is good with a dog.", "maps": "Wawona Meadow Loop Trail, Yosemite"}
  ],                                          // maps = text for a Google Maps search
  "hangouts": [{"name": "Cook's Meadow", "why": "..."}],   // picnic spots, viewpoints, beaches, riverbanks

  "rules": ["Leash no longer than 6 feet, at all times.", "..."],   // 5-9 plain-language rules

  "stay": {
    "camping": [{"name": "Upper Pines Campground", "note": "Reserve on Recreation.gov; pets OK"}],
    "lodging": [{"name": "Tenaya at Yosemite (Fish Camp)", "note": "Pet rooms with a fee"}],
    "boarding": [{"name": "Tenaya at Yosemite kennel", "note": "Day boarding, reserve ahead"}]
  },

  "seasons": [                                // level: "info" | "warn" | "danger"
    {"title": "Summer heat", "level": "warn", "detail": "..."}
  ],
  "wildlife": ["Black bears — store dog food in bear lockers, never in the car."],

  "checklist": ["Extra water and a bowl", "..."],   // 5-8 items, park-specific where possible

  "vets": [{"name": "Oakhurst Veterinary Hospital", "town": "Oakhurst"}],   // 1-3; name + town only

  "sources": [{"label": "NPS — Pets in Yosemite", "url": "https://www.nps.gov/yose/planyourvisit/pets.htm"}],
  "official": "https://www.nps.gov/yose/planyourvisit/pets.htm",   // the one link to check rules
  "verified": "October 2026"
}
```
