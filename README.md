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
- **Accessibility** — labelled map pins, ARIA states on every control, focus trapping in modals, Escape-to-dismiss, and `prefers-reduced-motion` support.

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

Photos are striped placeholders. Photos and reviews are **not** wired to the Google Places API — that needs an API key and a server-side proxy, since a key can't be safely embedded in a static page. The data structures are shaped so a real source can drop in behind them.

## Design source

`design/` holds the Claude Design handoff this was built from:

- `design/prototype/PawSpots.html` — the original prototype
- `design/chats/` — the design conversation that produced it
- `design/HANDOFF.md` — the handoff bundle's own README

The implementation is pixel-identical to the prototype across the mobile map, mobile sheet, mobile filters, desktop split view and desktop filters. The single intentional visual change is in the detail hero: the prototype's `.d-hero .ph:first-child` rule never matched, because the close button is the first child, which left an empty cell in the grid. That span is now anchored to the photo itself.
