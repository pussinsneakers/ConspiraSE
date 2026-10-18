"""
Create postings list. 

Creates posting list by adding term's doc ID and frequency. Stores the data in corresponding parallel lists.  
Merges sorted sequences of doc IDs by intesect, union or and not. 
"""
from typing import Iterator, Iterable

class PostingsList:
    """Postings List for a single term, the documents containing the term with term frequences are sorted by document IDs in parallel lists.
    
    doc_ids: internal document IDs in ascending order
    tfs: term frequencies in docuemnts, tfs[i] belongs to doc_ids[i]
    
    Addition of documents happens in increasing order, everything else raises an error. Iterating gives (doc_ids, tfs) pairs, 
    ids() gives just IDs, len() returns the number of documents in doc_ids list - df. 
    
    PostingsList does not hold the term itself, the term is held in inverted index."""
    __slots__ = ("doc_ids", "tfs") #memory optimization(for dic of attributes carried by python objects)
    def __init__(self) -> None:
        self.doc_ids: list[int] = [] #sorted internal doc IDs
        self.tfs: list[int] = [] #tfs[i] term frequency in doc_ids[i]

    def add (self,doc_id:int, tf:int) -> None:
        """Adds one posting. Since documents are appended in the ascending order, everything else raises an error."""
        if self.doc_ids: 
            if doc_id <= self.doc_ids[-1]: 
                raise ValueError (f"doc_id {doc_id} must be greater than last doc_id {self.doc_ids[-1]}")
        self.doc_ids.append(doc_id) #documents are appended in order, so there is no need for sorting
        self.tfs.append(tf)

    def __len__(self) -> int:
        """Return the length of the doc_ids list, essentially df"""
        return len(self.doc_ids)

    def __iter__(self) -> Iterator[tuple[int,int]]:
        """Yields doc_id, tf pairs. Enables the iteration, needed for ranking"""
        yield from zip (self.doc_ids, self.tfs) #yield from gives out one item at a time, not a single item as yield 

    def ids(self) -> Iterator[int]:
        """Yields doc_id list. Needed for the merge functions: union, intersect, and_not"""
        yield from self.doc_ids #from is needed to return just [lst], without it [list[list]] would be returned

    def __repr__(self) -> str:
        """Returns infromation about number of documents in the list and their ids"""
        return f"PostingsList (df = {len(self.doc_ids)}, doc_ids = {self.doc_ids})"

def intersect(a:Iterable[int], b:Iterable[int]) -> list[int]:
    """Returns the IDs shared in both 'a' and 'b'.
    Both inputs must be sorted in ascending order. The result is sorted as well"""
    a = iter(a)
    b = iter(b)
    x = next (a, None) #first element of a
    y = next (b, None) #first element of b
    result = []
    while x is not None and y is not None:
        if x == y:
            result.append(x)
            x = next (a, None) # advance elements in both sequences
            y = next (b, None)
        elif x < y:
            x = next(a, None) #if one a's id is smaller than the b's, it means a is 'behind', so move to the next element in a
        else:
            y = next(b, None) #a id is bigger, b is behind, move to the next elememnt in b
    return result

def union (a:Iterable[int], b:Iterable[int]) -> list[int]:
    """Returns the combination of IDs in 'a' and 'b'.
    Both inputs must be sorted in ascending order. The result is sorted as well"""
    a = iter(a)
    b = iter(b)
    x = next (a, None) 
    y = next (b, None) 
    result = []
    while x is not None and y is not None:
        if x == y: 
            result.append(x)
            x = next (a, None) 
            y = next (b, None) 
        elif x < y:
            result.append(x)
            x = next(a, None)
        else:
            result.append(y)
            y = next(b, None)
    # the loop above always adds the eleement which is smaller. If the last element in the list is bigger, it's never added 
    # append any values that are still left when the main loop ends 
    while x is not None:
        result.append (x)
        x = next(a, None)

    while y is not None:
        result.append(y)
        y = next(b, None)
    return result

def and_not (a:Iterable[int], b:Iterable[int]) -> list[int]:
    """Returns the IDs in 'a' that are not in 'b' (a AND NOT b).
    Both inputs must be sorted in ascending order. The result is sorted as well"""
    a = iter(a)
    b = iter(b)
    x = next (a, None) 
    y = next (b, None) 
    result = []
    while x is not None and y is not None:
        if x == y:
            x = next (a, None)
            y = next (b, None)
        elif x < y:
            result.append(x)
            x = next(a, None) 
        else:
            y = next(b,None) 
    # similar to union, pick last values in a which is bigger than last value in b
    while x is not None:
        result.append (x)
        x = next(a, None)
    return result


