"""
Store term frequency and postings. 
Merge sorted lists of document IDs by intesect, union or and not 
"""
from typing import Iterator, Iterable

class PostingsList:
    """Stores data for one term as two parallel lists"""
    __slots__ = ("doc_ids", "tfs") #memory optimization(for dic of attributes carried by python objects)
    def __init__(self) -> None:
        self.doc_ids: list[int] = [] #sorted internal doc IDs
        self.tfs: list[int] = [] #tfs[i] term frequency in doc_ids[i]

    def add (self,doc_id:int, tf:int) -> None:
        """Append one posting, catching mistakes based on the order of document ids"""
        if self.doc_ids: 
            if doc_id <= self.doc_ids[-1]: 
                raise ValueError (f"doc_id {doc_id} must be greater than last doc_id {self.doc_ids[-1]}")
        self.doc_ids.append(doc_id) #documents are appended in order, so there is no need for sorting
        self.tfs.append(tf)

    def __len__(self) -> int:
        """Return the length of the doc_ids list, essentially df"""
        return len(self.doc_ids)

    def __iter__(self) -> Iterator[tuple[int,int]]:
        """Needed for ranking"""
        yield from zip (self.doc_ids, self.tfs) #yield from gives out one item at a time, not a single item as yield 

    def ids(self) -> Iterator[int]:
        """Needed for the merge functions: union, intersect, and_not"""
        yield from self.doc_ids ##from is needed to return just [lst], without it [list[list]] would be returned

    def __repr__(self) -> str:
        return f"PostingsList (df = {len(self.doc_ids)}, doc_ids = {self.doc_ids})"

def intersect(a:Iterable[int], b:Iterable[int]) -> list[int]:
    """Takes two sorted sequences of doc IDs and returns the IDs they share"""
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
    """Takes sorted sequqnce of doc IDs and return all of the IDs present in both sequence"""
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


