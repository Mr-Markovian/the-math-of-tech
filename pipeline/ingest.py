"""
ingest.py — Step 00 (fetch): get a MATH-FAITHFUL markdown file into
content/inbox/, preferring LaTeX-native sources over PDF text extraction.

Why: a PDF stores positioned glyphs, not LaTeX — markitdown flattens
\\sqrt{d_k} into unicode soup and silently drops display equations. When
the real LaTeX exists upstream, fetch THAT instead:

    arXiv   e-print LaTeX source  → pandoc → markdown ($…$ math intact)
            fallback: ar5iv HTML (embeds the original TeX) → pandoc
    blogs   page HTML → pandoc (extracts TeX from MathJax/KaTeX MathML)

Usage (needs pandoc on PATH; it's in the tmot env via environment.yml):
    python pipeline/ingest.py 1706.03762 --name attention
    python pipeline/ingest.py https://arxiv.org/abs/1706.03762 --name attention
    python pipeline/ingest.py https://blog.example.com/post --name lora

Output: content/inbox/<name>.md — then run "TASK ingest for <name>" as
usual (it cleans the file AND builds the equations.md registry).

Last resort for scanned / non-arXiv PDFs: markitdown paper.pdf (or
Mathpix/Nougat OCR) — expect degraded math; verify equations.md against
the paper extra carefully in that case.
"""
import argparse
import gzip
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "Mozilla/5.0 (tmot-pipeline; academic use)"}
ARXIV_ID = re.compile(
    r"^(?:https?://(?:www\.)?arxiv\.org/(?:abs|pdf|e-print)/)?"
    r"(\d{4}\.\d{4,5})(v\d+)?(?:\.pdf)?/?$", re.I)


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def require_pandoc():
    if shutil.which("pandoc") is None:
        sys.exit("pandoc not found on PATH. Install it into the env:\n"
                 "  conda env update -f environment.yml --prune\n"
                 "(or one-time system: sudo apt install pandoc)")


def pandoc(src_args, workdir: Path) -> str:
    """Run pandoc → gfm markdown with $…$ math kept as raw TeX."""
    out = workdir / "_out.md"
    cmd = ["pandoc", *src_args, "-t", "gfm+tex_math_dollars",
           "--wrap=none", "--markdown-headings=atx", "-o", str(out)]
    r = subprocess.run(cmd, cwd=workdir, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"pandoc failed: {r.stderr.strip()[:400]}")
    return out.read_text(encoding="utf-8")


def safe_extract(tar: tarfile.TarFile, dest: Path):
    for m in tar.getmembers():
        p = Path(m.name)
        if p.is_absolute() or ".." in p.parts:
            raise RuntimeError(f"unsafe tar member: {m.name}")
    tar.extractall(dest)


def find_main_tex(src_dir: Path) -> Path | None:
    cands = []
    for f in src_dir.rglob("*.tex"):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "\\documentclass" in text:
            cands.append((("\\begin{document}" in text), f.stat().st_size, f))
    if not cands:
        return None
    cands.sort(reverse=True)
    return cands[0][2]


def from_arxiv_source(aid: str, tmp: Path) -> str:
    """e-print tarball (or single gzipped .tex) → pandoc. The gold path:
    this IS the author's LaTeX."""
    blob = fetch(f"https://arxiv.org/e-print/{aid}")
    if blob[:4] == b"%PDF":
        raise RuntimeError("PDF-only submission (no LaTeX source on arXiv)")
    src = tmp / "src"
    src.mkdir()
    if blob[:2] == b"\x1f\x8b":
        blob = gzip.decompress(blob)
    payload = tmp / "payload"
    payload.write_bytes(blob)
    if tarfile.is_tarfile(payload):
        with tarfile.open(payload) as t:
            safe_extract(t, src)
    else:
        (src / "main.tex").write_bytes(blob)
    main = find_main_tex(src)
    if main is None:
        raise RuntimeError("no \\documentclass .tex found in source")
    return pandoc([str(main.relative_to(src)), "-f", "latex"], src)


def from_ar5iv(aid: str, tmp: Path) -> str:
    """ar5iv HTML keeps the original TeX inside MathML annotations —
    pandoc pulls it back out as $…$."""
    html = fetch(f"https://ar5iv.labs.arxiv.org/html/{aid}")
    f = tmp / "page.html"
    f.write_bytes(html)
    return pandoc([f.name, "-f", "html"], tmp)


def from_url(url: str, tmp: Path) -> str:
    html = fetch(url)
    f = tmp / "page.html"
    f.write_bytes(html)
    return pandoc([f.name, "-f", "html"], tmp)


def tidy(md: str) -> str:
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip() + "\n"


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="arXiv id, arXiv URL, or webpage URL")
    ap.add_argument("--name", help="project name -> content/inbox/<name>.md "
                                   "(default: derived from the source)")
    args = ap.parse_args()
    require_pandoc()

    m = ARXIV_ID.match(args.source.strip())
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        if m:
            aid = m.group(1) + (m.group(2) or "")
            name = args.name or ("arxiv_" + m.group(1).replace(".", "_"))
            origin = f"https://arxiv.org/abs/{aid}"
            try:
                md, method = from_arxiv_source(aid, tmp), "arxiv e-print latex + pandoc"
            except Exception as e:
                print(f"e-print source path failed ({e}); trying ar5iv …")
                try:
                    md, method = from_ar5iv(aid, tmp), "ar5iv html + pandoc"
                except Exception as e2:
                    sys.exit(f"ar5iv failed too ({e2}).\nLast resort: markitdown "
                             f"the PDF (degraded math — verify equations.md "
                             f"against the paper carefully).")
        else:
            if not args.source.startswith(("http://", "https://")):
                sys.exit("source must be an arXiv id or an http(s) URL "
                         "(for local PDFs use markitdown as before)")
            origin = args.source
            name = args.name or re.sub(
                r"\W+", "_", args.source.rstrip("/").rsplit("/", 1)[-1])[:40]
            try:
                md, method = from_url(args.source, tmp), "page html + pandoc"
            except Exception as e:
                sys.exit(f"fetch/convert failed: {e}")

    out = ROOT / "content" / "inbox" / f"{name}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    header = (f"<!-- fetched: {origin} | method: {method} | "
              f"date: {date.today().isoformat()} -->\n\n")
    out.write_text(header + tidy(md), encoding="utf-8")
    n_math = len(re.findall(r"\$[^$]+\$", md))
    print(f"OK -> {out.relative_to(ROOT)}  ({method}; ~{n_math} inline/display "
          f"math fragments preserved)\nNext: run TASK ingest for {name}")


if __name__ == "__main__":
    main()
