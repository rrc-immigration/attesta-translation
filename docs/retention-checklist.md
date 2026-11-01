# File retention: what the site promises and how to keep the promise

Promise (FAQ, Privacy Policy): documents and working files are deleted within 30 days after delivery, or within 30 days after an order is closed without delivery. Order records without document images are kept up to 3 years. Clients can ask for earlier deletion.

## For every order, within 30 days after delivery
1. Gmail (hello@attestatranslation.com): delete the client's email threads that contain documents, then empty Trash. Search by client email address.
2. WhatsApp: delete the chat or the media, including "Delete for me" on the phone and any linked device. Turn off media auto-save to the phone's photo library.
3. Google Drive and downloads: delete the original scans, drafts, translated PDFs and the merged package. Empty Drive Trash.
4. This computer and any cloud session folder: delete working copies (blocks.json, translations.json, twin.pdf, rendered images).
5. Keep only the order record: client name, email, date, document type, language, pages, amount paid, certificate reference. No document images.

## Habits that make it possible
- Use one Drive folder per order, named by order number (for example AT-2026-0001), so deletion is one action.
- Keep a simple order log (a Sheet) with delivery date and a "deleted on" column. Review it weekly.
- Turn on 2-step verification for the Google Workspace account and the phone that holds WhatsApp (the Privacy Policy mentions sign-in protections).
- If a client asks for earlier deletion, do it and reply to confirm.
- Never commit client files to this repo (`orders/` and `client-files/` are git-ignored).

## If the retention period changes
Update the FAQ answer (`a6` in both languages in `public/index.html`) and `public/privacy.html` ("How long we keep it") together, and bump the "Last updated" date.
