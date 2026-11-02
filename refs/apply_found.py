import importlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
fr = importlib.import_module("fetch_refs")

entries = {e["key"]: e for e in fr.parse_bib(fr.BIB.read_text(encoding="utf-8"))}
items = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))

for item in items:
    key, url = item["key"], item["url"]
    entry = entries.get(key)
    if entry is None:
        print(f"{key}: NO SUCH KEY", flush=True)
        continue
    dest = fr.OUT / f"{key}.pdf"
    ok, msg = fr.download(url, dest)
    if not ok:
        print(f"{key}: FAIL {msg}", flush=True)
        continue
    vok, why = fr.verify(dest, entry)
    if not vok:
        dest.unlink(missing_ok=True)
        print(f"{key}: REJECT {why}", flush=True)
        continue
    print(f"{key}: OK {why}", flush=True)
