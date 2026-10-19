"""
Shared setup for the search interfaces.

Builds everything a query needs (documents, inverted index, permuterm index
and, optionally, document norms) in one place, so the command-line interface
and the web server start up the same way. Also provides cluster_search(),
which ranks a query and groups the top results with k-means.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from conspirase.corpus import Document, load
from conspirase.index import InvertedIndex, build_index
from conspirase.kmeans import doc_vector, kmeans, rss
from conspirase.permuterm import PermutermIndex
from conspirase.rank import doc_norms, rank


@dataclass
class Engine:
    """Everything needed to answer queries over one document collection.

    Attributes:
        docs: the documents; docs[i] is the document with internal ID i.
        index: the inverted index built from docs.
        permuterm: the permuterm index over the index's vocabulary (wildcards).
        norms: document vector lengths for ranking, or None if not computed.
    """

    docs: list[Document]
    index: InvertedIndex
    permuterm: PermutermIndex
    norms: list[float] | None


@dataclass
class ClusterResult:
    """The outcome of cluster_search().

    Attributes:
        ids: internal IDs of the clustered documents, in ranked order.
        assignments: assignments[i] is the cluster number of ids[i].
        centers: centers[c] is the center vector of cluster c.
        rss: rss[c] is the residual sum of squares of cluster c.
    """

    ids: list[int]
    assignments: list[int]
    centers: list[dict[str, float]]
    rss: list[float]


def build_engine(path: str | Path, with_norms: bool = True) -> Engine:
    """Load the documents at path and build all indexes.

    The documents are kept in a list because the index does not store text:
    a search result i is shown by looking up docs[i].

    Args:
        path: data file (.csv, .tsv or .jsonl).
        with_norms: compute document norms (needed for ranking and clustering).
            Skipping them makes start-up faster when only Boolean search is used.
    """
    docs = list(load(path))
    index = build_index(docs)
    permuterm = PermutermIndex(index.dictionary.keys())
    norms = doc_norms(index) if with_norms else None
    return Engine(docs=docs, index=index, permuterm=permuterm, norms=norms)


def cluster_search(engine: Engine, query: str, k: int, pool: int = 50) -> ClusterResult:
    """Rank a query and group the top results into k clusters.

    Args:
        engine: an engine built with norms.
        query: free-text query, as for ranked search.
        k: number of clusters (reduced automatically if there are fewer results).
        pool: how many top-ranked documents to cluster.

    Raises:
        ValueError: if the engine has no norms.
    """
    if engine.norms is None:
        raise ValueError("clustering needs an engine built with norms")

    results = rank(query, engine.index, engine.norms, k=pool)
    ids = [doc_id for doc_id, _ in results]
    vectors = [doc_vector(engine.docs[i].text, engine.index) for i in ids]
    assignments, centers = kmeans(vectors, k)
    return ClusterResult(
        ids=ids,
        assignments=assignments,
        centers=centers,
        rss=rss(vectors, assignments, centers),
    )