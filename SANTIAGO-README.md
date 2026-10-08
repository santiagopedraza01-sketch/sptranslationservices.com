# Santiago Pedraza Castillo — Certified Translation

Four pages plus a shared stylesheet and script. No build step, no framework, no
dependencies except Google Fonts. Host anywhere — Netlify, Vercel, Cloudflare
Pages, GitHub Pages, cPanel. Upload all six files to the same folder.

| File                | Language | URL                          |
|---------------------|----------|------------------------------|
| `index.html`        | Spanish  | `yourdomain.com/`            |
| `traductores.html`  | Spanish  | `yourdomain.com/traductores.html` |
| `en.html`           | English  | `yourdomain.com/en.html`     |
| `translators.html`  | English  | `yourdomain.com/translators.html` |
| `styles.css`        | shared   | every page                   |
| `app.js`            | shared   | every page                   |

Spanish is the default document. `hreflang` alternates are declared in both files,
with `x-default` pointing at the Spanish page, so search engines serve Spanish
speakers the Spanish URL and English speakers the English one.

The switcher sits in the navigation as `ES | EN` (masthead and mobile drawer), and
the Spanish footer also carries an "English" link. They are ordinary links, so they
work without JavaScript and each language has its own indexable URL.

## ⚠ The `archive/` folder — do not upload it

`archive/` holds earlier work, kept for reference only:

- `archive/santiago-translations/` — the first single-page design (different
  palette and structure; superseded).
- `archive/santiago-translations-v2/` — a byte-identical copy of the live site as
  it stood when this folder was created. Verified identical at the time; it will
  drift the moment you edit the real files.

**Upload only the eight files in this folder's root.** If `archive/` goes up with
them, the old site becomes publicly reachable at `yourdomain.com/archive/...`,
which means duplicate content competing with your real pages in search, and an
outdated design anyone can stumble onto. Delete `archive/` before deploying, or
select only the eight root files when you upload.

## Section order

Both home pages run:

| # | Spanish        | English        | Ground |
|---|----------------|----------------|--------|
| — | Portada        | Hero           | ink    |
| 01| Tarifas        | Fees           | bone   |
| 02| El despacho    | The practice   | warm   |
| 03| Servicios      | Services       | bone   |
| 04| Proceso        | Process        | ink    |
| 05| Testimonios    | Testimony      | warm   |
| 06| Pago           | Payment        | ink    |
| 07| Preguntas      | Questions      | bone   |
| 08| Encargo        | Instruction    | ink    |

Fees sits directly below the hero. Testimony sits between Process and Payment so
the page keeps alternating light and dark — Process and Payment are both ink, and
back to back they would read as one undifferentiated dark stretch.

To reorder again: move the whole `<!-- ═══ NAME ═══ -->` comment block, renumber
the `NN — Label` index marks, swap the `section--bone` / `section--warm` /
`section--ink` classes so grounds keep alternating, and update the nav, drawer and
footer lists to match. Payment and Process are written for dark grounds; the rest
are written for light.

## The WhatsApp opening message

Every WhatsApp link carries a `?text=` that pre-fills the visitor's first message.
It is written in **the visitor's own language, not the page's** — an English
speaker reading the Spanish site still opens an English chat, and a Colombian who
clicked through to the English page still writes to you in Spanish.

Order of preference: the browser's `navigator.languages` list, first match wins
(Spanish or English); if neither appears, it falls back to the language of the page
being read. The wording lives in `WA_TEXT` at the top of that block in `app.js`:

```
es: 'Hola Santiago, le escribo desde su sitio web. Quisiera un presupuesto…'
en: "Hello Santiago, I'm writing from your website. I would like a quote…"
```

Both mention the website deliberately, so you can tell a site enquiry from a
referral or a returning client at a glance in WhatsApp.

The `?text=` hard-coded in the HTML stays as the no-JavaScript fallback, in the
page's own language. Only Spanish and English are offered — adding, say,
Portuguese would imply you work in it.

## The WhatsApp direct line

WhatsApp appears in four places, deliberately different in weight:

| Where | Form |
|-------|------|
| Floating launcher, bottom right (desktop) | ink square, expands on hover |
| Intro card, once on a first visit | dismissible, remembered in `localStorage` |
| Contact section | a full panel: glyph, number on screen, and a solid button |
| Mobile dock and footer | icon and text link |

The contact-section panel is the one clients act on, so the whole surface is the
link — glyph, number and button together — with the button styled as a solid bone
rectangle so it reads as an action rather than as another row of the details list.
The button inside is a `<span>`, not a nested link, so the panel stays one target.

## ⚠ A Colombian number raises three questions

The WhatsApp line is +57 — Colombia. If the practice is based there rather than in
Europe, three things on the site currently contradict that:

- **Working hours** read *09:00–18:00 CET* in four places. Bogotá is COT (UTC−5),
  seven hours behind. A Spanish client reading CET will call at the wrong time.
- **Currency base** is EUR, and COP is treated as an indicative conversion only.
  If you invoice Colombian clients in pesos, COP belongs in `FX.invoice`, and
  `FX.base` may want to be COP or USD.
- **Certification route.** Colombia has its own sworn-translator system
  (*traductor e intérprete oficial*, certified by examination and registered with
  the Ministerio de Relaciones Exteriores). If you hold that, it is a stronger
  credential for Colombian and wider Latin American clients than the Malta MA, and
  it belongs in the dossier. See the note on *traducción jurada* above.

None of this is broken — it is just unstated. Tell me where the practice actually
operates and it can be made consistent in one pass.

## Currency

The fees section carries a currency selector. On a first visit the currency is
chosen automatically from the visitor's **device time zone** (`America/Bogota` →
COP, `Europe/Malta` → EUR, `America/Mexico_City` → MXN, and so on), falling back
to the browser language, then to EUR. Their choice is remembered in
`localStorage`, and the selector overrides the guess at any time.

Supported: **EUR, USD, GBP, MXN, COP, CLP, PEN, ARS, BRL.**

### ⚠ The rates are hard-coded and go stale

They live in one block at the top of `app.js`:

```js
var FX = {
  base: 'EUR',                    // the currency your data-amount figures are in
  invoice: ['EUR','USD','GBP'],   // the currencies you actually invoice in
  rates: { EUR:1, USD:1.08, GBP:0.85, MXN:19.80, COP:4450, CLP:1030,
           PEN:4.05, ARS:1180, BRL:6.05 }
};
```

**Set these to real rates before launch and review them monthly.** ARS moves fast
enough to embarrass you within weeks. Nothing binds you to a displayed figure —
the page states that non-invoice currencies are an indicative conversion, and the
written quotation is what governs — but a visibly wrong price still costs trust.

If you would rather not maintain rates at all, delete the currencies you do not
invoice in from `FX.rates` and the `<select>` in both home pages, leaving EUR, USD
and GBP. Live rates would need a third-party API call on every page load: an
external dependency that can fail, slow the page, and expose visitors to another
service. Not worth it at this scale.

### Why the ISO code and not a symbol

Figures render as `45 EUR`, `200.000 COP`, `MXN 890` — never a bare `$`. The
dollar sign denotes at least five different currencies across Latin America, and a
Colombian reading `$45` for a document that costs 200,000 pesos is a misquote, not
a rounding error. The code is unambiguous in every market you serve.

### Changing a price

Edit the `data-amount` attribute on the figure, not the visible text — the script
overwrites the text on load. Amounts are expressed in `FX.base`.

## The practice, and where credentials live

The home pages speak for the **practice**: qualified translators, firm standards,
no individual biography. Personal credentials — portrait, degree, dossier,
signature — live on the translators page, which is built to hold a roster.

- Home `01 — El despacho` / `01 — The practice` states the standards every
  translator must meet and links through to the roster.
- The home hero keeps one portrait, captioned **Director / Principal**, with a link
  to the roster. If you would rather the home page show no individual at all, swap
  that image for an office or document photograph and drop the caption.

### Adding a translator

In `traductores.html` and `translators.html`, duplicate the whole
`<li class="roster__entry">` block — it is marked with a comment — and replace the
portrait, name, seat, role, biography and dossier rows. The second entry in each
file is an example; replace it with a real translator or delete it. There is no
limit on entries, and the layout stacks on mobile automatically.

The `Normas del despacho` / `Standards` section states what is required of every
translator. Keep it honest: it is a promise you are making on their behalf.

## ⚠ Editing shared vs. per-page

Layout, styling and behaviour now live in **`styles.css`** and **`app.js`**, shared
by all four pages — edit those once. **Markup and copy are per page**, so a change
to the header, footer, contact details or any text must be applied to each of the
four HTML files. Every placeholder string is deliberately identical across files,
so one find-and-replace over all four handles the domain, telephone, WhatsApp
number, fees and form endpoint.

`app.js` picks its interface strings from `<html lang>`, so it serves both
languages without modification.

## ⚠ "Traducción certificada", not "traducción jurada"

The Spanish text deliberately says **traducción certificada** throughout. In Spain,
*traducción jurada* is a protected term: only a **Traductor-Intérprete Jurado**
appointed by the Ministerio de Asuntos Exteriores may issue one, and a Maltese MA
does not confer that appointment. Using *jurada* without the appointment would be a
false claim to Spanish clients — precisely the audience this page is built for.

If you hold the MAEC appointment, say so explicitly and switch the wording. If you
hold an equivalent appointment elsewhere (ATA certification, ITI/CIOL, a sworn
appointment in another country), name the body — an unqualified "certified" is
weaker than a named credential.

## Design system

| Token            | Value     | Use                                        |
|------------------|-----------|--------------------------------------------|
| Ink              | `#0F141A` | Hero, process, contact, footer grounds      |
| Navy             | `#1D2A38` | Primary button hover                        |
| Bone             | `#F5F2ED` | Page ground                                 |
| Bone warm        | `#FAF8F4` | Alternating sections, form panel            |
| Brass            | `#8E7243` | Rules, index labels, numerals — never fills |
| Brass light      | `#C4AC80` | Same, on ink grounds                        |
| Text             | `#161C23` | Headings and body on light                  |
| Text soft        | `#4A5560` | Body copy                                   |
| Text mute        | `#7C8691` | Labels, captions                            |
| Rule             | `#E1DCD3` | Hairlines on light                          |
| Rule (dark)      | `rgba(242,239,233,.16)` | Hairlines on ink            |

Type: **Spectral** (display, 300–600) over **Inter** (interface). Corners are 2px.
No drop shadows anywhere. Motion is opacity plus a 12px rise, 0.9s, staggered 70ms.

## Before going live

1. **Domain** — replace every `YOURDOMAIN.com` (canonical, Open Graph, JSON-LD,
   email addresses, footer, form error message).
2. **All four pages** — every replacement below applies to `index.html`,
   `traductores.html`, `en.html` and `translators.html`. A find-and-replace over
   all four is the safe way; the placeholder strings are identical in each.
3. **Company name** — the wordmark currently reads *Santiago Pedraza Castillo*
   with the role line *Traductor certificado* / *Certified Translator*. If the
   business trades under a different name, replace the wordmark in all four files
   and in the JSON-LD `name` fields. Consider changing the role line to
   *Traducción certificada* / *Certified Translation* so it describes the firm
   rather than a person.
4. **Portraits** — Santiago's photo (`santiago.jpg`, 900×1125, 114 KB) is in place
   on all four pages. The second roster entry shows an empty dashed slot labelled
   *Retrato pendiente* / *Portrait pending*; the markup to restore a real `<img>`
   sits in a comment directly above it. New portraits: 900×1125 (4:5), under
   200 KB, saved beside the HTML. The design greyscales them automatically, so a
   colour original is fine. The design greyscales it, so colour
   grading is not critical; a plain background and direct gaze are.
5. ~~**WhatsApp number**~~ — **done**: +57 321 854 1666 (`wa.me/573218541666`),
   set in all 22 links across the four pages and shown as text in the contact
   panel. Former instructions, should it ever change: the floating launcher (two),
   the intro card, the mobile dock, the direct-line panel in the contact section
   and the footer. The direct-line panel also shows the number **on screen** as
   text — replace that too, or it will read +00 000 000 000 next to a working link.
   Format is digits only — country code, no `+`, spaces or dashes.
   +57 321 854 1666 → `https://wa.me/573218541666`
   The `?text=` parameter pre-fills the visitor's opening message; edit or delete it.
   Test each link on a phone before launch — a wrong number fails silently.
6. **Contact particulars** — still placeholders: email (`hello@YOURDOMAIN.com`),
   **telephone** (`tel:+00000000000`, six links per page plus the `telephone`
   field in the JSON-LD), working hours, and the city/country in the JSON-LD
   address. If the telephone is the same line as WhatsApp, say so and it can be
   filled in the same pass.
7. **LinkedIn** — replace `YOURPROFILE` in the footer and in the JSON-LD `sameAs`.
8. **Fees** — replace the `data-amount` values (45 per page, 0.14 per word) and
   the +40% surcharge, set `FX.base` to the currency those figures are in, and put
   real exchange rates in `FX.rates`. See **Currency** above.
9. **Testimony** — all three quotes are placeholders. Replace with real client
   feedback you have permission to publish.
10. **Form endpoint** — create a form at formspree.io (or similar) and replace
   `YOUR_FORM_ID` in the form `action`. File uploads need a paid Formspree plan.
   Until then the form validates and confirms locally without transmitting.
11. **Payment page** — create a hosted payment page and replace the
   `https://YOURDOMAIN.com/pay` link in the Payment section:
   - Stripe → Payment links (recommended: cards, wallets, Link, one link, no code)
   - Stripe Invoicing → each invoice carries its own pay-now link
   - PayPal.Me → `paypal.me/YOURNAME`
   Never add a card-number field to this page — collecting card data directly puts
   you inside PCI-DSS scope. The hosted page keeps that liability with the provider.
12. **Acceptance marks** — the Visa / Mastercard / Amex chips are typographic
   placeholders. Swap each for official artwork:
   `<span class="marks__chip"><img src="marks/visa.svg" alt="Visa"></span>`
   Sources: visa.com/brandcenter · brand.mastercard.com ·
   americanexpress.com/merchantmarketing · paypal.com/brand-centre ·
   developer.apple.com/apple-pay/marketing. Use the official files; redrawn card
   logos look counterfeit and breach the brand terms.
13. **Payment terms** — confirm the four terms in the Payment section match how you
    actually bill (due on approval, 50% deposit over 20 pages, USD/EUR/GBP,
    cancellation), and the `paymentAccepted` / `currenciesAccepted` lines in the
    JSON-LD.
14. **Legal pages** — link real Privacy and Terms pages in the footer.
15. **Roster entries** — replace or delete the example translator on both
    translators pages (its name, biography and dossier rows are all placeholder
    text). Santiago's entry is complete except the membership row — name the body
    (ATA, ITI, CIOL, MAEC…) or delete the row if none is held.
16. **Social image** — add `og-image.jpg` (1200×630) and a real `favicon.ico`.

Search `index.html` for `SUSTITUIR` and `en.html` for `REPLACE` — every
placeholder is commented in the language of its page.

Fee figures are formatted by the browser for each page's language — `0,14 EUR` in
Spanish, `EUR 0.14` in English — so you set the number once, in `data-amount`, and
both pages render it correctly.

## Copy worth checking

- The Credentials section states a specialisation in legal and institutional
  translation at Malta. Amend if that is not accurate.
- The Questions section offers notarisation and apostille support. Amend if you
  do not offer it.
- The hero and dossier state 24–48 hour standard delivery. Amend if slower.
- The Payment section states card details never reach you. That stays true only
  while payment runs through a hosted provider page — do not add a card form.

## WhatsApp behaviour

The floating launcher sits bottom-right on desktop and expands to a label on hover.
On a first visit an introduction card opens after 5.2 seconds; dismissing it (or
following the link) stores `wa-card-dismissed` in `localStorage`, so it never
returns for that visitor. The launcher itself stays. Change the delay in the
script (`5200`), or delete the card block entirely to leave only the launcher.

Below 680px the launcher is hidden — the sticky dock carries WhatsApp and telephone
icons instead, so the two never overlap.

## A note on "Desde 2025"

Santiago's entry states practice since 2025 — roughly a year. Nothing else on the
site claims longer, and the copy leans on qualification rather than tenure, which
is the right emphasis while the practice is young. Two things follow from it:

- The testimonials are placeholders. Replace them with real ones as they arrive,
  or delete the section until you have them — invented praise beside a recent
  start date is the pairing a careful client notices.
- The home page says the practice works with "translators" in the plural. Until a
  second translator actually joins, that reads ahead of the facts. Either add them,
  or soften the plural until you do.

## Spanish copy worth reviewing

Written in peninsular Spanish with formal *usted* address throughout. If most of
your clients are Latin American, a few choices shift: *expediente académico* →
*certificado de notas* or *historial académico*, *permiso de conducir* → *licencia
de conducir*, and *móvil* / *ordenador* would change if you add them later.
Terms such as *apostilla*, *poder notarial*, *antecedentes penales* and
*legitimación notarial* are safe in both regions.

## After launch

- Submit to Google Search Console and check the International Targeting report
  for hreflang errors once both URLs are live.
- Validate the structured data at https://search.google.com/test/rich-results
- `LIMIT` in the script sets the 10 MB per-file warning — match it to your form
  handler's actual limit.
