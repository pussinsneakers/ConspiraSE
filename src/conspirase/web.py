"""
Web interface for the search engine.

A small Flask server with two routes:

- ``/`` serves the single-page front end (static/index.html).
- ``/api/search`` answers a query in Boolean, ranked or cluster mode and
  returns JSON. Every tweet comes back split into segments, with the words
  that match the query marked, so the page can highlight them.

Usage:
    python -m conspirase.web PATH [--port 8000] [--hide-handles]

Requires Flask (``python -m pip install flask``).
"""

from __future__ import annotations

import argparse
import logging
import re
import time
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from conspirase.engine import Engine, build_engine, cluster_search
from conspirase.kmeans import label
from conspirase.query import search
from conspirase.rank import rank
from conspirase.tokenize import normalize, terms

STATIC_DIR = Path(__file__).parent / "static"
MAX_LIMIT = 100

# A word in the tweet text: letters/digits, optionally joined by apostrophes,
# roughly what tokenize() treats as one token. (Regex is fine here: this is
# only for highlighting, not for retrieval.)
_WORD = re.compile(r"[^\W_]+(?:['’´`][^\W_]+)*")
_APOSTROPHES = str.maketrans({"’": "'", "´": "'", "`": "'"})
_OPERATORS = {"AND", "OR", "NOT"}


# --- highlighting ---

def query_term_groups(query: str, engine: Engine) -> dict[str, int]:
    """Map every index term a query can match to the number of its query word.

    The number decides the highlight color: all terms a wildcard expands to
    share the wildcard's number. Words after NOT are left out, since matching
    documents do not contain them.
    """
    groups: dict[str, int] = {}
    group = 0
    negate = False
    for word in query.split():
        if word in _OPERATORS:
            negate = word == "NOT"
            continue
        if "*" in word:
            try:
                matches = engine.permuterm.lookup(normalize(word))
            except ValueError:
                matches = []
        else:
            matches = terms(word)
        if matches and not negate:
            for term in matches:
                groups.setdefault(term, group)
            group += 1
        negate = False
    return groups


def segments(text: str, groups: dict[str, int]) -> list[dict]:
    """Split text into plain and matching pieces.

    Returns a list like [{"t": "plain text "}, {"t": "Impfung", "m": 0}, ...]
    where "m" is the query word number of a matching piece.
    """
    out: list[dict] = []
    pos = 0
    for match in _WORD.finditer(text):
        term = normalize(match.group().translate(_APOSTROPHES))
        if term not in groups:
            continue
        if match.start() > pos:
            out.append({"t": text[pos:match.start()]})
        out.append({"t": match.group(), "m": groups[term]})
        pos = match.end()
    if pos < len(text):
        out.append({"t": text[pos:]})
    return out


# --- app ---

def create_app(engine: Engine, hide_handles: bool = False) -> Flask:
    """Create the Flask app around an already built engine."""
    app = Flask(__name__, static_folder=None)

    def hits(scored: list[tuple[int, float | None]], groups: dict[str, int], limit: int) -> list[dict]:
        """Turn (doc_id, score) pairs into JSON hits, merging copy-pasted tweets.

        The corpus contains many copies of the same tweet under different IDs,
        often differing only in their shortened links. Tweets with the same
        terms (which ignores links, mentions and punctuation) are shown once,
        with a count.
        """
        out: list[dict] = []
        by_text: dict[tuple[str, ...], dict] = {}
        for doc_id, score in scored:
            text = tuple(terms(engine.docs[doc_id].text))
            if text in by_text:
                by_text[text]["copies"] += 1
                continue
            if len(out) == limit:
                continue  # keep counting copies of the hits already shown
            h = hit(doc_id, groups, score)
            h["copies"] = 1
            by_text[text] = h
            out.append(h)
        return out

    def hit(doc_id: int, groups: dict[str, int], score: float | None = None) -> dict:
        doc = engine.docs[doc_id]
        handle = "@user" if hide_handles else doc.meta.get("user_handle", "?")
        result = {"id": doc.doc_id, "handle": handle, "segments": segments(doc.text, groups)}
        if score is not None:
            result["score"] = round(score, 4)
        return result

    @app.get("/")
    def index_page():
        return send_from_directory(STATIC_DIR, "index.html")

    @app.get("/api/stats")
    def stats():
        return jsonify(docs=engine.index.num_docs(), terms=len(engine.index.dictionary))

    @app.get("/api/search")
    def api_search():
        query = request.args.get("q", "").strip()
        mode = request.args.get("mode", "boolean")
        limit = min(request.args.get("limit", 20, type=int), MAX_LIMIT)
        k = request.args.get("k", 4, type=int)

        if not query:
            return jsonify(error="empty query"), 400
        if mode not in ("boolean", "ranked", "clusters"):
            return jsonify(error=f"unknown mode '{mode}'"), 400

        start = time.perf_counter()
        groups = query_term_groups(query, engine)
        body: dict = {"query": query, "mode": mode}

        try:
            if mode == "boolean":
                ids = search(query, engine.index, engine.permuterm)
                body["total"] = len(ids)
                body["hits"] = hits([(i, None) for i in ids], groups, limit)
            elif mode == "ranked":
                results = rank(query, engine.index, engine.norms, k=limit)
                body["total"] = len(results)
                body["hits"] = hits(results, groups, limit)
            else:
                res = cluster_search(engine, query, max(1, k))
                body["total"] = len(res.ids)
                body["clusters"] = []
                for c, center in enumerate(res.centers):
                    members = [i for i, a in zip(res.ids, res.assignments) if a == c]
                    if not members:
                        continue
                    body["clusters"].append({
                        "label": label(center),
                        "size": len(members),
                        "rss": round(res.rss[c], 4),
                        "hits": hits([(i, None) for i in members], groups, limit),
                    })
        except ValueError as e:  # invalid queries, e.g. unsupported wildcards
            return jsonify(error=str(e)), 400

        body["ms"] = round((time.perf_counter() - start) * 1000, 1)
        return jsonify(body)

    return app


def main():
    """Build the engine and start the web server."""
    parser = argparse.ArgumentParser(description="Web interface for the search engine.")
    parser.add_argument("path", help="path to the data file")
    parser.add_argument("--host", default="127.0.0.1", help="address to listen on")
    parser.add_argument("--port", type=int, default=8000, help="port to listen on")
    parser.add_argument("--hide-handles", action="store_true",
                        help="show every author as @user (for screenshots and demos)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    # Built once at start-up; every request reuses it. Norms are always needed
    # here because the page offers ranked and cluster mode.
    engine = build_engine(args.path, with_norms=True)
    app = create_app(engine, hide_handles=args.hide_handles)
    print(f"Open http://{args.host}:{args.port} in your browser")
    app.run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
