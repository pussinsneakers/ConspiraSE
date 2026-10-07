from conspirase.query import search 
from conspirase.index import InvertedIndex 
from conspirase.tokenize import terms
from collections import Counter
import math 
import heapq



def doc_norms(index) -> list[float]:
    """Iterate through the index """
    #create a list, the length is number of dcouments in the corpus, all elements are 0.0 
    norms = [0.0] * index.num_docs()
    #go thorugh the inverted index term by term 
    for term in index.dictionary:
        # print(f"The term is {term}")
        #calculate idf
        idf = math.log10(index.num_docs()/index.df(term))
        #go thorugh the docs & tfs of term 
        for doc_id,tf in index.postings(term):
            #calculate weights
            w = (1 + math.log10(tf)) * idf
            # print (f"Terms appear in doc {doc_id} with the tf of {tf}, term-doc weight is {w}")
            norms[doc_id] += w*w
    return [math.sqrt(x) for x in norms]

def rank(query, index, norms,k=10,candidates=None) -> list[tuple[int,float]]:
    """Returns the top k documents as (internal_id, score)
    candidates: allows to combine boolean search to filter and then ranking to order. 
    """
    counts_q = Counter(terms(query)) #count the terms in query
    scores = {}
    for term,q_tf in counts_q.items():
        if index.df(term) > 0: #compute weights only for terms present in the vocabulary
            q_idf = math.log10(index.num_docs()/index.df(term))
            query_w = (1+math.log10(q_tf)) * q_idf #compute the query weight 
            for doc_id,doc_tf in index.postings(term): #go through all of the docs and tfs of the term
                if candidates is not None and doc_id not in candidates:
                    continue
                doc_w = (1 + math.log10(doc_tf)) * q_idf #calculate the doc weight
                #sum over to avoid overwriting the previous score (for 2 terms match, the multiplication is the nominator of the cosine
                scores[doc_id] = scores.get(doc_id, 0.0) + query_w*doc_w

    for doc_id,score in scores.items(): #go through the scores and devide them by the norm 
        if norms[doc_id] > 0:
            scores[doc_id] = score/norms[doc_id]

    scores = heapq.nlargest(k, scores.items(), key=lambda item: item[1]) 
    return scores