#!/usr/bin/env python3
"""Build templates/reference.docx: Pandoc's default reference document with CV styles.

Run once (or whenever the Word look should change); the result is committed.
Styles touched: Normal/Body Text, Title, Subtitle, Heading 1-3, Compact, First Paragraph, Table.
"""
import re, shutil, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = sys.argv[1] if len(sys.argv) > 1 else "cv"
OUT = ROOT / "templates" / ("reference-bc.docx" if PROFILE == "bc" else "reference.docx")
FONT = "Aptos"          # Word 365 default; Word substitutes if missing
FALLBACK = "Calibri"
HEADING_FONT = "Arial" if PROFILE == "bc" else FONT
BODY_SZ = "22" if PROFILE == "bc" else "21"   # half-points: 11pt for the form, 10.5pt for the CV

def patch_styles(xml):
    # base font and size for everything
    xml = re.sub(r'<w:rFonts w:ascii="[^"]*" w:hAnsi="[^"]*"', f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"', xml)
    xml = re.sub(r'<w:rFonts w:ascii="[^"]*"', f'<w:rFonts w:ascii="{FONT}"', xml)
    xml = re.sub(r'(<w:docDefaults>.*?<w:sz w:val=")\d+(")', rf'\g<1>{BODY_SZ}\2', xml, flags=re.S)
    xml = re.sub(r'(<w:docDefaults>.*?<w:szCs w:val=")\d+(")', rf'\g<1>{BODY_SZ}\2', xml, flags=re.S)

    def restyle(style_id, ppr, rpr):
        nonlocal xml
        pat = re.compile(rf'(<w:style [^>]*w:styleId="{style_id}"[^>]*>)(.*?)(</w:style>)', re.S)
        m = pat.search(xml)
        if not m: return
        body = m.group(2)
        body = re.sub(r"<w:pPr>.*?</w:pPr>", "", body, flags=re.S)
        body = re.sub(r"<w:rPr>.*?</w:rPr>", "", body, flags=re.S)
        body = body.rstrip() + f"<w:pPr>{ppr}</w:pPr><w:rPr>{rpr}</w:rPr>"
        xml = xml[:m.start()] + m.group(1) + body + m.group(3) + xml[m.end():]

    black = '<w:color w:val="000000"/>'
    font = f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:cs="{FALLBACK}"/>'
    hfont = f'<w:rFonts w:ascii="{HEADING_FONT}" w:hAnsi="{HEADING_FONT}" w:cs="{HEADING_FONT}"/>'
    if PROFILE == "bc":
        restyle("Title", '<w:spacing w:before="0" w:after="120"/><w:jc w:val="center"/>', hfont + black + '<w:b/><w:sz w:val="28"/>')
        restyle("Subtitle", '<w:spacing w:before="0" w:after="240"/><w:jc w:val="center"/>', hfont + '<w:color w:val="404040"/><w:sz w:val="22"/>')
        restyle("Heading1", '<w:keepNext/><w:spacing w:before="360" w:after="120"/>', hfont + black + '<w:b/><w:sz w:val="24"/>')
        restyle("Heading2", '<w:keepNext/><w:spacing w:before="240" w:after="80"/>', hfont + black + '<w:b/><w:sz w:val="22"/>')
        restyle("Heading3", '<w:keepNext/><w:spacing w:before="160" w:after="60"/>', hfont + black + '<w:b/><w:i/><w:sz w:val="22"/>')
        restyle("Compact", '<w:spacing w:before="0" w:after="60"/>', font + f'<w:sz w:val="{BODY_SZ}"/>')
        restyle("FirstParagraph", '<w:spacing w:before="0" w:after="120"/>', font + f'<w:sz w:val="{BODY_SZ}"/>')
        restyle("BodyText", '<w:spacing w:before="0" w:after="120"/>', font + f'<w:sz w:val="{BODY_SZ}"/>')
        return xml
    restyle("Title", '<w:spacing w:before="0" w:after="120"/><w:jc w:val="left"/>', font + black + '<w:b/><w:sz w:val="32"/>')
    restyle("Subtitle", '<w:spacing w:before="0" w:after="240"/>', font + '<w:color w:val="404040"/><w:sz w:val="24"/>')
    restyle("Heading1", '<w:keepNext/><w:spacing w:before="320" w:after="120"/><w:pBdr><w:bottom w:val="single" w:sz="6" w:space="2" w:color="000000"/></w:pBdr>',
            font + black + '<w:b/><w:caps/><w:sz w:val="22"/>')
    restyle("Heading2", '<w:keepNext/><w:spacing w:before="220" w:after="80"/>', font + black + '<w:b/><w:sz w:val="21"/>')
    restyle("Heading3", '<w:keepNext/><w:spacing w:before="160" w:after="60"/>', font + black + '<w:b/><w:i/><w:sz w:val="21"/>')
    restyle("Compact", '<w:spacing w:before="0" w:after="80"/>', font + '<w:sz w:val="21"/>')
    restyle("FirstParagraph", '<w:spacing w:before="0" w:after="120"/>', font + '<w:sz w:val="21"/>')
    restyle("BodyText", '<w:spacing w:before="0" w:after="120"/>', font + '<w:sz w:val="21"/>')
    return xml

def patch_sectpr(xml):
    # US Letter, 1in margins
    xml = re.sub(r'<w:pgSz [^>]*/>', '<w:pgSz w:w="12240" w:h="15840"/>', xml)
    xml = re.sub(r'<w:pgMar [^>]*/>', '<w:pgMar w:top="1296" w:right="1296" w:bottom="1296" w:left="1296" w:header="720" w:footer="720" w:gutter="0"/>', xml)
    return xml

def main():
    tmp = Path(tempfile.mkdtemp())
    default = tmp / "default.docx"
    subprocess.run(["quarto", "pandoc", "-o", str(default), "--print-default-data-file", "reference.docx"], check=True)
    src = zipfile.ZipFile(default)
    OUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "word/styles.xml":
                data = patch_styles(data.decode("utf8")).encode("utf8")
            elif item.filename == "word/document.xml":
                data = patch_sectpr(data.decode("utf8")).encode("utf8")
            dst.writestr(item, data)
    shutil.rmtree(tmp)
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
