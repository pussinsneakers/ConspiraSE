"""
Load the tweets and build the index, prints how mony documents and terms are there 
"""
import argparse
import logging
from conspirase.corpus import load
from conspirase.index import build_index
from conspirase.query import search 

def print_results(ids,docs,limit):
    print (f"The tweets matching the result: {len(ids)}")
    for doc_id in ids[:limit]:
        doc = docs[doc_id]
        print (f"User: {doc.meta['user_handle']}, tweet: {doc.text[:100]}")

def main():
    """
    Read the command line
    """
    #read the command line 
    parser = argparse.ArgumentParser(description="Search the tweet corpus.")
    parser.add_argument("path", help="path to the tweet file")
    parser.add_argument("--limit", type=int, default=10, help="results to show")
    args = parser.parse_args()
    #args.path and args.limit hold what the user typed

    logging.basicConfig(level=logging.INFO)

    #load and build
    docs = list(load(args.path))
    index = build_index(docs)
    print (f"Number of documents in the corpus{index.num_docs()}.\n Number of terms {len(index.dictionary)}")

    while True:
        query = input("What's your query hun? ").strip()
        if not query:
            continue
        elif query == "quit":
            break
        ids = search(query,index)
        print_results(ids, docs, args.limit)

if __name__== "__main__":
    main()


