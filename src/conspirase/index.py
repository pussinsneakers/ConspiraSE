"""
Build a non-positional inverted index.

Dictionary maps each term to a PostingList sorted by internal document IDs. doc_ids maps internal IDs to original onses, this is needed because
original tweet IDs are very long unordered strings.
Documents go through tokenization and normalization during indexing, so class lookups need normalized term. 
The documents are added from any iterable Document in build_index() method. 

This module do not stores document text, parse queries and does not saved anything on disk (lives in memory only).
"""
from conspirase.tokenize import terms
from conspirase.postings import PostingsList
from collections import Counter
from conspirase.corpus import Document 
from pathlib import Path
from typing import Iterable

class InvertedIndex:
    """In-memory non-positional index over the a collection of documents
    Documents must be added with add_document. IDs are assigned in order.

    dictionary: maps term to PostingList. PostingList contains internal doc ID, tf pairs.
    doc_ids: maps internal ID to tweet IDs. tweet IDs internal ID is its index. 

    Lookups requires normalization, unknown terms return an empty PostingsList.
    """
    def __init__(self):
        self.dictionary: dict[str, PostingsList] = {} #term -> PostingsList
        self.doc_ids: list[str] = [] #Internal ID -> tweet ID, internal ID is the index of the original tweet ID
    
    def add_document (self, tweet_id:str, text:str) -> None:
        """Appends tweet ID to the doc IDs list, with it's index being internal ID.
        Iterates over normalized and tokenized text, maping its terms to PosstingList."""
        internal_id = len(self.doc_ids)
        self.doc_ids.append(tweet_id)
        
        counts = Counter (terms(text))
        for term,tf in counts.items():
            if term not in self.dictionary:
                self.dictionary[term] = PostingsList()
            self.dictionary[term].add(internal_id,tf)
    
    def postings(self, term:str) -> PostingsList:
        """Return postings or empty PostingsList if term is not in the dictionary"""
        return self.dictionary.get(term, PostingsList()) #empty postings list is returned if term does not appear in the dictionary 
    
    def df(self,term:str) -> int:
        """Return df of a term"""
        return len(self.dictionary.get(term, PostingsList()))
    
    def num_docs(self) -> int:
        """Return number of documents in the index"""
        return len(self.doc_ids)
    
    def external_id(self, internal_id:int) -> str:
        """Return external id of a document"""
        return self.doc_ids[internal_id]
    
    def all_doc_ids(self) -> list[int]:
        """Return list of all documents with internal ids"""
        return list(range(len(self.doc_ids))) #shortcut for returning a list which consists of indexes 

def build_index(docs: Iterable[Document]) -> InvertedIndex:
    """Builds the inverted index from the document"""
    new_index = InvertedIndex()
    for doc in docs:
        new_index.add_document(doc.doc_id,doc.text)
    return new_index