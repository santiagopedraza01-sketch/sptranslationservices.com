# SP Translations — blog content strategy

Goal: maximise organic visibility for searches that lead to paid work, and turn that traffic into
quote requests. Every article needs a clear **search intent**, **audience** and **business objective**.
Never publish for the sake of publishing: if no topic clears the bar below, update an existing post instead.

## Audiences (in order of revenue)
1. **People moving to or living in Malta** who need official documents translated: non-EU workers
   (Single Permit, Skills Pass, renewals), families (reunification, births, marriages), students,
   nomads, applicants for long-term residence or citizenship. Biggest source of certified work.
2. **iGaming companies in Malta**: operators, studios, affiliates entering new regulated markets.
   High value, recurring localisation and content-writing work.
3. **Businesses, legal and academic clients**: contracts, court papers, transcripts, websites.
4. **Museums, heritage and tourism** organisations (exhibitions, audio guides).

## Topic pillars → service page each article must link to
| Pillar | Example intents | Money page |
|---|---|---|
| Moving to Malta (permits, residence, family) | "documents for Malta single permit", "translate birth certificate Malta" | /certified-translations-malta |
| Certified, sworn & apostille | "apostille Philippines documents Malta", "sworn translation Malta" | /certified-translations-malta |
| Life events in Malta (marriage, births, driving licence, qualifications) | "getting married in Malta documents", "MQRIC recognition translation" | /certified-translations-malta |
| iGaming & regulated markets | "Brazil iGaming localisation", "translate T&Cs for new market" | /igaming-translation-services |
| Content & localisation | "multilingual SEO content", "website translation cost" | /content-writing-services, /website-translation-services |
| Languages | "Italian to English certified translation Malta" | the language page |

## What earns a slot (score each candidate 1–5, publish the highest total)
- **Demand**: real people searching now (Google suggest / People Also Ask, forums, Facebook groups,
  Reddit r/malta, news). Time-sensitive events (new rules, deadlines, budget measures) score 5.
- **Business fit**: the reader will need a translation/localisation we sell.
- **Gap**: competitors (transcripta.com, gts.com.mt, 1stoptranslations.com, translayte.com,
  languagebear.com, other Malta agencies) have nothing, or something thin/outdated.
- **Winnability**: specific long-tail queries beat broad ones.
**Breaking opportunities** (e.g. a rule giving non-EU nationals a short deadline to verify documents)
jump the queue: publish within the run, factual and calm, with the deadline in the first lines.

## Quality bar (every article)
- 1,200–2,200 words for guides; 700–1,100 for breaking news. Answer the query in the first 100 words.
- **Facts only from official or primary sources** (gov.mt, servizz.gov.mt, legislation.mt, MGA,
  MFHEA/MQRIC, Jobsplus, Skills Pass, EU portals, embassy sites, reputable press for news).
  Hedge anything not confirmed ("at the time of writing", "check with the receiving institution").
  Never invent fees, dates, deadlines, statistics, quotes or case studies. List the sources checked.
- Hero image: generated per article with `_tools/gen_image.py` (Higgsfield, Recraft V4.1 Pro) — a
  realistic, on-topic scene in the site's navy/brass palette, never text, flags, logos, readable
  official stamps or recognisable people.
- Structure: key-facts box → sections with descriptive H2s (each with an id) → practical checklist or
  table → FAQ (4–6 real questions) → sources → related links. Internal links: the money page, 2+
  related posts/pages. One clear CTA (built into the template).
- Helpful first: explain what to do, in what order, and the common mistakes that cause rejections.
  The service mention is natural ("we translate…") — not an advert.
- Titles ≤ 60 characters + brand; descriptions 140–160 characters; include the year when the
  content is time-bound.
- Spanish version (`es`) when the audience is largely Spanish-speaking (LatAm/Spain documents,
  LatAm iGaming). Otherwise English only.

## House rules (must follow)
- **Do not mention Identità** (the agency) by name or link to its site. Say "the residence
  authorities", "the Public Registry", "the immigration authorities in Malta".
- **Never write "certificate of accuracy" / "certificado de exactitud".** Our translations are
  "issued, signed, dated and stamped by a professional, accredited translator".
- We are a generic agency for all languages (14 core languages + 120 via network). Do not position
  as Spanish-first. Santiago's own pair (Spanish ⇄ English) may appear in his bio only.
- Prices: certified civil documents from €30/page; academic & legal from €0.1/word; priority +30%.
- Do not claim certifications (ISO etc.), years of experience, client names or statistics we have not
  been given. No fake testimonials.
- British English for EN; neutral Spanish (tú) for ES, consistent with the site.

## Process for each run (every two days)
1. Read this file, `backlog.md` and `published.md`.
2. Research (30 min budget): Malta news (Times of Malta, Malta Independent, Newsbook, Lovin Malta,
   gov.mt press releases), immigration/residence changes, MGA and iGaming news, competitor blogs
   (above), Google suggestions / People Also Ask for 3–5 seed queries. Add new ideas to the backlog
   with scores; re-score time-sensitive ones.
3. Pick the top-scoring topic not yet covered (check `published.md` to avoid cannibalising).
4. Verify every fact against primary sources. If a key fact can't be verified, choose another topic.
5. Write `_tools/blog/posts/<slug>.json` (see `_tools/build_post.py` for the format), then run:
   `python3 _tools/build_post.py <slug> && python3 _tools/build_blog.py && python3 _tools/apply_heroes.py && python3 _tools/build_search_index.py`
6. Check: valid JSON-LD, no broken internal links, no "Identità", no "certificate of accuracy".
7. Commit "Blog: <title>", rebuild the sitemap (`python3 _tools/build_sitemap.py`), commit
   "Sitemap: refresh last-modified times", then `git push origin main && git push origin main:staging`.
8. Update `published.md` (date, slug, title, target query, pillar) and `backlog.md` (move the topic,
   add new findings). Commit and push those too.
9. Every 4th run: competitor review (what they published since last time, gaps), and refresh any of
   our posts whose facts may have changed (update the `updated` date only when content changes).
