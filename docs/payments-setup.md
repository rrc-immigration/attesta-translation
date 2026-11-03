# Taking payment: Stripe and Zelle

The site says clients pay by card (secure link) or Zelle, and that payment instructions arrive after the final price is confirmed. No Zelle recipient or Stripe link is published on the site, on purpose: it keeps clients from paying look-alike accounts and lets you quote an exact total first.

## Stripe (cards, Apple Pay, Google Pay)
1. Create the account at stripe.com with hello@attestatranslation.com and the business details Stripe asks for (business type, owner, bank account for payouts, statement descriptor "ATTESTA TRANSLATION"). Turn on two-step verification.
2. Dashboard > Product catalog: create two products.
   - "Certified translation, per page (1 to 10 pages)", one-time, US$ 15.00.
   - "Certified translation, per page (11 or more pages)", one-time, US$ 12.50.
3. Dashboard > Payment Links > New: pick one product, then turn on "Let customers adjust quantity" and set the range (1 to 10 for the first link, 11 to 200 for the second). Collect the customer's email and name. Add an order-reference custom field if offered.
4. Stripe's docs list flat-rate and package pricing for one-time prices in Payment Links, not tiered volume pricing, so two links (or a custom amount per order) is the way to apply the 11-page rule. For rush or notarization, make a one-off link or an invoice with the exact amount.
5. Check Settings > Payment methods: cards, Apple Pay and Google Pay should be on. Standard card pricing was about 2.9% + $0.30 per charge when the plan was written; confirm the current rate in Stripe.
6. Send the right link in the order confirmation after you have counted the pages. Do a $15 test payment, then refund it.
7. Later phases (see CLAUDE.md): Checkout with webhooks once uploads exist.

## Zelle
- Zelle is offered by banks, not by Zelle directly. Enroll the Attesta business bank account (many banks have a "Zelle for business" option) using hello@attestatranslation.com, or a business phone number, as the Zelle identifier. Do not use your personal phone, your WhatsApp number or a Rocha Ricomini address.
- Customers pay your enrolled email, phone or Zelle tag, and the name they see should match the business name on the account. Put that exact name in your payment instructions.
- Zelle payments are final: there is no purchase protection and a sent payment cannot be cancelled once the recipient is enrolled. That is why the site tells clients to check the recipient name, and why you should confirm the page count before sending instructions.
- Confirm with your bank that business payments may be received on the account you enroll (some banks restrict business use of personal accounts), and ask about limits and fees.
- Never publish the Zelle recipient on the website. Send it by email or WhatsApp with the final price, and never change it by message.
- Do not use the Zelle logo until you have read Zelle's brand guidelines; the site uses the word only.

## Sources
- Stripe, Create a payment link: https://docs.stripe.com/payment-links/create
- Example of a bank's Zelle for business terms (TD Bank): https://td.com/us/en/small-business/zelle-for-business
