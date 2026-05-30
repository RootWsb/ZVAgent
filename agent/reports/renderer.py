import html
import os
import re
import textwrap
from datetime import datetime

from common.log import logger


def _markdown_to_html(markdown_text: str) -> str:
    try:
        from markdown_it import MarkdownIt

        return MarkdownIt("commonmark", {"html": False}).render(markdown_text)
    except Exception:
        escaped = html.escape(markdown_text)
        return "<pre>" + escaped + "</pre>"


def _extract_headings(markdown_text: str) -> list:
    headings = []
    used = set()
    for line in str(markdown_text or "").splitlines():
        m = re.match(r"^(#{2,3})\s+(.+?)\s*$", line)
        if not m:
            continue
        title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", m.group(2)).strip()
        title = re.sub(r"[#*_`]+", "", title).strip()
        if not title or title == "参考来源":
            continue
        slug = _slugify(title)
        base = slug
        idx = 2
        while slug in used:
            slug = f"{base}-{idx}"
            idx += 1
        used.add(slug)
        headings.append({"level": len(m.group(1)), "title": title, "id": slug})
    return headings


def _slugify(text: str) -> str:
    raw = re.sub(r"\s+", "-", str(text or "").strip().lower())
    raw = re.sub(r"[^\w\u4e00-\u9fff-]+", "", raw)
    return raw.strip("-") or "section"


def _apply_heading_ids(body: str, headings: list) -> str:
    queue = list(headings)

    def repl(match):
        if not queue:
            return match.group(0)
        item = queue.pop(0)
        level = match.group(1)
        attrs = match.group(2) or ""
        content = match.group(3)
        if " id=" in attrs:
            return match.group(0)
        return f'<h{level}{attrs} id="{html.escape(item["id"])}">{content}</h{level}>'

    return re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", repl, body, flags=re.S)


def _build_toc(headings: list) -> str:
    items = [h for h in headings if h["level"] == 2]
    if not items:
        return ""
    rows = "\n".join(
        f'<a class="toc-item" href="#{html.escape(h["id"])}">'
        f'<span>{idx}. {html.escape(h["title"])}</span><i></i></a>'
        for idx, h in enumerate(items, 1)
    )
    return f"""
  <section class="toc">
    <div class="toc-label">目录</div>
    {rows}
  </section>
"""


def render_html(markdown_text: str, title: str, html_path: str):
    headings = _extract_headings(markdown_text)
    body = _apply_heading_ids(_markdown_to_html(markdown_text), headings)
    toc = _build_toc(headings)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{html.escape(title)}</title>
  <style>
    @page {{ size: A4; margin: 22mm 18mm 20mm; }}
    body {{
      font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", Arial, sans-serif;
      color: #172033;
      font-size: 13px;
      line-height: 1.75;
      background: #ffffff;
    }}
    .cover {{
      min-height: 260px;
      border-bottom: 4px solid #2563eb;
      padding: 42px 0 30px;
      margin-bottom: 28px;
      page-break-after: always;
    }}
    .kicker {{
      color: #2563eb;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }}
    .cover h1 {{
      font-size: 34px;
      line-height: 1.25;
      margin: 18px 0 18px;
      max-width: 680px;
      letter-spacing: 0;
    }}
    .meta {{ color: #667085; font-size: 12px; }}
    .cover-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-top: 34px;
      max-width: 620px;
    }}
    .cover-chip {{
      border: 1px solid #d8e0ec;
      border-radius: 8px;
      padding: 10px 12px;
      background: #f8fafc;
    }}
    .cover-chip b {{ display: block; color: #334155; font-size: 11px; margin-bottom: 2px; }}
    .toc {{
      page-break-after: always;
      margin: 0 0 24px;
    }}
    .toc-label {{
      font-size: 22px;
      font-weight: 700;
      color: #0f172a;
      margin-bottom: 18px;
      padding-bottom: 8px;
      border-bottom: 1px solid #d7dee8;
    }}
    .toc-item {{
      display: flex;
      align-items: center;
      gap: 10px;
      color: #334155;
      text-decoration: none;
      padding: 6px 0;
      font-size: 13px;
    }}
    .toc-item i {{
      flex: 1;
      height: 1px;
      border-bottom: 1px dotted #cbd5e1;
      order: 2;
    }}
    .toc-item span {{ order: 1; }}
    h1 {{ font-size: 28px; line-height: 1.25; margin: 10px 0 14px; }}
    h2 {{
      font-size: 20px;
      margin-top: 28px;
      border-bottom: 1px solid #d7dee8;
      padding-bottom: 6px;
      page-break-after: avoid;
    }}
    h3 {{ font-size: 16px; margin-top: 20px; page-break-after: avoid; }}
    p {{ margin: 9px 0; }}
    ul, ol {{ padding-left: 22px; }}
    li {{ margin: 5px 0; }}
    blockquote {{
      border-left: 4px solid #16a34a;
      background: #f2fbf6;
      margin: 14px 0;
      padding: 8px 14px;
    }}
    table {{ width: 100%; border-collapse: collapse; margin: 14px 0; }}
    th, td {{ border: 1px solid #d7dee8; padding: 8px; vertical-align: top; }}
    th {{ background: #f5f7fa; }}
    code {{ background: #f1f5f9; padding: 2px 4px; border-radius: 4px; }}
    a {{ color: #1d4ed8; text-decoration: none; }}
    h2[id*="参考"] + ol,
    h2[id*="参考"] + ul {{
      font-size: 11.5px;
      color: #475569;
      line-height: 1.6;
      word-break: break-all;
    }}
    .report-body {{ page-break-before: auto; }}
  </style>
</head>
<body>
  <section class="cover">
    <div class="kicker">ZVAgent Report</div>
    <h1>{html.escape(title)}</h1>
    <div class="meta">自动生成的研究报告，可继续要求 Agent 修订和扩展。</div>
    <div class="cover-grid">
      <div class="cover-chip"><b>生成时间</b>{html.escape(generated_at)}</div>
      <div class="cover-chip"><b>交付格式</b>PDF / Markdown / HTML</div>
      <div class="cover-chip"><b>工作流</b>调研、写作、排版</div>
      <div class="cover-chip"><b>版本</b>V4</div>
    </div>
  </section>
  {toc}
  <main class="report-body">
    {body}
  </main>
</body>
</html>"""
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(page)


def render_pdf(html_path: str, pdf_path: str, markdown_text: str, title: str):
    try:
        _render_pdf_with_playwright(html_path, pdf_path)
        return
    except Exception as e:
        logger.warning(f"[Reports] Playwright PDF render failed, using fallback renderer: {e}")
    _render_pdf_fallback(markdown_text, title, pdf_path)


def _render_pdf_with_playwright(html_path: str, pdf_path: str):
    from pathlib import Path
    from playwright.sync_api import sync_playwright

    uri = Path(html_path).resolve().as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(uri, wait_until="load")
        page.pdf(
            path=pdf_path,
            format="A4",
            print_background=True,
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=(
                "<div style='width:100%;font-size:9px;color:#94a3b8;"
                "padding:0 16mm;display:flex;justify-content:space-between;"
                "font-family:Arial,sans-serif;'>"
                "<span>ZVAgent Report</span>"
                "<span><span class='pageNumber'></span> / <span class='totalPages'></span></span>"
                "</div>"
            ),
            margin={"top": "18mm", "right": "16mm", "bottom": "18mm", "left": "16mm"},
        )
        browser.close()


def _strip_markdown(markdown_text: str) -> str:
    text = re.sub(r"```.*?```", "", markdown_text, flags=re.S)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^[#>*\-\s]+", "", text, flags=re.M)
    return text


def _pdf_obj(num: int, body: str) -> bytes:
    return f"{num} 0 obj\n{body}\nendobj\n".encode("latin-1")


def _hex_text(value: str) -> str:
    return value.encode("utf-16-be", errors="ignore").hex().upper()


def _escape_pdf_text(value: str) -> str:
    return "<" + _hex_text(value) + ">"


def _render_pdf_fallback(markdown_text: str, title: str, pdf_path: str):
    text = title + "\n\n" + _strip_markdown(markdown_text)
    raw_lines = []
    for para in text.splitlines():
        para = para.strip()
        if not para:
            raw_lines.append("")
            continue
        raw_lines.extend(textwrap.wrap(para, width=34, break_long_words=False, replace_whitespace=False))

    pages = []
    current = []
    for line in raw_lines:
        current.append(line)
        if len(current) >= 34:
            pages.append(current)
            current = []
    if current:
        pages.append(current)
    if not pages:
        pages = [[title]]

    objects = []
    page_nums = []
    font_num = 3
    next_num = 4
    for lines in pages:
        content_num = next_num
        next_num += 1
        page_num = next_num
        next_num += 1
        stream_lines = ["BT", "/F1 12 Tf", "1 0 0 1 56 785 Tm", "18 TL"]
        for line in lines:
            stream_lines.append(f"{_escape_pdf_text(line)} Tj")
            stream_lines.append("T*")
        stream_lines.append("ET")
        stream = "\n".join(stream_lines).encode("latin-1")
        objects.append(_pdf_obj(content_num, f"<< /Length {len(stream)} >>\nstream\n" + stream.decode("latin-1") + "\nendstream"))
        page_body = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {font_num} 0 R >> >> "
            f"/Contents {content_num} 0 R >>"
        )
        objects.append(_pdf_obj(page_num, page_body))
        page_nums.append(page_num)

    kids = " ".join(f"{n} 0 R" for n in page_nums)
    base_objects = [
        _pdf_obj(1, "<< /Type /Catalog /Pages 2 0 R >>"),
        _pdf_obj(2, f"<< /Type /Pages /Kids [{kids}] /Count {len(page_nums)} >>"),
        _pdf_obj(font_num, "<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light /Encoding /UniGB-UCS2-H >>"),
    ]
    all_objects = base_objects + objects

    output = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    offsets = [0]
    for obj in all_objects:
        offsets.append(sum(len(part) for part in output))
        output.append(obj)
    xref_pos = sum(len(part) for part in output)
    count = max(next_num, len(offsets))
    xref = [f"xref\n0 {count}\n0000000000 65535 f \n"]
    for i in range(1, count):
        off = offsets[i] if i < len(offsets) else 0
        xref.append(f"{off:010d} 00000 n \n")
    xref.append(f"trailer\n<< /Size {count} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n")
    output.append("".join(xref).encode("latin-1"))

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    with open(pdf_path, "wb") as f:
        f.write(b"".join(output))
