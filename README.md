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

- **Map** — pannable Leaflet map of California. Pins are colour- and icon-coded: green fill for fully dog-friendly, white with a green outline for patio-only, and a larger amber paw for featured places. Each business type has its own glyph (fork & knife, beer mug, coffee cup, hotel bed, storefront) on pins, filter chips, list cards and the detail view.
- **Search** — autosuggest over 30 California cities and ZIP codes. Selecting an area flies the map there and recalculates every distance. Keyboard-navigable (arrow keys, Enter, Escape).
- **Filters** — business type chips plus a panel for friendliness level, amenities, minimum rating and distance. The options are derived from the data, so a type or amenity nothing has is not offered, and the rating group stays hidden while nothing is rated. The active-filter count shows on the Filters button.
- **Most dog-friendly** — the amber-paw list of featured places, pinned above the main results. It shows the five nearest, with a "Show all" toggle for the rest; the map always shows every featured pin.
- **Detail view** — amenities grid, photo gallery, pet fee and limits for hotels, and a banner spelling out the dog policy.
- **Accessibility** — labelled map pins, ARIA states on every control, focus trapping in modals, Escape-to-dismiss, and `prefers-reduced-motion` support.

## Data

All 56 places are real businesses, imported from `data/dogfriendly-california.csv` — restaurants, bars and hotels across Southern California and the Eastern Sierra (Mammoth, Bishop, Lone Pine). They live at the top of the script in `index.html`, alongside `AREAS`, the cities and ZIP codes the search resolves against.

The design prototype's 14 invented places were removed once real data arrived, along with their mocked reviews. Lazy Dog was kept — it is a real business and appears in the CSV — but its invented rating and reviews are gone.

Three things to know before trusting this data:

- **Nothing has a rating or reviews.** The CSV has none, and attaching invented numbers to real businesses would be fabricating records. Places display "Not rated yet", the detail view says reviews appear once a source is connected, and the minimum-rating filter hides itself until something is actually rated.
- **Coordinates are approximate.** No geocoder was available during the import, so well-known venues sit close to their real position and the rest sit at the centre of the town named in the CSV. Run a geocoding pass before anyone navigates by this. No street addresses were invented — `addr` is the CSV's Location text verbatim.
- **Friendliness was inferred.** California restricts dogs to outdoor areas in food-service venues, so restaurants and bars are marked patio-only unless the CSV says otherwise (Distant Brewing in Mammoth allows dogs indoors). Hotels are marked fully dog-friendly, since dogs are allowed in the rooms. A place is featured — the amber paw list — when it has a real dog menu.

The CSV has no coffee shops or stores, so those two type chips do not currently appear. They come back on their own when matching data is added.

Photos are striped placeholders. Photos and reviews are **not** wired to the Google Places API — that needs an API key and a server-side proxy, since a key can't be safely embedded in a static page. The data structures are shaped so a real source can drop in behind them.

## Design source

`design/` holds the Claude Design handoff this was built from:

- `design/prototype/PawSpots.html` — the original prototype
- `design/chats/` — the design conversation that produced it
- `design/HANDOFF.md` — the handoff bundle's own README

The implementation is pixel-identical to the prototype across the mobile map, mobile sheet, mobile filters, desktop split view and desktop filters. The single intentional visual change is in the detail hero: the prototype's `.d-hero .ph:first-child` rule never matched, because the close button is the first child, which left an empty cell in the grid. That span is now anchored to the photo itself.
