#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup


# ------------------------------
# Config and helpers
# ------------------------------

WIKI_ENDPOINTS = {
    "simple": "https://simple.wikipedia.org/w/api.php",
}

RTL_LANGS = {"ar", "fa", "he", "ur"}


def debug(msg: str):
    print(f"[mini-book] {msg}")


def which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)


def clean_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Remove references and tables
    for tag in soup.select("table, sup.reference, span.mw-editsection"):
        tag.decompose()
    text = soup.get_text("\n")
    # Collapse excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def word_count(text: str) -> int:
    return len(re.findall(r"\w+", text))


def safe_filename(s: str) -> str:
    s = re.sub(r"[^\w\-\s]", "", s, flags=re.UNICODE).strip()
    s = re.sub(r"\s+", "-", s)
    return s or "book"


@dataclass
class Chapter:
    title: str
    content: str
    questions: List[str]
    answers: List[str]


# ------------------------------
# Wikipedia fetching (Simple + standard)
# ------------------------------

def wiki_search(topic: str, lang: str) -> Tuple[str, str]:
    """Return (endpoint, canonical_title) for best page match.
    Prefer Simple English Wikipedia for English, else language Wikipedia.
    """
    if lang.lower().startswith("en"):
        endpoint = WIKI_ENDPOINTS["simple"]
    else:
        endpoint = f"https://{lang}.wikipedia.org/w/api.php"

    params = {
        "action": "opensearch",
        "search": topic,
        "limit": 1,
        "namespace": 0,
        "format": "json",
        "origin": "*",
    }
    r = requests.get(endpoint, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data and len(data) >= 2 and data[1]:
        title = data[1][0]
        return endpoint, title
    return endpoint, topic


def wiki_sections(endpoint: str, title: str) -> List[dict]:
    params = {
        "action": "parse",
        "page": title,
        "prop": "sections",
        "format": "json",
        "origin": "*",
    }
    r = requests.get(endpoint, params=params, timeout=20)
    r.raise_for_status()
    js = r.json()
    return js.get("parse", {}).get("sections", [])


def wiki_section_html(endpoint: str, title: str, index: int) -> str:
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "section": index,
        "format": "json",
        "origin": "*",
    }
    r = requests.get(endpoint, params=params, timeout=20)
    r.raise_for_status()
    js = r.json()
    html = js.get("parse", {}).get("text", {}).get("*", "")
    return html


def wiki_lead_html(endpoint: str, title: str) -> str:
    params = {
        "action": "parse",
        "page": title,
        "prop": "text",
        "section": 0,
        "format": "json",
        "origin": "*",
    }
    r = requests.get(endpoint, params=params, timeout=20)
    r.raise_for_status()
    js = r.json()
    return js.get("parse", {}).get("text", {}).get("*", "")


# ------------------------------
# Optional LLM (OpenAI) for expansion/translation
# ------------------------------

def have_openai() -> bool:
    try:
        import openai  # noqa: F401
        return bool(os.environ.get("OPENAI_API_KEY"))
    except Exception:
        return False


def llm_expand_and_translate(section_title: str, source_text: str, audience_lang: str, words: int) -> Tuple[str, List[str], List[str]]:
    """Use OpenAI to expand content for kids 8–12, produce ~words, questions and answers in audience_lang."""
    import openai

    client = openai.OpenAI()
    system = (
        "You are an educator writing kid-friendly content for ages 8–12. "
        "Use clear, safe language, short paragraphs, and concrete examples."
    )
    prompt = f"""
Create a chapter titled "{section_title}" for a kids (8–12) mini-book in language code "{audience_lang}".
Base the facts on the provided source (summarize and reorganize in your own words; do not copy):
--- SOURCE START ---
{source_text[:8000]}
--- SOURCE END ---

Requirements:
- About {words} words.
- Friendly tone; explain terms simply.
- End the chapter with a section 'שאלות'/'Questions' containing 3 assessment questions.
- Then provide an 'Answers' section listing the answers concisely.

Return JSON with keys: chapter_text (string without the Q&A), questions (array of 3 strings), answers (array of 3 strings). The language must be {audience_lang}.
"""
    resp = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.7,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content
    try:
        data = json.loads(content)
        chapter_text = data.get("chapter_text", "").strip()
        questions = [q.strip() for q in data.get("questions", [])][:3]
        answers = [a.strip() for a in data.get("answers", [])][:3]
        return chapter_text, questions, answers
    except Exception:
        # Fallback: return source text truncated, with placeholder Q&A
        fallback = source_text.strip()
        return fallback, ["Question 1?", "Question 2?", "Question 3?"], ["Answer 1", "Answer 2", "Answer 3"]


# ------------------------------
# Book assembly
# ------------------------------

def pick_sections(sections: List[dict], n: int = 7) -> List[dict]:
    ignore = {"references", "see also", "external links", "further reading", "bibliography", "notes", "sources"}
    selected = []
    for s in sections:
        line = s.get("line", "").strip()
        if not line:
            continue
        low = line.lower()
        if any(x in low for x in ignore):
            continue
        if s.get("toclevel", 1) > 2:
            continue
        selected.append(s)
        if len(selected) >= n:
            break
    return selected


def make_chapters(endpoint: str, title: str, lang: str, count: int, words_per: int, use_llm: bool) -> Tuple[List[Chapter], str]:
    """Return chapters and attribution string."""
    chapters: List[Chapter] = []
    sections = wiki_sections(endpoint, title)
    chosen = pick_sections(sections, count)

    # If we have no sections, use lead only
    if not chosen:
        lead_html = wiki_lead_html(endpoint, title)
        lead_text = clean_text(lead_html)
        chap_text, qs, ans = (
            llm_expand_and_translate(title, lead_text, lang, words_per)
            if use_llm
            else (lead_text, ["?", "?", "?"], ["-", "-", "-"])
        )
        chapters.append(Chapter(title=title, content=chap_text, questions=qs, answers=ans))
    else:
        for s in chosen:
            idx = int(s.get("index"))
            stitle = s.get("line", f"Section {idx}")
            html = wiki_section_html(endpoint, title, idx)
            text = clean_text(html)
            if use_llm:
                chap_text, qs, ans = llm_expand_and_translate(stitle, text, lang, words_per)
            else:
                # Non-LLM fallback: take text and lightly reshape
                # If target language is not English, note limitation
                if lang.lower().startswith("en"):
                    base = text
                else:
                    base = (
                        f"[Auto-language note] This chapter is in English due to missing LLM/translator.\n\n" + text
                    )
                # pad to rough length by reiterating key points (simple fallback)
                while word_count(base) < int(0.7 * words_per):
                    base += "\n\n" + text[:1500]
                chap_text, qs, ans = base, ["?", "?", "?"], ["-", "-", "-"]
            chapters.append(Chapter(title=stitle, content=chap_text, questions=qs, answers=ans))

    # Attribution (CC BY-SA 4.0)
    project = "Simple English Wikipedia" if endpoint == WIKI_ENDPOINTS.get("simple") else f"Wikipedia ({endpoint})"
    attrib = (
        f"This mini-book incorporates material from {project} article '{title}', "
        "licensed under CC BY-SA 4.0. See https://creativecommons.org/licenses/by-sa/4.0/."
    )
    return chapters, attrib


def build_markdown(book_title: str, topic: str, lang: str, chapters: List[Chapter], attrib: str, author: str) -> str:
    today = datetime.date.today().strftime("%B %Y")
    rtl_note = "(RTL)" if lang in RTL_LANGS else ""
    lines = []
    lines.append(f"---")
    lines.append(f"title: \"{book_title}\"")
    lines.append(f"author: {author}")
    lines.append(f"date: {today}")
    lines.append(f"lang: {lang}")
    lines.append(f"---\n")

    lines.append(f"# {book_title} {rtl_note}\n")
    lines.append(f"A mini-book for kids ages 8–12 about '{topic}'.\n")
    lines.append(f"\n## Table of Contents\n")
    for i, ch in enumerate(chapters, 1):
        lines.append(f"{i}. [{ch.title}](#chapter-{i}-{safe_filename(ch.title).lower()})")
    lines.append("")

    for i, ch in enumerate(chapters, 1):
        anchor = f"chapter-{i}-{safe_filename(ch.title).lower()}"
        lines.append(f"\n---\n")
        lines.append(f"\n## {i}. {ch.title} {{#{anchor}}}\n")
        lines.append(ch.content.strip() + "\n")
        lines.append(f"\n### Questions\n")
        for q in ch.questions:
            lines.append(f"- {q}")

    # Appendix
    lines.append("\n---\n")
    lines.append("\n## Appendix: Answers\n")
    for i, ch in enumerate(chapters, 1):
        lines.append(f"\n### Chapter {i}: {ch.title}\n")
        for j, a in enumerate(ch.answers, 1):
            lines.append(f"- Q{j}: {a}")

    # Sources
    lines.append("\n---\n")
    lines.append("\n## Sources & License\n")
    lines.append(attrib)

    return "\n".join(lines) + "\n"


def write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_rtl_css(path: Path):
    css = """
html { direction: rtl; }
body { direction: rtl; unicode-bidi: embed; text-align: right; font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif; line-height: 1.6; }
h1,h2,h3,h4,h5,h6 { text-align: right; }
p,li { text-align: right; }
ol,ul { list-style-position: inside; padding-right: 0; margin-right: 0; }
code, pre { direction: ltr; text-align: left; }
"""
    write_text(path, css)


def run_cmd(cmd: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def render_pdf(markdown_path: Path, out_pdf: Path, lang: str) -> bool:
    """Render PDF using pandoc+tectonic for LTR; for RTL languages prefer HTML+LibreOffice if available."""
    outdir = out_pdf.parent

    # RTL path via soffice
    if lang in RTL_LANGS and which("soffice"):
        html_path = outdir / (markdown_path.stem + ".html")
        css_path = outdir / "mini_rtl.css"
        write_rtl_css(css_path)
        code, out, err = run_cmd([
            "pandoc", str(markdown_path), "-o", str(html_path), "--standalone", "-c", css_path.name, "--metadata", f"lang={lang}", "--toc"
        ], cwd=outdir)
        if code != 0:
            debug(f"pandoc HTML failed: {err.strip()}")
            return False
        code, out, err = run_cmd([
            "soffice", "--headless", "--convert-to", "pdf", html_path.name, "--outdir", "."
        ], cwd=outdir)
        if code == 0 and out_pdf.exists():
            return True
        return out_pdf.exists()

    # LTR or no soffice → try pandoc+tectonic
    if which("pandoc"):
        args = [
            "pandoc", str(markdown_path), "-o", str(out_pdf),
            "--pdf-engine=tectonic", "--toc",
            "-V", "geometry:margin=1in",
        ]
        # Use system fonts if present; otherwise let LaTeX pick defaults
        if lang in RTL_LANGS:
            # try a Hebrew-capable system font if available
            args += ["-V", "mainfont=Arial Hebrew Scholar"]
        code, out, err = run_cmd(args, cwd=outdir)
        if code == 0 and out_pdf.exists():
            return True
        debug(f"pandoc PDF failed: {err.strip()}")

    return False


def main():
    parser = argparse.ArgumentParser(description="Create a kids mini-book PDF (ages 8–12) from a topic.")
    parser.add_argument("topic", help="Topic to cover (e.g., 'Robotics')")
    parser.add_argument("--language", "-l", default="en", help="Target language code (e.g., en, he, ar)")
    parser.add_argument("--chapters", "-n", type=int, default=7, help="Number of chapters (default 7)")
    parser.add_argument("--words-per-chapter", "-w", type=int, default=2000, help="Target words per chapter (default 2000)")
    parser.add_argument("--title", "-t", default=None, help="Override book title")
    parser.add_argument("--author", "-a", default="MindQuest", help="Author name")
    parser.add_argument("--outdir", "-o", default=".", help="Output directory")
    parser.add_argument("--no-llm", action="store_true", help="Do not use LLM even if OPENAI_API_KEY is set")
    args = parser.parse_args()

    topic = args.topic.strip()
    lang = args.language.strip().lower()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    title = args.title or f"{topic} for Kids (Ages 8–12)"

    endpoint, page_title = wiki_search(topic, lang)
    debug(f"Using source: {endpoint} | page: {page_title}")

    use_llm = (not args.no_llm) and have_openai()
    if use_llm:
        debug("LLM enabled via OPENAI_API_KEY")
    else:
        debug("LLM disabled (no key found or --no-llm). Output may be shorter/English-only.")

    chapters, attrib = make_chapters(endpoint, page_title, lang, args.chapters, args.words_per_chapter, use_llm)

    book_md = build_markdown(title, topic, lang, chapters, attrib, author=args.author)
    base = safe_filename(f"{title}-{lang}")
    md_path = outdir / f"{base}.md"
    pdf_path = outdir / f"{base}.pdf"

    write_text(md_path, book_md)
    debug(f"Wrote markdown: {md_path}")

    ok = render_pdf(md_path, pdf_path, lang)
    if ok:
        debug(f"PDF created: {pdf_path}")
        print(str(pdf_path))
        sys.exit(0)
    else:
        debug("PDF rendering failed. Markdown is available for manual conversion.")
        print(str(md_path))
        sys.exit(2)


if __name__ == "__main__":
    main()
