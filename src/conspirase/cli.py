"""
An interactive command-line search over a document collection.

Loads the document, builds the inverted index, build the permuterm index, and compute document norms when in rank mode. There are two modes:
Boolean with wildcard and operators (default) and ranked (--ranked), with free-text TF-IDF and operators and wildcards have no effect. 
To end the search type "quit".
"""
import argparse
import logging

from conspirase.engine import build_engine, cluster_search
from conspirase.kmeans import label
from conspirase.query import search
from conspirase.rank import rank


def print_results(ids, docs, limit):
    """Print the result of a Boolean search."""
    print(f"The tweets matching the result: {len(ids)}")
    for doc_id in ids[:limit]:
        doc = docs[doc_id]
        print(f"User: {doc.meta.get('user_handle', '?')}, tweet: {doc.text[:100]}")


def print_ranked(results, docs):
    """Print the result of a ranked search."""
    print(f"Top {len(results)} results")
    for doc_id, score in results:
        doc = docs[doc_id]
        print(f"Score: {score:.3f}, User: {doc.meta.get('user_handle', '?')}, tweet: {doc.text[:100]}")


def print_clusters(ids, assignments, centers, scores, docs, limit):
    """Print each non-empty cluster: its label, size and RSS, then its top tweets."""
    for c in range(len(centers)):
        # Ranked IDs belonging to cluster c, still in score order.
        members = [doc_id for doc_id, a in zip(ids, assignments) if a == c]
        if not members:
            continue
        print(f"\n== {' · '.join(label(centers[c]))}  ({len(members)} tweets, RSS {scores[c]:.2f}) ==")
        for doc_id in members[:limit]:
            doc = docs[doc_id]
            print(f"User: {doc.meta.get('user_handle', '?')}, tweet: {doc.text[:100]}")

def main():
    """Parse arguments, build the indexes and run the interactive query loop."""
    # --- arguments ---
    parser = argparse.ArgumentParser(description="Search the tweet corpus.")
    parser.add_argument("path", help="path to the tweet file")
    parser.add_argument("--limit", type=int, default=10, help="results to show")
    parser.add_argument("--ranked", action="store_true", help="rank results by TF-IDF")
    parser.add_argument("--clusters", type=int, default=0,
                        help="group ranked results into K clusters (0 = off)")
    args = parser.parse_args()

    # The entry point decides whether library log messages are shown.
    logging.basicConfig(level=logging.INFO)

    # --- load and build ---
    # Norms are expensive, so only compute them when ranking or clustering.
    engine = build_engine(args.path, with_norms=bool(args.ranked or args.clusters))
    docs, index = engine.docs, engine.index
    print(f"Number of documents in the corpus: {index.num_docs()}\nNumber of terms: {len(index.dictionary)}")

    # --- query loop ---
    try:
        while True:
            query = input("What's your query hun? ").strip()
            if not query:
                continue
            if query == "quit":
                break

            if args.clusters:
                result = cluster_search(engine, query, args.clusters)
                if not result.ids:
                    print("No results")
                    continue
                print_clusters(result.ids, result.assignments, result.centers,
                               result.rss, docs, args.limit)
            elif args.ranked:
                results = rank(query, index, engine.norms, k=args.limit)
                print_ranked(results, docs)
            else:
                try:
                    ids = search(query, index, engine.permuterm)
                except ValueError as e:  # a bad query prints a message instead of ending the session
                    print(f"Invalid query: {e}")
                    continue
                print_results(ids, docs, args.limit)
    except (KeyboardInterrupt, EOFError):
        print("\nbye")


if __name__ == "__main__":
    main()