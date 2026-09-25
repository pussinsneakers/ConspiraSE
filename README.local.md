doomscroll/
├── README.md
├── pyproject.toml
├── Makefile
├── .gitignore               # ignores data/raw, data/processed, indexes/
├── data/
│   ├── README.md            # where to get the corpus, expected format
│   └── sample.jsonl         # ~200 synthetic docs for tests and quick demo
├── indexes/                 # built index files land here (gitignored)
├── scripts/
│   ├── prepare_corpus.py
│   └── benchmark.py
├── src/doomscroll/
│   ├── __init__.py
│   ├── config.py
│   ├── corpus.py
│   ├── tokenize.py
│   ├── postings.py
│   ├── index.py
│   ├── storage.py
│   ├── permuterm.py
│   ├── kgram.py
│   ├── query.py
│   ├── vectors.py
│   ├── rank.py
│   ├── kmeans.py
│   ├── engine.py
│   ├── cli.py
│   └── web.py
└── tests/
    ├── test_tokenize.py
    ├── test_index.py
    ├── test_postings.py
    ├── test_wildcard.py
    ├── test_query.py
    ├── test_rank.py
    └── test_kmeans.py