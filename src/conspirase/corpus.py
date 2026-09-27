"""
Reading datafile from disk
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator
from pathlib import Path
import logging
import json

log = logging.getLogger(__name__)

@dataclass (frozen=True, slots = True)
class Document: 
    """
    One document as stored on disk, no tokenization

    doc_id: external ID, tweet ID
    text: raw, unnormalized text
    meta: dict with user handle, name & timestemp 
    """
    doc_id:str
    text:str
    meta:dict[str, str]

# --------------------- Cleaning helpers ------------------
def normalize_whitespace(text:str) -> str: 
    """Collapse whitespace (incl newline and tabs) into single spaces."""
    return " ".join(text.split())

def clean_tweet(text:str) -> str:
    """Undo the escaping in the tweet corpus. """
    text = text.replace("[NEWLINE]", " ").replace("[TAB]", " ")
    return normalize_whitespace(text)

# --------------------- Readers -------------------------
def read_tweets (path:str | Path) -> Iterator[Document]:
    """
    Yild document from the tab-seperated tweet file. The function acts as a generator, so that the large corpus does not sit in the memory all at once.
    Expected columns: timestemp, tweet_id, user_handle, username, raw_text
    Skips malformed lines, empty tweets and duplicate IDs.  
    """ 
    path = Path(path) #can pass either a string or a Path
    with path.open("r", encoding = "utf-8") as f:
        malformed = duplicates = empty = 0
        seen = set () #set of str of seend IDs
        for line in f:
            parts = line.rstrip("\n").split("\t",4)
            if len(parts) != 5: #lines which could not be separated into 5 parts 
                malformed += 1
                continue
            
            timestemp, tweet_id, user_handle, username, raw_text = parts 

            if tweet_id in seen: 
                duplicates += 1 
                continue
            seen.add(tweet_id)

            text = clean_tweet(raw_text) #tweets that are empty 
            if not text:
                empty += 1 
                continue

            yield Document(
                doc_id = tweet_id,
                text = text,
                meta = {"user_handle": user_handle, "username": username, "timestemp":timestemp}
            )

    log.info("%s: kept %d, skipped %d malformed, %d empty, %d duplicates",
             path.name, len(seen) - empty, malformed, empty, duplicates)

def read_jsonl(path:str | Path) -> Iterator[Document]:
    """Yield document from the jsonl file"""
    path = Path(path) 
    malformed = duplicates = empty = 0
    seen = set ()
    with path.open("r", encoding = "utf-8") as fh:
        for line_no, line in enumerate (fh, start = 1):
            line = line.strip()
            if not line: #skipping blank lines 
                continue
            try: 
                record = json.loads(line)
            except json.JSONDecodeError as exc: 
                raise ValueError (f"{path}:{line_no}: malformed JSON") from exc

            try:
                doc_id = str(record["_id"])
            except KeyError as exc:
                raise ValueError(f"{path}:{line_no}: missing '_id'")
            if doc_id in seen:
                duplicates += 1 
                continue
            seen.add(doc_id)

            text = normalize_whitespace(record.get("text", ""))
            if not text:
                empty += 1 
                continue

            yield Document (
                doc_id= doc_id,
                text = text, 
                meta = {k: str(v) for k, v in record.items() if k not in ("_id", "text")}
            )
    log.info("%s: kept %d, skipped %d malformed, %d empty, %d duplicates",
                 path.name, len(seen) - empty, malformed, empty, duplicates)

def load(path: str | Path):
    path = Path(path)
    format = path.suffix.lower()
    if format == ".csv" or format == ".tsv":
        return read_tweets(path)
    elif format == ".jsonl":
        return read_jsonl (path)
    else:
        raise ValueError(f"unsupported file type '{format}' (expected .csv, .tsv or .jsonl)")






