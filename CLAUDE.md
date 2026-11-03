# Attesta Translation (attestatranslation.com)

Certified translations of PT/ES/FR/IT documents into English for USCIS filings. Owner: Sergio Rocha.
This is a separate business from Rocha Ricomini Consulting and Migrei.ai. Never put those names, letterhead or seals on Attesta materials.

## Layout
- `public/index.html`: the whole site (single self-contained page, EN and PT-BR, live price estimator). Vercel serves `public/`.
- `public/attesta-gold-seal*.{svg,png}`, `public/sample-certificate.pdf`: brand assets.
- `tools/certificate/attesta_cert.py`: Certificate of Translation Accuracy generator.
- `tools/seal/make_seal.py`: regenerates the gold seal PNG.
- `tools/translate/mirror_pdf.py`: in-place facsimile translation of a PDF (keeps the original page, replaces the text).
- `public/lp/index.html`: Facebook ad landing page at /lp (PT default, EN with `?lang=en`; `?src=name` tags the WhatsApp message with the ad source; `noindex`). Its CONFIG duplicates the prices and WhatsApp number from `public/index.html`: change both together. No Meta Pixel installed; if one is added, update `privacy.html` (it says the site has no ad trackers).
- `public/terms.html`, `public/privacy.html`: Terms of Service and Privacy Policy (English only, linked in the footer; Vercel serves them at /terms and /privacy). Draft, not yet reviewed by an attorney.
- `docs/retention-checklist.md`: how to keep the 30-day deletion promise.
- `docs/website-plan.md`: original plan and stack ideas. `docs/attesta-translation-skill.md`: the order workflow skill text.

## Settings (top of the `<script>` in `public/index.html`, object `CONFIG`)
email hello@attestatranslation.com, WhatsApp digits (used only inside the button link, never printed), rate $15/page, $12.50/page from 11 pages (whole order, unconfirmed), rush +$10/page (placeholder), standardDays 2 (placeholder), maxPages 200.

## Rules that do not change
- WhatsApp number is never displayed on the page or on certificates. Business email is hello@attestatranslation.com; never use a personal or Rocha Ricomini address.
- Certificates: blank signature line (the translator signs in Adobe), date is today's date at generation, no signature images.
- Never claim "USCIS approved/certified". USCIS does not approve translators. Certified is not sworn (tradução juramentada). Notarization is not required by USCIS.
- Default signer Sergio Rocha for PT/ES/FR. Italian has no signer yet: do not publish an Italian promise without one.
- Do not add copy that promises something the business does not yet do (uploads, checkout). The 30-day deletion promise is real only if `docs/retention-checklist.md` is followed.

## Current state (launch version)
Static site. "Start my order" shows the price and opens a prefilled email or WhatsApp message; documents are NOT uploaded through the site. Payment is by a link Sergio sends. There is no backend.

## Next phases
1. Stripe Payment Links, then Stripe Checkout with webhooks.
2. Private uploads (Supabase or R2, signed URLs, automatic deletion), order status pages, admin inbox. Plan stack: Next.js on Vercel.
3. Partner portal for attorneys (bulk upload, invoicing).

## Open decisions (surface these, do not guess)
- Does $12.50 apply to all pages once over 10, or only pages beyond the 10th?
- Rush surcharge, turnaround promises, 250-word page definition, free-redo guarantee wording.
- File retention is set to 30 days after delivery (order records 3 years). This is a default Sergio has not confirmed; if it changes, update the FAQ (`a6`), `privacy.html` and `docs/retention-checklist.md` together.
- Terms/Privacy need attorney review, the legal entity name that operates Attesta, and Portuguese versions (the footer says "em inglês").
- Italian signer; English into PT/ES/FR/IT direction.
- E&O insurance, trademark clearance for "Attesta".
- Conflict check with Sergio's employment at Kilpatrick Townsend; clearing marketing wording with Edmund Kim, Esq. if associated with the consulting business.
- Re-verify competitor prices before quoting them anywhere; check the BRL rate before any case with Brazilian amounts.
