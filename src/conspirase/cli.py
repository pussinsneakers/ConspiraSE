"""
An interactive command-line search over a document collection.

Loads the document, builds the inverted index, build the permuterm index, and compute document norms when in rank mode. There are two modes:
Boolean with wildcard and operators (default) and ranked (--ranked), with free-text TF-IDF and operators and wildcards have no effect. 
To end the search type "quit".
"""
import argparse
import logging
from conspirase.corpus import load
from conspirase.index import build_index
from conspirase.query import search 
from conspirase.rank import doc_norms, rank
from conspirase.permuterm import PermutermIndex

def print_results(ids,docs,limit):
    """Prints the result of the search"""
    print (f"The tweets matching the result: {len(ids)}")
    for doc_id in ids[:limit]:
        doc = docs[doc_id]
        print (f"User: {doc.meta['user_handle']}, tweet: {doc.text[:100]}")

def print_ranked(results, docs):
    """Prints the result of the ranked search"""
    print (f"Top {len(results)} results")
    for (doc_id, score) in results:
        doc = docs[doc_id]
        print (f"Score: {score:.3f}, User: {doc.meta['user_handle']}, tweet: {doc.text[:100]}")


def main():
    """Parse document, build the index and run an interactive query loop
    """
    #read the command line 
    parser = argparse.ArgumentParser(description="Search the tweet corpus.")
    parser.add_argument("path", help="path to the tweet file")
    parser.add_argument("--limit", type=int, default=10, help="results to show")
    parser.add_argument("--ranked", action ="store_true", help = "rank results by TF-IDF")
    args = parser.parse_args()
    #args.path and args.limit hold what the user typed

    logging.basicConfig(level=logging.INFO)

    #load and build
    docs = list(load(args.path)) 
    index = build_index(docs)
    permuterm = PermutermIndex(index.dictionary.keys())
    norms = doc_norms(index) if args.ranked else None #only computed in --ranked mode 
    print (f"Number of documents in the corpus: {index.num_docs()}\nNumber of terms: {len(index.dictionary)}")

    #query loop 
    while True:
        query = input("What's your query hun? ").strip()
        if not query:
            continue
        elif query == "quit":
            break
        if args.ranked:
            results = rank (query,index,norms, k = args.limit)
            print_ranked(results,docs)
        else:
            try:
                ids = search(query,index,permuterm)
            except ValueError as e: #bad prompt does not end the session but prints an error message
                print (f"Invalid query: {e}")
                continue
            print_results(ids, docs, args.limit)
            

if __name__== "__main__":
    main()


