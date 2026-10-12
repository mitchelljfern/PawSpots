# PawSpots

A dashboard for finding dog-friendly places — restaurants, bars, coffee shops, hotels and stores — with clear indicators for whether dogs are welcome **inside and outside** or **on the patio only**.

Built mobile-first: a full-screen map with a slide-up list sheet on phones, and a split list/map layout on desktop (≥1024px).

## Running it

Live at **https://mitchelljfern.github.io/PawSpots/**, served from `main` by GitHub Pages.

Locally, open `index.html` in a browser. There is no build step and no dependencies to install.

It loads three things from CDNs at runtime, so the first load needs a network connection:

- [Leaflet](https://leafletjs.com/) 1.9.4 for the map (subresource-integrity pinned)
- OpenStreetMap raster tiles
- Bricolage Grotesque from Google Fonts

If the Leaflet CDN is unreachable, the map pane says so and the list view keeps working.

## What's in it

- **Map** — pannable Leaflet map of California. Pins are colour- and icon-coded: green fill for fully dog-friendly, white with a green outline for patio-only, and a larger amber paw for featured places. Each type has its own glyph (fork & knife, beer mug, coffee cup, hotel bed, storefront, fire hydrant for dog parks) on pins, filter chips, list cards and the detail view.
- **Search** — autosuggest over 30 California cities and ZIP codes. Selecting an area flies the map there and recalculates every distance. Keyboard-navigable (arrow keys, Enter, Escape).
- **Filters** — business type chips plus a panel for friendliness level, amenities, minimum rating and distance. The options are derived from the data, so a type or amenity nothing has is not offered, and the rating group stays hidden while nothing is rated. The active-filter count shows on the Filters button.
- **Most dog-friendly** — the amber-paw list of featured places, pinned above the main results. It shows the five nearest, with a "Show all" toggle for the rest; the map always shows every featured pin.
- **Amenity icons** — each amenity has its own colour and icon: water bowls blue, dog menu green, shade red, treats orange, off-leash teal, dog beds violet, fencing indigo, small-dog area pink, self-serve wash cyan, raw food amber. Each `.am-*` class sets three custom properties (`--am-fg`, `--am-bg`, `--am-br`) and every surface reads them, so a new amenity needs one CSS rule and one icon.
- **Detail view** — amenities grid, photo gallery, pet fee and limits for hotels, and a banner spelling out the dog policy. The wording follows the place type: patio-only for restaurants, off-leash for parks, dogs-welcome-inside for shops.
- **Photos** — 10 places have a real photo, shown as the card thumbnail and the detail hero. Every photo carries its author and licence in the page, because most are CC BY or CC BY-SA and may only be published with the author credited. The striped placeholders remain everywhere else.
- **Link previews** — favicon, Apple touch icon and a 1200x630 social card, so links unfurl properly in iMessage, Slack, Facebook and X.
- **Park guides** — a Guides tab in the top bar leads to per-park dog guides for California's national and state parks. See [Park guides](#park-guides).
- **Accessibility** — labelled map pins, ARIA states on every control, focus trapping in modals, Escape-to-dismiss, and `prefers-reduced-motion` support.

## Park guides

`guides/` is a second surface: one page per national or state park saying where dogs can and cannot go, dog-legal walks, places to hang out, the rules in plain words, camping and lodging, seasons, wildlife, a packing checklist, nearby vets and the official source. The hub at `guides/index.html` has search, a national/state filter and a dog-friendliness sort. Both the map and the guides carry a Map | Guides tab in the top bar.

The pages are built for phones first: 17px base text with an "Aa" button that steps it up two sizes (remembered per device), 44px tap targets, a sticky jump bar between sections, status words next to every colour so nothing relies on colour alone, a packing checklist that remembers ticks, native share sheet, print styles, and `prefers-reduced-motion` support.

### Editing or adding a guide

Each guide is one JSON file in `data/guides/`; the format is documented in `data/guides/SCHEMA.md` and `yosemite-national-park.json` is the model. The HTML under `guides/<slug>/` and `sitemap.xml` are generated. Don't hand-edit them; edit the JSON and re-run:

```
python3 tools/build-guides.py
```

The builder validates every file (required fields, the six at-a-glance keys in order, a photo with credit) and fails loudly on a bad one. `guides/guides.css` and `guides/guides.js` are hand-written and shared by every page.

### Guide photos

Hero images, card thumbnails and the social-sharing card for each guide are hotlinked from [Unsplash](https://unsplash.com) at the sizes the page needs, which is what Unsplash asks for; nothing is downloaded. Each JSON `photo` block holds the `urls.raw` link plus the photographer's name and profile, and the page credits them under the hero. The guides hub uses `data/guides/hub-photo.json` for its own share image. Pick a photo of the park itself, landscape, at least 3000px wide.

### Accuracy

Rules were researched in October 2026 from the official NPS and California State Parks pages and recent third-party guides, by web search. Where sources disagree the text says so. Every page ends with the official pet-rules link and a "check before you go" box, because superintendents can close areas to dogs at any time. Fees and hotel pet policies are the least stable facts; treat them as "about" and confirm when booking.

## Data

All 79 places are real, imported from two CSVs in `data/`:

- `dogfriendly-california.csv` — 32 restaurants and bars, 23 hotels
- `petstores-dogparks.csv` — 16 dog parks, 8 pet stores

77 of the 79 carry a real Google rating and review count; the two exceptions (Mammoth Lakes Community Dog Park, Woofpak Pet Kitchen) are not yet rated on Google and show "Not rated yet".

### Rebuilding the data

`index.html` holds the places inline, between the `PLACES:START` and `PLACES:END` markers. Don't hand-edit that block — edit the CSVs and re-run:

```
python3 tools/import-places.py
```

The importer holds every mapping decision from CSV column to app field, so the reasoning is reviewable rather than buried in the data. Worth knowing:

- **Coordinates come from `tools/coordinates.json`, and they are approximate.** No geocoder was reachable from the build environment, so they were derived from the CSV street addresses by hand — close for well-known venues and identifiable streets, town-centre for the rest. Replace that file wholesale with real geocoder output before anyone navigates by this; the importer reads nothing else for position.
- **Friendliness is inferred.** California restricts dogs to outdoor areas in food-service venues, so restaurants and bars are patio-only unless the row says dogs go inside (Distant Brewing). Hotels, parks and shops are marked dogs-allowed-throughout.
- **"Partial" is not "Yes".** A partially shaded patio doesn't earn the shade badge — only an explicit Yes does.
- **Featured** — the amber paw list — means a real dog menu, or a dog park with the full kit: fenced, separate small-dog area, shade and water.
- **Notes are filtered.** Fragments where the spreadsheet talks about itself ("Rating shown is the Irvine location", "Listed on Google as…") are dropped; caveats a visitor would want ("verify before visiting", "seasonal") are kept.

### Photos

Ten places have a photo. Sources, credits and licences live in `tools/photos.json`, keyed by a slug whose `place` must match a Name in the CSVs exactly — the importer fails loudly if it doesn't, so a renamed place can't silently lose its picture.

**The credits are load-bearing.** Most of these images are CC BY or CC BY-SA, which permit publication only with the author credited, so the credit travels with the photo into the page and renders under every hero. Don't strip it. `photos/ATTRIBUTIONS.txt` keeps the original notice as delivered.

To add or replace photos: drop the files in a directory, add entries to `tools/photos.json`, then

```
python3 tools/build-photos.py <source-dir>   # writes photos/<slug>.jpg + <slug>-thumb.jpg
python3 tools/import-places.py               # links them into index.html
```

`build-photos.py` exists because the originals average ~350 KB, which is silly for an 86px card thumbnail. It writes a 240x240 crop for cards and a version bounded to 1200x800 for the hero: 132 KB of thumbnails on first paint, with the heroes loaded only when a detail opens.

### Icons and the social card

`favicon.svg` is the source of truth for the icon. `og.png` is rendered from `tools/og-image.html`. Both rasterise via

```
node tools/build-assets.mjs        # writes og.png, apple-touch-icon.png, favicon-32.png
```

The `og:image` URL in `index.html` is absolute and points at `pawspots.netlify.app`. It has to be — a relative URL yields no preview at all. If the site moves, update the `og:*`, `twitter:*` and canonical tags together.

Photos beyond those ten are striped placeholders.

## Design source

`design/` holds the Claude Design handoff this was built from:

- `design/prototype/PawSpots.html` — the original prototype
- `design/chats/` — the design conversation that produced it
- `design/HANDOFF.md` — the handoff bundle's own README

The implementation is pixel-identical to the prototype across the mobile map, mobile sheet, mobile filters, desktop split view and desktop filters. The single intentional visual change is in the detail hero: the prototype's `.d-hero .ph:first-child` rule never matched, because the close button is the first child, which left an empty cell in the grid. That span is now anchored to the photo itself.
