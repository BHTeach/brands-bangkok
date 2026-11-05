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

## Website structure

Location profiles focus on shops, transport and neighbourhoods. They do not display rental prices or fixed pop-up packages. Business services are introduced on planning.html, with a separate rental.html page for rates. A profile's Retail space enquiries link can preselect that location only.

The rental page requires a season, length of stay, size and setup before showing an estimate. It has no preset September or 14-day choice. Options:
- Seasons: Feb–Apr, May–Jul, Aug–Oct, Nov–Jan.
- Stays: 7, 14 or 28 days.
- Space: 20, 40 or 60 square metres.
- Setup: space only, retail setup, or brand display.
- Optional stock storage and printed brand signs.

Rental math in assets/rental.js uses the previous per-venue 14-day Aug–Oct rent and reference area as its basis. Rent scales by area, days and seasonal factor (1.1, 0.9, 1, 1.3 respectively). Setup is charged once, using 0, 1 or 1.5 times the area-scaled reference setup price. Storage is THB 300/day; signs are THB 6,000 once. The deposit scales with area and is shown separately. Rent, setup and deposits are rounded to the nearest THB 100. Total before opening includes the deposit; taxes and stated operating costs remain excluded.

## Printable pack

Two separate six-page A4 booklets are available, so rental information can be handed out for the second part of lesson 1:

- print/brands-bangkok-locations.pdf — overview, business services and five full location profiles, with photographs and credits.
- print/brands-bangkok-rental-rates.pdf — options and terms, followed by a rate page for each location. Every combination of season, 7/14/28-day stay and 20/40/60 m² space is listed; setup, extras and refundable deposits are separate. The dated THB–JPY rate is printed.

print-pack.html contains both booklets. print-locations.html and print-rental.html contain each separately. These pages retain the access gate and are unlinked from the student website navigation; print and PDF controls appear only on these resource pages. PDF assets are static public files, like other repository assets.

build.mjs also runs build-print.mjs, which uses venues.json, exchange-rate.json and the actual estimator in assets/rental.js to produce the HTML and print/print-data.json. This avoids a second set of pricing formulas.

After changing venue data, prices or the exchange rate, rebuild both HTML and PDFs and commit the generated files:

~~~sh
node build.mjs
python -m pip install reportlab Pillow
python scripts/build-print-pdf.py
~~~

The PDF script uses Arial and Georgia from C:/Windows/Fonts. On other systems, set BB_FONT_DIR to a directory with the same font filenames (see the script). PDF generation is separate so ordinary website rebuilds remain dependency-free.

## Teacher and research notes

This is an English communication resource for British Hills. Brands Bangkok is a fictional business, not a real leasing agency or venue partner. Real location, retail and transport information was checked against the linked official sources on 5 November 2026. All package prices, floor areas, setup amounts, deposits and commercial terms are fictional course material and do not represent real offers or available space. No booking, enquiry or payment is sent to a real venue.

The website deliberately uses the voice of a business promotion site. Simulation notices and teaching instructions are not shown to students. It does not rank locations, assign research roles or provide a model recommendation.

Source URLs and photo credits remain available in sources.html and venues.json. Photographs are resized/cropped and retain the licences shown in the credits.

## Privacy

The password form runs locally and makes no authentication request. There are no accounts, enquiry forms, analytics, tracking cookies or student records. GitHub hosting and external source websites have their own technical access logging and privacy practices.

## Currency display

The estimate includes a Currency Converter for THB and JPY. All line items and the total switch together; underlying prices remain in THB so repeated switching does not compound rounding. JPY display rounds to whole yen.

The fixed rate in exchange-rate.json is 1 THB = JPY 4.72877, checked from Wise on 5 November 2026. It is a dated rate snapshot, not a continuously refreshed feed. The displayed rate, date and source come from that same file. The printable booklets use this same dated rate. To refresh it, update exchange-rate.json and rebuild the site.
