"""Resolve and download open-access copies of the references in paper/refs.bib."""

import argparse
import concurrent.futures
import csv
import difflib
import json
import pathlib
import re
import subprocess
import sys
import threading
import time
from urllib.parse import urlparse

import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
BIB = ROOT / "paper" / "refs.bib"
OUT = ROOT / "refs"
MAILTO = "luk036@users.noreply.github.com"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
MIN_BYTES = 25_000
BAD_HOSTS = (
    "dl.acm.org",
    "ieeexplore.ieee.org",
    "sciencedirect.com",
    "link.springer.com",
    "onlinelibrary.wiley.com",
    "tandfonline.com",
    "cambridge.org",
    "jstor.org",
    "nature.com",
    "mdpi.com",
)
OVERRIDES = {
    "boyd2004convex": "https://web.stanford.edu/~boyd/cvxbook/bv_cvxbook.pdf",
}
STOP = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "under",
    "using",
    "based",
    "via",
    "its",
    "their",
    "this",
    "that",
    "some",
    "new",
    "toward",
    "towards",
}

OUT.mkdir(exist_ok=True)
S = requests.Session()
S.headers.update({"User-Agent": UA})
_s2_lock = threading.Lock()
_s2_last = [0.0]


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def parse_bib(text):
    out = []
    for typ, key, body in re.findall(r"@(\w+)\{([^,]+),(.*?)\n\}", text, re.S):

        def f(name):
            m = re.search(name + r"\s*=\s*[{\"](.+?)[}\"],?\s*\n", body, re.S)
            return re.sub(r"\s+", " ", m.group(1)).strip() if m else None

        authors = f("author") or ""
        surname = (
            authors.split(",")[0].strip()
            if "," in authors
            else (authors.split()[0] if authors else "")
        )
        out.append(
            {
                "type": typ.lower(),
                "key": key.strip(),
                "title": re.sub(r"[{}]", "", f("title") or ""),
                "year": f("year"),
                "doi": (f("doi") or "").lower(),
                "surname": surname,
            }
        )
    return out


def get_json(url, params=None, timeout=25):
    for attempt in range(2):
        try:
            r = S.get(url, params=params, timeout=timeout)
            if r.status_code == 429:
                time.sleep(2 + attempt * 2)
                continue
            if r.status_code == 200:
                return r.json()
        except Exception:
            time.sleep(0.5)
    return None


def s2_call(url, params):
    with _s2_lock:
        wait = 1.3 - (time.time() - _s2_last[0])
        if wait > 0:
            time.sleep(wait)
        _s2_last[0] = time.time()
    return get_json(url, params)


def openalex_doi(doi):
    d = get_json(
        f"https://api.openalex.org/works/https://doi.org/{doi}", {"mailto": MAILTO}
    )
    return [d] if d else []


def openalex_title(title):
    d = get_json(
        "https://api.openalex.org/works",
        {"filter": f"title.search:{title}", "per-page": 8, "mailto": MAILTO},
    )
    return d.get("results", []) if d else []


def s2_lookup(doi, title):
    fields = "title,year,openAccessPdf,externalIds"
    if doi:
        d = s2_call(
            f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}",
            {"fields": fields},
        )
        return [d] if d else []
    d = s2_call(
        "https://api.semanticscholar.org/graph/v1/paper/search",
        {"query": title, "fields": fields, "limit": 6},
    )
    return d.get("data", []) if d else []


def arxiv(title):
    q = 'ti:"' + re.sub(r"[^A-Za-z0-9 ]", " ", title) + '"'
    try:
        r = S.get(
            "http://export.arxiv.org/api/query",
            params={"search_query": q, "max_results": 5},
            timeout=25,
        )
        ids = (
            re.findall(r"<id>http://arxiv.org/abs/([^<]+)</id>", r.text)
            if r.status_code == 200
            else []
        )
        return [f"https://arxiv.org/pdf/{i}.pdf" for i in ids]
    except Exception:
        return []


def pdf_text(path):
    try:
        r = subprocess.run(
            ["pdftotext", "-f", "1", "-l", "2", str(path), "-"],
            capture_output=True,
            timeout=30,
        )
        return r.stdout.decode("utf-8", "ignore")
    except Exception:
        return ""


def verify(path, entry):
    if not path.exists() or path.stat().st_size < MIN_BYTES:
        return False, "too small"
    if not path.read_bytes()[:1024].startswith(b"%PDF"):
        return False, "not a PDF"
    text = norm(pdf_text(path))
    if not text:
        return True, "unverified-scan"
    words = [w for w in norm(entry["title"]).split() if len(w) >= 4 and w not in STOP]
    if not words:
        return True, "unverified-short-title"
    cover = sum(w in text for w in words) / len(words)
    author = norm(entry["surname"]) in text if entry["surname"] else False
    if cover >= 0.65 or (cover >= 0.45 and author):
        return True, f"verified cover={cover:.2f}"
    return False, f"title mismatch cover={cover:.2f}"


def oa_urls(rec):
    out = []
    for loc in [rec.get("best_oa_location")] + (rec.get("locations") or []):
        if loc and loc.get("is_oa") and loc.get("pdf_url"):
            out.append(loc["pdf_url"])
    return out


def download(url, dest):
    host = urlparse(url).netloc.lower()
    if any(host == h or host.endswith("." + h) for h in BAD_HOSTS):
        return False, "blocked host"
    reason = ""
    try:
        r = S.get(url, timeout=60, allow_redirects=True, stream=True)
        if r.status_code == 200:
            total, chunks = 0, []
            for chunk in r.iter_content(65536):
                total += len(chunk)
                if total > 90_000_000:
                    return False, "too large"
                chunks.append(chunk)
            data = b"".join(chunks)
            if data.startswith(b"%PDF"):
                dest.write_bytes(data)
                return True, f"{total} bytes"
        reason = f"HTTP {r.status_code}"
    except Exception as e:
        reason = str(e)[:50]
    return curl_download(url, dest, reason)


def curl_download(url, dest, reason):
    tmp = dest.with_name(dest.name + ".part")
    try:
        r = subprocess.run(
            [
                "curl.exe",
                "-sS",
                "-L",
                "-A",
                UA,
                "--max-time",
                "90",
                "-o",
                str(tmp),
                "-w",
                "%{http_code}",
                url,
            ],
            capture_output=True,
            timeout=120,
        )
        code = r.stdout.decode(errors="ignore").strip()
        if (
            code == "200"
            and tmp.exists()
            and tmp.read_bytes()[:4] == b"%PDF"
            and tmp.stat().st_size >= MIN_BYTES
        ):
            tmp.replace(dest)
            return True, f"{dest.stat().st_size} bytes (curl)"
        tmp.unlink(missing_ok=True)
        return False, f"{reason}; curl {code}"
    except Exception as e:
        tmp.unlink(missing_ok=True)
        return False, f"{reason}; curl {str(e)[:40]}"


def resolve(entry, force=False):
    key, title, doi = entry["key"], entry["title"], entry["doi"]
    dest = OUT / f"{key}.pdf"
    if dest.exists() and not force:
        ok, why = verify(dest, entry)
        if ok:
            return {
                **entry,
                "status": "cached",
                "source": "",
                "file": dest.name,
                "note": why,
            }
        dest.unlink()

    if entry["type"] in ("book", "misc") and key not in OVERRIDES:
        return {
            **entry,
            "status": "skip",
            "source": "",
            "file": "",
            "note": entry["type"],
        }

    cands = []
    if key in OVERRIDES:
        cands.append((OVERRIDES[key], "override"))
    for rec in (openalex_doi(doi) if doi else []) or openalex_title(title):
        if sim(rec.get("display_name") or "", title) >= 0.75:
            cands += [(u, "openalex") for u in oa_urls(rec)]
    for rec in s2_lookup(doi or None, None if doi else title):
        if sim(rec.get("title") or "", title) < 0.75:
            continue
        if (rec.get("openAccessPdf") or {}).get("url"):
            cands.append((rec["openAccessPdf"]["url"], "semanticscholar"))
        ax = (rec.get("externalIds") or {}).get("ArXiv")
        if ax:
            cands.append((f"https://arxiv.org/pdf/{ax}.pdf", "arxiv"))
    if not cands:
        cands += [(u, "arxiv") for u in arxiv(title)]

    seen, note = set(), ""
    for url, src in cands:
        if url in seen:
            continue
        seen.add(url)
        ok, msg = download(url, dest)
        if ok:
            vok, why = verify(dest, entry)
            if vok:
                return {
                    **entry,
                    "status": "downloaded",
                    "source": src,
                    "file": dest.name,
                    "note": f"{why}; {url}",
                }
            dest.unlink()
            note = f"{src}: rejected ({why})"
        else:
            note = f"{src}: {msg}"
    dest.unlink(missing_ok=True)
    return {**entry, "status": "not_found", "source": "", "file": "", "note": note}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    entries = parse_bib(BIB.read_text(encoding="utf-8"))
    if a.only:
        entries = [e for e in entries if e["key"] in set(a.only)]

    rows = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(resolve, e, a.force): e for e in entries}
        for n, fut in enumerate(concurrent.futures.as_completed(futs), 1):
            r = fut.result()
            rows.append(r)
            print(
                f"[{n:02}/{len(entries)}] {r['key']}: {r['status']} {r['note'][:80]}",
                flush=True,
            )

    rows.sort(key=lambda r: r["key"])
    for r in rows:
        r.pop("surname", None)
    (OUT / "_manifest.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with (OUT / "_status.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "key",
                "type",
                "year",
                "doi",
                "status",
                "source",
                "file",
                "note",
                "title",
            ],
        )
        w.writeheader()
        w.writerows(rows)
    ok = sum(r["status"] in ("downloaded", "cached") for r in rows)
    print(f"\n{ok}/{len(rows)} available; see refs/_status.csv", flush=True)


if __name__ == "__main__":
    sys.exit(main())
