# Brands Bangkok

A promotional-style website for overseas fashion and retail businesses exploring Bangkok. Educational context and research notes are kept in this repository rather than in the visitor-facing copy.

## Access

Website password: BHFutureLeaders

Every HTML page includes a lightweight client-side gate, including direct links to profiles, sources and the print pack. Successful entry is remembered in sessionStorage for the current tab. The footer's Lock site button ends that access. JavaScript is required; content stays hidden without it.

This is an accidental-visitor deterrent, not secure authentication. GitHub Pages serves static files, the repository is public, and page source and assets remain publicly retrievable. Do not store confidential information here. Pages include noindex metadata to discourage search indexing.

## Hosting

Static HTML, CSS and JavaScript, published from main and /(root) with GitHub Pages. No framework, package installation, API keys or environment variables are needed.

## Editing

Edit venues.json for profile copy. Run `node build.mjs` to rebuild HTML after content or template edits, then commit the generated pages too. Shared design is in assets/style.css; mobile navigation and the separate pack's print action are in assets/site.js. Access logic is in assets/access.js. Photographs are stored in assets/.

## Printable pack

The printable pack remains at print-pack.html as a separate teacher resource. Main site pages have no print buttons or links to the pack. The pack uses the same current profile information as the website and has its own Print all five profiles button.

## Teacher and research notes

This is an English communication resource for British Hills. Brands Bangkok is a fictional business, not a real leasing agency or venue partner. Real location, retail and transport information was checked against the linked official sources on 5 November 2026. All package prices, floor areas, setup amounts, deposits and commercial terms are fictional course material and do not represent real offers or available space. No booking, enquiry or payment is sent to a real venue.

The website deliberately uses the voice of a business promotion site. Simulation notices and teaching instructions are not shown to students. It does not rank locations, assign research roles or provide a model recommendation.

Source URLs and photo credits remain available in sources.html and venues.json. Photographs are resized/cropped and retain the licences shown in the credits.

## Privacy

The password form runs locally and makes no authentication request. There are no accounts, enquiry forms, analytics, tracking cookies or student records. GitHub hosting and external source websites have their own technical access logging and privacy practices.
