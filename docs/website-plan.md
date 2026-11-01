# Attesta Translation: website plan (v1)

Domain: attestatranslation.com (primary). getattesta.us and others redirect to it.
Owner: Sergio Rocha. Focus: certified translations for USCIS filings; general clients second.
Signing: Sergio signs PT, ES and FR. Italian signer still to be decided.

---

## 1. Competitor pricing (US, published per-page rates)

Per page = up to 250 words, the industry convention. Prices come from provider pages and articles found in search on 2026-09-27. Several pages are undated or old, so re-verify before publishing any comparison.

| Provider | Standard rate | Notes | Date of source |
|---|---|---|---|
| Translations Certified | $14.50/page | Includes notarization and PDF delivery (their claim) | Jul 2026 |
| Sure Translation | $18 | 24h, unlimited revisions, acceptance guarantee | undated |
| uscis-translations.com | $18 | 12h delivery claimed; rush from $28 | 2019 (likely stale) |
| Corpus Localization | $19.99 | | Jun 2026 |
| D&T Translations | from $19.95 (or $0.06/word) | 24-48h typical | undated |
| Writeliff | $20 | Rush and super rush offered | 2023 |
| ASAP Translate | from $24.90 | | Oct 2024 |
| RushTranslate | $24.95 | 24h, unlimited revisions, acceptance guarantee | undated |
| Translayte | $24.99 | | Oct 2025 |
| Rapid Translate | $27.99 (priority $37.99) | | undated |
| Rev | $33 | Sources from 2020-2021 | stale |
| U.S. Language Services | $39 | Notarization +$39 per document | May-Aug 2026 |

Market summary: one 2026 guide puts typical US certified translation at $20-$45 per page. Common language pairs (ES, FR, PT, IT) sit in that range.

Common patterns to copy or beat:
- Guarantee of USCIS acceptance plus free revisions. Nearly everyone advertises one.
- 24-hour turnaround as the baseline; rush costs about +$10/page.
- Notarization sold separately at $5-$39. USCIS does not require it, and the all-in rate is a selling point.
- Same-day and 12-hour claims exist, so speed alone won't differentiate you.

### Your planned pricing: $15/page, $12.50/page over 10 pages

- $15 is below every price found except Translations Certified ($14.50, notarization included). $12.50 is below everything found.
- It works as an entry price, but margin depends on your time per page. At $15/page, 15 minutes of your time is $60/hr, 30 minutes is $30/hr, and 45 minutes is $20/hr. Payment fees on a single page are about $0.74 if Stripe is 2.9% + $0.30 (confirm current rates).
- A very low price can also make anxious clients suspicious. The guarantee, sample certificate, and layout-matched translation have to carry the trust.

Decisions to make:
1. **Define "page" on the site** (up to 250 words). Dense pages, tables, handwriting, and stamps need a stated rule.
2. **Does $12.50 apply to all pages at 11+, or only to pages beyond the 10th?** Write it into the pricing table and the checkout logic.
3. **Most clients need 1-5 pages.** The 11+ tier mainly serves attorneys, so consider a partner rate and a packet bundle for individuals.
4. **Rush add-on:** competitors charge about +$10/page. Suggested: 24-hour rush +$10/page, same-day by quote.
5. **Notarization:** offer as an optional add-on priced at your cost plus a small margin, and state that USCIS does not require it.
6. **Hard copy by mail** as an add-on.
7. **EN to PT/ES/FR/IT direction:** USCIS needs foreign-to-English. If you sell the reverse, decide who certifies it and what it costs.

---

## 2. Brand and visual direction

Concept: **the certificate is the hero.** These clients are anxious, and a rejected packet costs months. The site should feel like an official, careful, human service instead of a generic SaaS page.

- **Palette:** deep ink navy (text and headers), warm paper/cream (backgrounds), one seal accent in muted gold or deep green. Avoid blue-to-purple gradients and stock-photo clichés.
- **Type:** a refined serif for headings (e.g., Source Serif 4 or Fraunces) with a clean sans for body (e.g., Inter or Instrument Sans). Confirm the fonts render PT/ES/FR/IT diacritics correctly (ã, õ, ç, é, è, ñ).
- **Motifs:** a seal/stamp badge, subtle ledger or paper texture, thin rule lines like a document border.
- **Signature components:**
  1. Hero with an upload dropzone and a live price estimator (pages x rate + rush + notarization).
  2. Original vs translation side-by-side slider showing the layout-matched output.
  3. Sample certificate viewer. Fake data only, clearly marked SAMPLE.
  4. "How it works" 4-step timeline.
  5. Document cards (birth certificate, marriage certificate, police record, diploma/transcript, bank statement, divorce decree).
  6. Sticky WhatsApp button on mobile; language toggle EN / PT-BR (ES later).
  7. Guarantee block and FAQ accordion.
- **Mobile-first:** most clients will upload from a phone. Camera upload, multi-file, and progress states must work well.
- **Reviews:** show only real customer reviews. Leave the section out until you have some.
- **Accessibility and speed:** WCAG AA contrast, keyboard navigation, image optimization, Core Web Vitals in the green.

---

## 3. Site map (MVP)

- **Home:** one-line promise, upload + estimator, trust signals, sample certificate, how it works, guarantee, FAQ teaser.
- **Pricing:** table, definition of a page, rush, notarization, hard copy, bundles, partner rate.
- **How it works**
- **Documents:** one landing page each (birth cert, marriage cert, police record, diploma + transcript, bank statement, divorce decree). Main SEO workhorses.
- **Languages:** Portuguese to English first, then Spanish, French, Italian.
- **USCIS translation requirements:** plain-language explainer of 8 CFR 103.2(b)(3): complete English translation plus the translator's certification of competence and accuracy. No claims about "USCIS-approved translators."
- **Guarantee**
- **For attorneys and consultants:** partner rate, bulk upload, invoice billing.
- **About:** you as the signing translator, credentials stated accurately.
- **FAQ, Contact (WhatsApp, email), Privacy, Terms.**

---

## 4. Order flow

1. Upload documents (PDF, JPG, PNG, HEIC), select language and direction.
2. Instant estimate (page count is confirmed manually if the file is unclear).
3. Payment (Stripe Checkout; check whether Pix or other payment methods are available for your account).
4. Translation and review, using the `/certified-translation` skill for layout-mirrored output and the Certificate of Translation Accuracy.
5. Sign the certificate by hand or by Adobe Sign. Never a pasted signature image.
6. Deliver as PDF through a secure download link; optional mailed copy.
7. Email notifications at each stage.

---

## 5. Suggested stack (confirm before building)

- Next.js (App Router) on Vercel, Tailwind CSS, i18n routing (EN default, PT-BR)
- Supabase or S3/R2 with **private** buckets, signed URLs, and an automatic deletion policy for uploads
- Stripe Checkout with webhooks
- Resend for email
- Cloudflare Turnstile against spam
- Analytics with UTM tracking; schema markup (Service/LocalBusiness)

---

## 6. Build phases

1. **Foundation:** design tokens, layout, i18n, component library, static pages with placeholder copy.
2. **Quote and upload:** hero estimator, upload flow, storage, admin inbox for new orders.
3. **Payments and orders:** Stripe, order status pages, email notifications, PDF delivery.
4. **Trust and content:** sample certificate, document pages, requirements explainer, FAQ, guarantee, Terms and Privacy reviewed.
5. **Partner portal:** attorney rate, bulk upload, invoicing.
6. **SEO and launch:** per-document and per-language pages, Google Business Profile, sitemap, redirects from getattesta.us.

---

## 7. Announcement on Migrei.ai and Rocha Ricomini Consulting

- Banner and service page on each site, linking to attestatranslation.com with UTM tags.
- Add-on step in the intake flow ("Need your documents translated?").
- Email to the client list; WhatsApp broadcast.
- Sample banner: "Novo: tradução certificada para o USCIS, a partir de US$ 15 por página." / "New: certified translations for USCIS, from $15 per page."
- Keep Attesta's copy free of immigration advice, and run the cross-promotion wording past Edmund Kim since the consulting work is under his supervision.

---

## 8. Open items and risks

1. **Competitor prices need re-verifying** before any public comparison. Do not name competitors in marketing copy without checking.
2. **Italian signer** is unassigned. Either you certify competence honestly, or bring in a vetted translator.
3. **Your certificate is a statement of competence and accuracy under your name.** Every page, including any AI-assisted draft, needs your full review before signing.
4. **Employer conflict check.** Confirm your firm's outside-activity policy before launch.
5. **Business setup:** entity, E&O insurance, Terms (refunds, guarantee wording, what "certified" means), and a retention policy for uploaded passports and IDs.
6. **Trademark clearance** for "Attesta" (USPTO plus common-law) is still not done.
7. **Sworn translations** (for Brazil, Italy, France, Spain) are a different service. Offer through a partner or say clearly you don't.
8. **Guarantee wording:** promise a free redo if the translation itself causes a rejection or RFE. Do not promise the case outcome.

---

## 9. Claude Code kickoff prompt

```
Read attesta-website-plan.md. We're building AttestaTranslation.com.
Start with Phase 1 only. First propose the design tokens (palette, type scale,
spacing), the component list, and the page templates, and wait for my approval
before writing code. Ask me about anything unclear in pricing or legal wording.
Use the /certified-translation skill for layout-mirroring and the certificate
structure, but adapt the certificate letterhead to Attesta Translation. Keep Attesta's
site and certificates visually and legally separate from Migrei.ai and Rocha Ricomini
Consulting, and never use a signature image.
```
