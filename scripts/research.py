"""Fetch primary-source metadata; retain a dated audit without source page copies."""
import argparse
import json
import time
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.metadata = {}
        self.title = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "meta":
            key = attrs.get("name", attrs.get("property", ""))
            if key.startswith("citation_") or key in ("description", "og:description", "og:title"):
                self.metadata.setdefault(key, []).append(attrs.get("content", ""))

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title.append(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--urls", nargs="+")
    parser.add_argument("--catalog", default="data/sources.json")
    parser.add_argument("--output", default="research/source-audit.json")
    args = parser.parse_args()
    urls = args.urls or [s["url"] for s in json.loads(Path(args.catalog).read_text(encoding="utf-8"))]
    target = Path(args.output)
    previous = json.loads(target.read_text(encoding="utf-8")) if target.exists() else []
    records = {record["url"]: record for record in previous}
    for url in urls:
        record = {"url": url, "checkedAt": datetime.now(timezone.utc).isoformat()}
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "AgenticRLAtlas/0.1 (personal research; metadata verification)"})
            with urllib.request.urlopen(request, timeout=35) as response:
                content = response.read().decode("utf-8", errors="replace")
                page = MetadataParser()
                page.feed(content)
                record.update(status=response.status, finalUrl=response.url, title=" ".join(page.title).strip(), metadata=page.metadata)
            print(json.dumps(record, ensure_ascii=True), flush=True)
        except Exception as error:
            record["error"] = str(error)
            print(json.dumps(record), flush=True)
        records[url] = record
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(list(records.values()), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        time.sleep(1)


if __name__ == "__main__":
    main()
