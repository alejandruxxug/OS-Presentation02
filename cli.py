#!/usr/bin/env python3
"""
Interactive CLI for the DocumentDB demo API.

Run:
    python3 cli.py
    # or with an override:
    API_URL=https://xxxxx.execute-api.us-east-1.amazonaws.com/Prod python3 cli.py
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError

DEFAULT_API = "https://8dq2yzjmaj.execute-api.us-east-1.amazonaws.com/Prod"
API = os.environ.get("API_URL", DEFAULT_API).rstrip("/")


def _request(method, path, body=None, query=None):
    url = f"{API}{path}"
    if query:
        url += "?" + urllib.parse.urlencode({k: v for k, v in query.items() if v not in (None, "")})

    data = None
    headers = {"accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode()
        headers["content-type"] = "application/json"

    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode() or "{}"
            return resp.status, json.loads(raw) if raw else {}
    except HTTPError as e:
        raw = e.read().decode()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"raw": raw}
        return e.code, payload
    except URLError as e:
        return 0, {"error": f"network: {e.reason}"}


def show(status, payload):
    print(f"\n  HTTP {status}")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()


def _prompt(label, default=None, cast=str, required=True):
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"  {label}{suffix}: ").strip()
        if not raw:
            if default is not None:
                return default
            if not required:
                return None
            print("    value required")
            continue
        try:
            return cast(raw)
        except (ValueError, TypeError) as exc:
            print(f"    invalid: {exc}")


def _csv_list(raw):
    return [x.strip() for x in raw.split(",") if x.strip()]


def op_health():
    show(*_request("GET", "/health"))


def op_root():
    show(*_request("GET", "/"))


def op_list():
    limit = _prompt("limit", default=20, cast=int)
    skip = _prompt("skip", default=0, cast=int)
    show(*_request("GET", "/products", query={"limit": limit, "skip": skip}))


def op_get():
    pid = _prompt("product id")
    show(*_request("GET", f"/products/{pid}"))


def op_search():
    print("  (press enter to skip any filter)")
    show(*_request("GET", "/products/search/", query={
        "category":      _prompt("category", required=False),
        "min_price":     _prompt("min_price", cast=float, required=False),
        "max_price":     _prompt("max_price", cast=float, required=False),
        "name_contains": _prompt("name_contains", required=False),
        "tag":           _prompt("tag", required=False),
    }))


def op_create():
    body = {
        "name":     _prompt("name"),
        "category": _prompt("category"),
        "price":    _prompt("price", cast=float),
        "stock":    _prompt("stock", cast=int),
        "tags":     _csv_list(_prompt("tags (comma-separated)", default="")),
    }
    show(*_request("POST", "/products", body=body))


def op_patch():
    pid = _prompt("product id")
    print("  (press enter to skip a field)")
    body = {}
    for key, cast in [("name", str), ("category", str), ("price", float), ("stock", int)]:
        val = _prompt(key, cast=cast, required=False)
        if val is not None:
            body[key] = val
    tags_raw = _prompt("tags (comma-separated)", required=False)
    if tags_raw is not None:
        body["tags"] = _csv_list(tags_raw)
    if not body:
        print("  nothing to update\n")
        return
    show(*_request("PATCH", f"/products/{pid}", body=body))


def op_put():
    pid = _prompt("product id")
    body = {
        "name":     _prompt("name"),
        "category": _prompt("category"),
        "price":    _prompt("price", cast=float),
        "stock":    _prompt("stock", cast=int),
        "tags":     _csv_list(_prompt("tags (comma-separated)", default="")),
    }
    show(*_request("PUT", f"/products/{pid}", body=body))


def op_delete():
    pid = _prompt("product id")
    confirm = _prompt(f"type DELETE to confirm removing {pid}").upper()
    if confirm != "DELETE":
        print("  cancelled\n")
        return
    show(*_request("DELETE", f"/products/{pid}"))


def op_stats():
    show(*_request("GET", "/products/stats/by-category"))


MENU = [
    ("Health check                  (GET  /health)",                  op_health),
    ("Service root                  (GET  /)",                        op_root),
    ("List products                 (GET  /products)",                op_list),
    ("Get product by id             (GET  /products/{id})",           op_get),
    ("Search products               (GET  /products/search/)",        op_search),
    ("Create product                (POST /products)",                op_create),
    ("Patch product (partial)       (PATCH /products/{id})",          op_patch),
    ("Replace product               (PUT /products/{id})",            op_put),
    ("Delete product                (DELETE /products/{id})",         op_delete),
    ("Aggregation by category       (GET  /products/stats/...)",      op_stats),
]


def main():
    print(f"\n  DocumentDB Demo CLI")
    print(f"  API: {API}\n")
    while True:
        print("=" * 60)
        for i, (label, _) in enumerate(MENU, start=1):
            print(f"  {i:2}.  {label}")
        print(f"   0.  exit")
        print("=" * 60)
        choice = input("  > ").strip()
        if choice in ("0", "q", "quit", "exit"):
            return
        if not choice.isdigit() or not (1 <= int(choice) <= len(MENU)):
            print("  invalid choice\n")
            continue
        try:
            MENU[int(choice) - 1][1]()
        except KeyboardInterrupt:
            print("\n  aborted\n")
        except Exception as exc:
            print(f"  error: {exc}\n")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nbye")
        sys.exit(0)
