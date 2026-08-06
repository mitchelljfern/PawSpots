# PawSpots

A dashboard for finding dog-friendly places — restaurants, bars, coffee shops, hotels and stores — with clear indicators for whether dogs are welcome **inside and outside** or **on the patio only**.

Built mobile-first: a full-screen map with a slide-up list sheet on phones, and a split list/map layout on desktop (≥1024px).

## Running it

Open `PawSpots.html` in a browser. There is no build step and no dependencies to install.

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

## Sample data

Everything is currently sample data, defined at the top of the script in `PawSpots.html`:

- `PLACES` — 16 Orange County businesses (including both Lazy Dog locations as featured examples)
- `AREAS` — cities and ZIP codes the search resolves against
- `REVIEWS` — mocked reviews, presented as "via Google"

Photos are striped placeholders. Reviews and photos are **not** wired to the Google Places API — that needs an API key and a server-side proxy, since a key can't be safely embedded in a static page. The data structures are shaped so a real source can drop in behind them.

## Design source

`design/` holds the Claude Design handoff this was built from:

- `design/prototype/PawSpots.html` — the original prototype
- `design/chats/` — the design conversation that produced it
- `design/HANDOFF.md` — the handoff bundle's own README

The implementation is pixel-identical to the prototype across the mobile map, mobile sheet, mobile filters, desktop split view and desktop filters. The single intentional visual change is in the detail hero: the prototype's `.d-hero .ph:first-child` rule never matched, because the close button is the first child, which left an empty cell in the grid. That span is now anchored to the photo itself.
