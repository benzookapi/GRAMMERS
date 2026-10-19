#!/usr/bin/env python3
"""Build the complete and free sample editions from the original manga pages."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from pypdf import PdfReader, PdfWriter
from pypdf.generic import DictionaryObject, NameObject, TextStringObject
from reportlab import rl_config
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf"
TMP = ROOT / "tmp" / "pdfs"
W, H = 420, 595
INK = HexColor("#101d24")
GREEN = HexColor("#68e2ad")
MUTED = HexColor("#59656d")
EPISODES = [
    "Get started", "Heads up!", "Cognition", "Fusion", "Extension",
    "New Stage", "True Story", "New world", "New hero", "Dark side",
    "Innovation", "New power", "Hackathon!!", "Valunability", "Forever",
]


def fonts():
    font_dir = Path("/System/Library/Fonts/Supplemental")
    pdfmetrics.registerFont(TTFont("Body", str(font_dir / "Arial.ttf")))
    pdfmetrics.registerFont(TTFont("Bold", str(font_dir / "Arial Bold.ttf")))
    pdfmetrics.registerFont(TTFont("JP", str(font_dir / "Arial Unicode.ttf")))


def text(c, x, y, content, size=12, font="Body", color=INK):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, content)


def footer(c, label):
    c.setStrokeColor(HexColor("#d9dfe2"))
    c.line(30, 38, W - 30, 38)
    text(c, 30, 23, "GRAMMERS / benzookapi", 8, color=MUTED)
    c.setFont("Body", 8)
    c.drawRightString(W - 30, 23, label)


def cover(c, sample, background=INK):
    c.setFillColor(background)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    text(c, 28, 553, "ANOTHER PROGRAMMERS' STORY", 9, "Bold", GREEN)
    text(c, 25, 491, "GRAMMERS", 51, "Bold", white)
    text(c, 29, 462, "エンジニアSF漫画", 15, "JP", white)
    c.setFillColor(white)
    c.rect(28, 195, W - 56, 241, fill=1, stroke=0)
    c.drawImage(str(ROOT / "Sun/image.gr.png"), 32, 201, 175, 226,
                preserveAspectRatio=True, anchor="c", mask="auto")
    c.drawImage(str(ROOT / "Rail/image.gr.png"), 213, 201, 175, 226,
                preserveAspectRatio=True, anchor="c", mask="auto")
    label = "FREE SAMPLE" if sample else "COMPLETE EDITION"
    jp = "無料試し読み版 / 第1・2話" if sample else "完全版 / 全15話"
    text(c, 29, 153, label, 20, "Bold", GREEN)
    text(c, 30, 125, jp, 14, "JP", white)
    text(c, 30, 85, "JAPANESE LANGUAGE MANGA", 10, "Bold", white)
    text(c, 30, 65, "benzookapi", 10, "Body", white)
    text(c, 30, 31, "DIGITAL EDITION / 2026", 8, "Body", GREEN)
    c.showPage()


def contents(c, sample, pages):
    text(c, 30, 550, "CONTENTS", 25, "Bold")
    text(c, 31, 522, "目次", 15, "JP")
    text(c, 31, 496, "Japanese manga. Read panels from right to left.", 9, color=MUTED)
    text(c, 31, 478, "本文は日本語です。コマは右から左へお読みください。", 10, "JP", MUTED)
    y = 437
    for n in range(1, (2 if sample else 15) + 1):
        dest = f"episode-{n}"
        text(c, 31, y, f"{n:02d}", 12, "Bold")
        text(c, 66, y, EPISODES[n - 1], 11)
        c.setFont("Body", 10)
        c.drawRightString(W - 31, y, str(pages[n]))
        c.linkAbsolute(f"Episode {n}", dest, (28, y - 5, W - 28, y + 15), thickness=0)
        y -= 23
    text(c, 31, 66, "各話のタイトルをクリックすると移動できます。", 9, "JP", MUTED)
    footer(c, "02")
    c.showPage()


def closing(c, full_url):
    text(c, 30, 548, "CONTINUE THE STORY", 23, "Bold")
    text(c, 31, 509, "続きは完全版で。", 22, "JP")
    for y, line in zip([451, 426, 401], [
        "サンの前に現れた怪人。突然目覚めた能力。",
        "レイル、そして新たな仲間との出会い。",
        "プログラマーたちの物語は、ここから動き出します。",
    ]):
        text(c, 31, y, line, 12, "JP")
    c.setFillColor(INK)
    c.rect(30, 250, W - 60, 111, fill=1, stroke=0)
    text(c, 46, 329, "GRAMMERS / COMPLETE EDITION", 13, "Bold", GREEN)
    text(c, 46, 301, "全15話・原稿177ページ収録", 14, "JP", white)
    text(c, 46, 276, "All 15 episodes in one Japanese-language PDF.", 10, color=white)
    c.linkURL(full_url, (30, 250, W - 30, 361), relative=0, thickness=0)
    text(c, 31, 213, "完全版の商品ページ / Get the complete edition", 11, "JP")
    # Wrap long URLs without shrinking the readable CTA text.
    for i in range(0, len(full_url), 58):
        text(c, 31, 187 - (i // 58) * 14, full_url[i:i + 58], 8, color=MUTED)
    text(c, 31, 130, "この試し読み版には第1・2話の原稿28ページを収録しています。", 10, "JP", MUTED)
    footer(c, "FREE SAMPLE")
    c.showPage()


def colophon(c, sample):
    text(c, 30, 548, "GRAMMERS", 30, "Bold")
    text(c, 31, 512, "無料試し読み版" if sample else "完全版", 19, "JP")
    lines = [
        ("作者 / Creator", "benzookapi"),
        ("作品", "エンジニアSF漫画 GRAMMERS"),
        ("収録内容", "第1・2話 / 原稿28ページ" if sample else "全15話 / 原稿177ページ"),
        ("形式 / Format", "PDF / 日本語 / Japanese"),
        ("デジタル版作成日", "2026年10月18日"),
    ]
    y = 449
    for label, value in lines:
        text(c, 31, y, label, 10, "JP", MUTED)
        text(c, 31, y - 23, value, 13, "JP")
        y -= 60
    text(c, 31, 120, "Geechs Magazine 掲載作品のデジタル再編集版。", 10, "JP")
    text(c, 31, 99, "各話の扉・本文・最終ページを含む原稿を収録しています。", 10, "JP")
    text(c, 31, 78, "ストアの商品説明の言語にかかわらず、漫画本文は日本語です。", 10, "JP")
    footer(c, "benzookapi.com")
    c.showPage()


def build(sample, full_url):
    name = "grammers-free-sample-ja.pdf" if sample else "grammers-complete-ja.pdf"
    manuscript = []
    starts = {}
    page_number = 3
    for n in range(1, (2 if sample else 15) + 1):
        sources = sorted((ROOT / "_works" / f"No{n}").glob("*.png"))
        assert sources, f"No pages in episode {n}"
        starts[n] = page_number
        for source in sources:
            manuscript.append((n, source, page_number))
            page_number += 1
    raw = TMP / name
    c = canvas.Canvas(str(raw), pagesize=(W, H), pageCompression=1)
    c.setTitle("GRAMMERS - Free Sample (Japanese)" if sample else "GRAMMERS - Complete Edition (Japanese)")
    c.setAuthor("benzookapi")
    c.setSubject("Japanese science-fiction manga about programmers")
    cover(c, sample)
    contents(c, sample, starts)
    manifest = []
    for n, source, number in manuscript:
        if number == starts[n]:
            c.bookmarkPage(f"episode-{n}")
            c.addOutlineEntry(f"第{n}話 / {EPISODES[n - 1]}", f"episode-{n}")
        asset = TMP / "assets" / f"No{n}-{source.stem}.jpg"
        if not asset.exists():
            im = Image.open(source).convert("RGB")
            im.thumbnail((2400, 3400), Image.Resampling.LANCZOS)
            im.save(asset, quality=92, subsampling=0, optimize=True)
        c.drawImage(str(asset), 0, 0, W, H, preserveAspectRatio=True, anchor="c")
        c.showPage()
        manifest.append({"source":str(source.relative_to(ROOT)), "pdf_page":number,
                         "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest()})
    if sample:
        closing(c, full_url)
    colophon(c, sample)
    c.save()
    reader = PdfReader(raw)
    writer = PdfWriter()
    writer.clone_document_from_reader(reader)
    writer._root_object[NameObject("/Lang")] = TextStringObject("ja-JP")
    writer._root_object[NameObject("/ViewerPreferences")] = DictionaryObject({NameObject("/Direction"):NameObject("/R2L")})
    # Prefer single pages: consecutive episode covers need no artificial blank pages.
    writer.page_layout = "/SinglePage"
    writer.page_mode = "/UseOutlines"
    dest = OUT / name
    with dest.open("wb") as f:
        writer.write(f)
    expected = 32 if sample else 180
    assert len(PdfReader(dest).pages) == expected
    record = {"file":name,"pages":expected,"manuscript_pages":len(manuscript),
              "bytes":dest.stat().st_size,"sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
              "sources":manifest}
    (OUT / name.replace(".pdf", ".manifest.json")).write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in record.items() if k!="sources"}), flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--full-product-url", default="https://benzookapi.com/products/grammers-complete-edition-japanese-pdf")
    p.add_argument("--product-covers-only", action="store_true")
    p.add_argument("--product-cover-background", default="#101d24")
    args=p.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    (TMP/"assets").mkdir(parents=True,exist_ok=True)
    rl_config.useA85 = 0
    fonts()
    if args.product_covers_only:
        product_out = ROOT / "output" / "shopify"
        product_out.mkdir(parents=True, exist_ok=True)
        for sample, label in [(False, "complete"), (True, "sample")]:
            dest = product_out / f"grammers-{label}-cover-original.pdf"
            c = canvas.Canvas(str(dest), pagesize=(W, H))
            cover(c, sample, HexColor(args.product_cover_background))
            c.save()
            print(dest)
        return
    build(False,args.full_product_url)
    build(True,args.full_product_url)


if __name__ == "__main__":
    main()
