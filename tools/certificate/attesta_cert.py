"""
attesta_cert.py: Attesta Translation, Certificate of Translation Accuracy.

Same legal statements and signature policy as the Rocha Ricomini certificate
(8 CFR 103.2(b)(3): competence in both languages + accuracy), on Attesta's own
letterhead with the gold seal. Kept separate from the Rocha Ricomini template
on purpose.

SIGNATURE POLICY: the signature line is an empty underline. Never embed a
signature image. The translator signs the finished PDF in Adobe Acrobat
(Fill & Sign > Sign Yourself).

The certificate date and "Date signed" are always today's real date,
computed when the file is generated.

Usage:
    python3 attesta_cert.py --source "Certidao_Nascimento.pdf" --pages 1 \
        --language "Portuguese (Brazil)" --translator "Sergio Rocha" -o certificate.pdf
"""
import argparse, datetime, os

HERE = os.path.dirname(os.path.abspath(__file__))
SEAL = os.path.join(HERE, "assets", "attesta_gold_seal.png")

NAVY = "#14213D"
GOLD = "#B8902E"
INK = "#1B2236"

# Business details: change here once, every certificate picks it up.
BUSINESS = {
    "name": "ATTESTA TRANSLATION",
    "tagline": "Certified Translation Services",
    "website": "attestatranslation.com",
    "email": "hello@attestatranslation.com",
    "phone": None,   # set when decided, e.g. "408 000 0000"
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def cert_html(source, pages, language, translator, order_no=None, brl_rate=None):
    today = datetime.date.today().strftime("%m/%d/%Y")
    seal = f'<img src="file://{SEAL}" style="width:118px;height:118px;">' if os.path.exists(SEAL) else ""
    contact_lines = "".join(f'<p class="sdet">{label}{esc(BUSINESS[k])}</p>' for k, label in (("email", "Email: "), ("phone", "Telephone: ")) if BUSINESS.get(k))
    order_row = f"<tr><th>Reference No.</th><td>{esc(order_no)}</td></tr>" if order_no else ""
    brl_note = ""
    if brl_rate:
        brl_note = (
            f'<p class="note">Note: All Brazilian Reais (BRL) figures appearing in the attached translation are '
            f'accompanied by an approximate U.S. Dollar (USD) equivalent, calculated at the exchange rate of '
            f'BRL {brl_rate:.2f} = USD 1.00 as quoted on {today}. The USD figures are provided solely for the '
            f'convenience of the reader and are approximate; the BRL figures stated in the original document '
            f'remain controlling.</p>'
        )
    return f"""<html><head><meta charset="utf-8"></head><body style="margin:0;">
<style>
  .page {{ width: 6.5in; margin: 0.75in auto 0 auto; }}
  .outer {{ border: 1.5px solid {NAVY}; padding: 5px; }}
  .inner {{ border: 1px solid {GOLD}; padding: 28px 40px 24px 40px; }}
  .serif {{ font-family: 'Times New Roman', Times, 'Liberation Serif', serif; }}
  .name {{ text-align:center; font-size: 21pt; font-weight: bold; letter-spacing: 3px; color: {NAVY}; margin: 0; }}
  .tag {{ text-align:center; font-size: 8.5pt; letter-spacing: 2.8px; color: {GOLD}; text-transform: uppercase; margin: 4px 0 14px 0; }}
  .rule {{ border: none; border-top: 1.5px solid {GOLD}; margin: 0 auto 18px auto; width: 60%; }}
  .title {{ text-align:center; font-size: 15pt; font-weight: bold; letter-spacing: 1.8px; color: {NAVY}; margin: 0 0 20px 0; text-transform: uppercase; }}
  .body p {{ font-size: 10.9pt; line-height: 1.55; color: {INK}; text-align: justify; margin: 0 0 13px 0; }}
  table.info {{ width:100%; border-collapse: collapse; margin: 16px 0 22px 0; }}
  table.info th {{ background: transparent; color: {NAVY}; font-size: 8.7pt; text-align:left; padding: 5px 10px 5px 8px; width: 32%;
      font-weight: bold; letter-spacing: .5px; text-transform: uppercase; border-bottom: 1px solid #bbb; border-left: 2.5px solid {GOLD}; }}
  table.info td {{ font-size: 10pt; padding: 5px 10px; border-bottom: 1px solid #ddd; color: #111; }}
  table.sign {{ width:100%; border-collapse: collapse; margin-top: 30px; }}
  table.sign td {{ vertical-align: bottom; padding: 0; }}
  .line {{ border-bottom: 1px solid {INK}; height: 34px; margin-bottom: 4px; }}
  .sname {{ font-size: 11.8pt; font-weight: bold; color: {NAVY}; margin: 0; }}
  .sdet {{ font-size: 9.2pt; color: #333; margin: 1px 0; }}
  .note {{ font-family: Arial, Helvetica, sans-serif; font-size: 7.8pt; color: #444; border-top: 1px solid #ccc; margin: 24px 0 0 0; padding-top: 9px; line-height: 1.4; }}
</style>
<div class="page serif"><div class="outer"><div class="inner">
  <p class="name">{BUSINESS['name']}</p>
  <p class="tag">{BUSINESS['tagline']}</p>
  <hr class="rule">
  <p class="title">Certificate of Translation Accuracy</p>
  <div class="body"><p>I, <b>{esc(translator)}</b>, hereby certify that I am fluent in both the {esc(language)} and English
  languages, and that I possess the requisite knowledge, training, and experience to competently translate documents
  between these two languages. I further certify that, to the best of my knowledge and ability, the attached translation
  is a true, complete, and accurate rendering of the original document identified below, and that this translation was
  prepared with professional care and diligence.</p></div>
  <table class="info">
    {order_row}
    <tr><th>Source Document</th><td>{esc(source)}</td></tr>
    <tr><th>Source Language</th><td>{esc(language)}</td></tr>
    <tr><th>Target Language</th><td>English (United States)</td></tr>
    <tr><th>Pages Translated</th><td>{esc(pages)}</td></tr>
    <tr><th>Certificate Date</th><td>{today}</td></tr>
  </table>
  <table class="sign"><tr>
    <td style="width:64%; padding-right:24px;">
      <div class="line"></div>
      <p class="sname">{esc(translator)}</p>
      <p class="sdet">Translator, Attesta Translation</p>
      <p class="sdet">{BUSINESS['website']}</p>{contact_lines}
      <p class="sdet">Date signed: <b>{today}</b></p>
    </td>
    <td style="width:36%; text-align:center;">{seal}</td>
  </tr></table>
  {brl_note}
</div></div></div>
</body></html>"""


def render(out_path, source, pages, language, translator, order_no=None, brl_rate=None, pagesize="Letter"):
    import pdfkit
    pdfkit.from_string(cert_html(source, pages, language, translator, order_no, brl_rate), out_path, options={
        "page-size": pagesize, "margin-top": "0in", "margin-bottom": "0.3in", "margin-left": "0in",
        "margin-right": "0in", "encoding": "UTF-8", "quiet": "", "enable-local-file-access": ""})
    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True); ap.add_argument("--pages", required=True)
    ap.add_argument("--language", default="Portuguese (Brazil)"); ap.add_argument("--translator", default="Sergio Rocha")
    ap.add_argument("--order-no"); ap.add_argument("--brl-rate", type=float); ap.add_argument("--pagesize", default="Letter")
    ap.add_argument("-o", "--out", default="certificate.pdf")
    a = ap.parse_args()
    print(render(a.out, a.source, a.pages, a.language, a.translator, a.order_no, a.brl_rate, a.pagesize))
