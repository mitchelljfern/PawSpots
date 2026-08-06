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

- **Map** — pannable Leaflet map of Orange County. Pins are colour- and icon-coded: green fill for fully dog-friendly, white with a green outline for patio-only, and a larger amber paw for featured places. Each business type has its own glyph (fork & knife, beer mug, coffee cup, hotel bed, storefront) on pins, filter chips, list cards and the detail view.
- **Search** — autosuggest over Orange County cities and ZIP codes. Selecting an area flies the map there and recalculates every distance. Keyboard-navigable (arrow keys, Enter, Escape).
- **Filters** — business type chips plus a panel for friendliness level, amenities (dog menu, water bowls, treats, off-leash area, shaded patio, dog beds), minimum rating and distance. The active-filter count shows on the Filters button.
- **Most dog-friendly** — the amber-paw list of featured places, pinned above the main results.
- **Detail view** — amenities grid, photo gallery, reviews, and a banner spelling out the dog policy.
- **Accessibility** — labelled map pins, ARIA states on every control, focus trapping in modals, Escape-to-dismiss, and `prefers-reduced-motion` support.

## Data

All data lives at the top of the script in `index.html`. There are 70 places, from two sources:

- **54 real California places**, imported from `data/dogfriendly-california.csv` — restaurants, bars and hotels across Southern California and the Eastern Sierra (Mammoth, Bishop, Lone Pine).
- **16 invented demo places** in Orange County, from the original design prototype. These are the ones carrying ratings and reviews.

`AREAS` holds the cities and ZIP codes the search resolves against; `REVIEWS` holds the mocked reviews.

Three things to know before trusting this data:

- **The real places have no ratings and no reviews.** The CSV has none, and attaching invented numbers to real businesses would be fabricating records. They display "Not rated yet" until a reviews source is connected. The mocked "via Google" reviews only ever appear on the invented demo places.
- **Coordinates are approximate.** No geocoder was available during the import, so well-known venues sit close to their real position and the rest sit at the centre of the town named in the CSV. Run a geocoding pass before anyone navigates by this. No street addresses were invented — `addr` is the CSV's Location text verbatim.
- **Friendliness was inferred.** California restricts dogs to outdoor areas in food-service venues, so restaurants and bars are marked patio-only unless the CSV says otherwise (Distant Brewing in Mammoth allows dogs indoors). Hotels are marked fully dog-friendly, since dogs are allowed in the rooms. A place is featured — the amber paw list — when it has a real dog menu.

Photos are striped placeholders. Photos and reviews are **not** wired to the Google Places API — that needs an API key and a server-side proxy, since a key can't be safely embedded in a static page. The data structures are shaped so a real source can drop in behind them.

## Design source

`design/` holds the Claude Design handoff this was built from:

- `design/prototype/PawSpots.html` — the original prototype
- `design/chats/` — the design conversation that produced it
- `design/HANDOFF.md` — the handoff bundle's own README

The implementation is pixel-identical to the prototype across the mobile map, mobile sheet, mobile filters, desktop split view and desktop filters. The single intentional visual change is in the detail hero: the prototype's `.d-hero .ph:first-child` rule never matched, because the close button is the first child, which left an empty cell in the grid. That span is now anchored to the photo itself.
