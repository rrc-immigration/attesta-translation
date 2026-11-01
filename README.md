# Attesta Translation

Static site in `public/`, tools in `tools/`. See `CLAUDE.md` for rules, settings and open decisions.

## Preview locally
    cd public && python3 -m http.server 8000

## Deploy (Vercel)
1. Push this repo to GitHub.
2. In Vercel: Add New > Project > import the repo. No build command; output directory is `public` (set in `vercel.json`).
3. Project > Settings > Domains: add `attestatranslation.com` and `www.attestatranslation.com`.
4. At Namecheap (Domain List > Manage > Advanced DNS), add exactly the records Vercel shows for each domain (an A record for the root and a CNAME for `www`). Remove Namecheap's default parking records first.
5. Wait for Vercel to show "Valid Configuration" and issue the certificate (usually minutes).

## Translation tools
    pip install pymupdf pdfkit fonttools playwright pillow pypdf   # plus wkhtmltopdf and Chromium
    python3 tools/seal/make_seal.py tools/certificate/assets
    python3 tools/certificate/attesta_cert.py --source "File.pdf" --pages 1 --language "Portuguese (Brazil)" --translator "Sergio Rocha" -o certificate.pdf
    python3 tools/translate/mirror_pdf.py extract file.pdf blocks.json
