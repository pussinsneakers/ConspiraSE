"""
Assign internal document IDs because tweet IDs are very long unordered strings.
Build a dictionary: for each tweet run terms() and count how often each word occurs and add a posting for each word 
"""
from conspirase.tokenize import terms
from conspirase.postings import PostingsList
from collections import Counter
from conspirase.corpus import Document 
from pathlib import Path
from typing import Iterable

class InvertedIndex:
    def __init__(self):
        self.dictionary: dict[str, PostingsList] = {} #term -> PostingsList
        self.doc_ids: list[str] = [] #Internal id -> tweet_id
    
    def add_document (self, tweet_id:str, text:str) -> None:
        """Appends tweet_id to the doc_ids list with it's position(index) as it's internal id. 
        Gives the tweet it's internal ID and add key value data to the dictionary {term:(PostingsList)}. *PostingsList objects are("doc_ids", "tfs")"""
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
        return len(self.dictionary.get(term, PostingsList()))
    
    def num_docs(self) -> int:
        """Number of documents in the index"""
        return len(self.doc_ids)
    
    def external_id(self, internal_id:int) -> str:
        return self.doc_ids[internal_id]
    
    def all_doc_ids(self) -> list[int]:
        """List of all documents with internal ids"""
        return list(range(len(self.doc_ids))) #shortcut for returning a list which consists of indexes 

def build_index(docs: Iterable[Document]) -> InvertedIndex:
    """Building the inverted index"""
    new_index = InvertedIndex()
    for doc in docs:
        new_index.add_document(doc.doc_id,doc.text)
    return new_index