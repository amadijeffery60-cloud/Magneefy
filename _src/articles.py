"""Insights articles: a small Markdown converter, original featured artwork,
and loading of the article source files in _src/articles/*.md.

Supported Markdown: ## / ### headings, paragraphs, - and 1. lists, | tables,
> quotes, **bold**, `code`, [links](url), and raw HTML blocks (lines starting
with "<" are passed through untouched).
"""
from pathlib import Path
import html
import re

SRC = Path(__file__).resolve().parent / "articles"


# ---------------------------------------------------------------- markdown
def _inline(text):
    t = html.escape(text, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    # typographic quotes and apostrophes (outside tags)
    parts = re.split(r"(<[^>]+>)", t)
    for i, p in enumerate(parts):
        if not p.startswith("<"):
            p = re.sub(r'"([^"]*)"', "“\\1”", p)
            p = p.replace("'", "’")
            parts[i] = p
    return "".join(parts)


def slugify(s):
    s = re.sub(r"^\d+\.\s*", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def md_to_html(md):
    """Returns (html, toc) where toc is a list of (id, title) for ## headings."""
    blocks = re.split(r"\n\s*\n", md.strip())
    out, toc = [], []
    for b in blocks:
        lines = b.strip("\n").split("\n")
        first = lines[0]
        if first.startswith("<"):
            out.append(b)
        elif first.startswith("### "):
            out.append(f"<h3>{_inline(first[4:])}</h3>")
        elif first.startswith("## "):
            title = first[3:].strip()
            hid = slugify(title)
            toc.append((hid, title))
            out.append(f'<h2 id="{hid}">{_inline(title)}</h2>')
        elif first.startswith("|"):
            rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines if not re.match(r"^\|\s*-", l)]
            head = "".join(f"<th>{_inline(c)}</th>" for c in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
            out.append(f'<div class="a-table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
        elif first.startswith("> "):
            paras = "".join(f"<p>{_inline(l[2:])}</p>" for l in lines)
            out.append(f'<blockquote class="a-quote">{paras}</blockquote>')
        elif re.match(r"^- ", first):
            items = "".join(f"<li>{_inline(l[2:])}</li>" for l in lines)
            out.append(f"<ul>{items}</ul>")
        elif re.match(r"^\d+\. ", first):
            items = "".join(f"<li>{_inline(re.sub(r'^\d+\.\s', '', l))}</li>" for l in lines)
            out.append(f"<ol>{items}</ol>")
        else:
            out.append(f"<p>{_inline(' '.join(lines))}</p>")
    return "\n".join(out), toc


def load_articles():
    arts = []
    for f in sorted(SRC.glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        _, fm, body = raw.split("---", 2)
        meta = {}
        for line in fm.strip().split("\n"):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
        meta["related"] = [r.strip() for r in meta.get("related", "").split(",") if r.strip()]
        meta["html"], meta["toc"] = md_to_html(body)
        meta["excerpt"] = meta["description"]
        meta["image"] = f'assets/img/insights/{meta["slug"]}.svg'
        meta["url"] = f'insights/{meta["slug"]}/'
        arts.append(meta)
    return arts


# ---------------------------------------------------------------- artwork (original, 1200x675)
_BG = '''<rect width="1200" height="675" fill="#141916"/>
<radialGradient id="gl" cx="78%" cy="18%" r="70%"><stop offset="0" stop-color="#16A36A" stop-opacity=".28"/><stop offset="1" stop-color="#16A36A" stop-opacity="0"/></radialGradient>
<rect width="1200" height="675" fill="url(#gl)"/>
<g stroke="#29332D" stroke-opacity=".55">''' + "".join(f'<line x1="{x}" y1="0" x2="{x}" y2="675"/>' for x in range(0, 1201, 100)) + "".join(f'<line x1="0" y1="{y}" x2="1200" y2="{y}"/>' for y in range(0, 676, 100)) + "</g>"

_FONT = 'font-family="Manrope, Inter, Arial, sans-serif"'


def _card(x, y, w, h, stroke="#29332D", fill="#1B211D", r=14, op=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2" opacity="{op}"/>'


def _label(x, y, text, size=22, fill="#FFFFFF", weight=700, op=1, anchor="start"):
    return f'<text x="{x}" y="{y}" {_FONT} font-size="{size}" font-weight="{weight}" fill="{fill}" opacity="{op}" text-anchor="{anchor}">{text}</text>'


def _check(cx, cy, r=18):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#16A36A"/><path d="M{cx - 8} {cy} l6 6 l11 -12" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'


def art(slug):
    g = []
    if slug == "why-businesses-lose-leads":
        rows = [("New enquiry · Website", 1, "#29332D"), ("Quote request · Email", .55, "#29332D"), ("Callback · Phone", .28, "#29332D"), ("DM · Instagram", .14, "#29332D")]
        for i, (t, op, s) in enumerate(rows):
            y = 120 + i * 115
            g.append(_card(110 + i * 26, y, 420, 88, s, op=op))
            g.append(f'<circle cx="{150 + i * 26}" cy="{y + 44}" r="8" fill="#A5ADA7" opacity="{op}"/>')
            g.append(_label(176 + i * 26, y + 52, t, 24, "#FFFFFF", 700, op))
        g.append('<path d="M560 164 C 680 164, 680 330, 800 330" fill="none" stroke="#16A36A" stroke-width="3" stroke-dasharray="8 9"/>')
        g.append(_card(800, 270, 300, 120, "#26C982"))
        g.append(_check(850, 330))
        g.append(_label(884, 322, "Customer", 28, "#FFFFFF", 800))
        g.append(_label(884, 352, "Followed up · Won", 19, "#A5ADA7", 600))
        g.append(_label(110, 600, "ENQUIRIES WITHOUT A FOLLOW-UP GO COLD", 18, "#26C982", 800))
    elif slug == "automated-lead-follow-up-system":
        steps = [("Now", "Acknowledge"), ("Day 1", "First follow-up"), ("Day 3", "Share info"), ("Day 5", "Check in"), ("Day 7", "Final follow-up")]
        g.append('<line x1="160" y1="340" x2="1040" y2="340" stroke="#29332D" stroke-width="4"/>')
        g.append('<line x1="160" y1="340" x2="600" y2="340" stroke="#26C982" stroke-width="4"/>')
        for i, (d, t) in enumerate(steps):
            x = 160 + i * 220
            done = i <= 2
            if done:
                g.append(_check(x, 340, 22))
            else:
                g.append(f'<circle cx="{x}" cy="340" r="20" fill="#141916" stroke="#29332D" stroke-width="4"/>')
            g.append(_label(x, 270, d, 20, "#26C982" if done else "#A5ADA7", 800, anchor="middle"))
            g.append(_label(x, 412, t, 22, "#FFFFFF" if done else "#A5ADA7", 700, anchor="middle"))
        g.append(_card(160, 480, 520, 96))
        g.append(_label(196, 520, "AUTOMATION RUNNING", 16, "#26C982", 800))
        g.append(_label(196, 552, "Form → CRM → Email → Team task", 24, "#FFFFFF", 700))
    elif slug == "ai-search-small-business-visibility-2027":
        for r, op in [(130, .9), (210, .6), (300, .4), (400, .25)]:
            g.append(f'<circle cx="600" cy="360" r="{r}" fill="none" stroke="#29332D" stroke-width="2" opacity="{op}"/>')
        g.append(_card(330, 140, 540, 76, "#29332D", "#1B211D", 38))
        g.append('<circle cx="380" cy="178" r="13" fill="none" stroke="#A5ADA7" stroke-width="3"/><line x1="390" y1="188" x2="402" y2="200" stroke="#A5ADA7" stroke-width="3"/>')
        g.append(_label(420, 186, "Who can help my business grow?", 24, "#FFFFFF", 600))
        g.append(_card(360, 270, 480, 200, "#26C982"))
        g.append('<path d="M400 302 l6 14 l14 6 l-14 6 l-6 14 l-6 -14 l-14 -6 l14 -6z" fill="#26C982"/>')
        g.append(_label(432, 330, "AI ANSWER", 16, "#26C982", 800))
        for i, w in enumerate([400, 360, 300]):
            g.append(f'<rect x="400" y="{360 + i * 26}" width="{w}" height="10" rx="5" fill="#29332D"/>')
        g.append(f'<rect x="400" y="436" width="180" height="22" rx="11" fill="none" stroke="#16A36A" stroke-width="2"/>')
        g.append(_label(490, 452, "yourbusiness.com", 14, "#26C982", 700, anchor="middle"))
        for cx, cy in [(240, 250), (960, 470), (880, 150), (300, 560)]:
            g.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="#16A36A"/>')
    elif slug == "business-tasks-to-automate":
        tasks = ["Enquiries", "Scheduling", "Email follow-ups", "Invoices", "Onboarding", "Social posts", "Reporting"]
        for i, t in enumerate(tasks):
            col, row = i % 4, i // 4
            x, y = 110 + col * 255, 150 + row * 210
            done = i in (0, 1, 2, 4, 6)
            g.append(_card(x, y, 225, 170, "#26C982" if done else "#29332D"))
            g.append(_label(x + 26, y + 46, f"0{i + 1}", 18, "#26C982", 800))
            g.append(_label(x + 26, y + 128, t, 24, "#FFFFFF", 700))
            if done:
                g.append(_check(x + 186, y + 40, 16))
        x, y = 110 + 3 * 255, 360
        g.append(_card(x, y, 225, 170, "#16A36A", "#16A36A"))
        g.append(_label(x + 26, y + 70, "Time back", 26, "#FFFFFF", 800))
        g.append(_label(x + 26, y + 104, "for growth", 26, "#FFFFFF", 800))
    elif slug == "business-standard-operating-procedures":
        g.append(_card(330, 90, 540, 500, "#29332D"))
        g.append(_label(372, 150, "SOP · CUSTOMER ENQUIRIES", 16, "#26C982", 800))
        g.append(_label(372, 190, "How we handle new enquiries", 28, "#FFFFFF", 800))
        steps = ["Check incoming enquiries", "Create the CRM record", "Send an acknowledgement", "Assign an owner", "Schedule the next follow-up"]
        for i, s in enumerate(steps):
            y = 250 + i * 62
            g.append(f'<circle cx="390" cy="{y - 8}" r="17" fill="none" stroke="#16A36A" stroke-width="2.5"/>')
            g.append(_label(390, y - 1, str(i + 1), 17, "#26C982", 800, anchor="middle"))
            g.append(_label(424, y, s, 22, "#FFFFFF" if i < 4 else "#A5ADA7", 600))
        g.append(_card(840, 420, 250, 96, "#26C982"))
        g.append(_label(866, 458, "OWNER", 14, "#26C982", 800))
        g.append(_label(866, 490, "Support Assistant", 21, "#FFFFFF", 700))
        g.append('<rect x="150" y="200" width="150" height="190" rx="12" fill="#1B211D" stroke="#29332D" stroke-width="2" opacity=".55"/><rect x="120" y="230" width="150" height="190" rx="12" fill="#1B211D" stroke="#29332D" stroke-width="2" opacity=".35"/>')
    elif slug == "measure-digital-marketing-performance":
        for i, (t, x) in enumerate([("♥ 500", 140), ("+15% followers", 140), ("2,000 views", 140)]):
            g.append(_card(x, 150 + i * 120, 300, 84, op=.45))
            g.append(_label(x + 28, 202 + i * 120, t, 24, "#A5ADA7", 700, .7))
        g.append('<line x1="480" y1="120" x2="480" y2="560" stroke="#29332D" stroke-width="2" stroke-dasharray="6 8"/>')
        bars = [(560, 120), (650, 170), (740, 240), (830, 300), (920, 380)]
        for i, (x, h) in enumerate(bars):
            fill = "#16A36A" if i == 4 else "#1B211D"
            g.append(f'<rect x="{x}" y="{520 - h}" width="64" height="{h}" rx="6" fill="{fill}" stroke="{"#16A36A" if i == 4 else "#29332D"}" stroke-width="2"/>')
        g.append('<polyline points="592,390 682,340 772,270 862,210 952,130" fill="none" stroke="#26C982" stroke-width="4" stroke-linejoin="round"/>')
        g.append('<circle cx="952" cy="130" r="9" fill="#26C982"/>')
        g.append(_label(560, 580, "QUALIFIED ENQUIRIES → CUSTOMERS", 18, "#26C982", 800))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675" role="img"><defs></defs>{_BG}{"".join(g)}</svg>'
