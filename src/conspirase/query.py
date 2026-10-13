from conspirase.index import InvertedIndex
from conspirase.tokenize import terms, normalize 
from conspirase.postings import and_not, union, intersect 
from conspirase.permuterm import PermutermIndex

def search(query:str, index: InvertedIndex, permuterm: PermutermIndex | None = None) -> list[int]:
    """Return the matching list with internal id tweets"""
    result = None 
    negate = False 
    op = "AND" #set the operator to AND by default 
    for w in query.split():
        if w == "AND" or w == "OR": #check if word is operator 
            op = w 
            continue #skip the rest of the loop 
        if w == "NOT":
            negate = True #check if word is a negation
            continue

        if "*" in w: #wildcard word 
            if permuterm is None:
                raise ValueError ("Wildcard need a permuterm index")
            pattern = normalize(w)
            matching = permuterm.lookup(pattern)
            w_ids= [] 
            for term in matching:
                w_ids = union(w_ids,index.postings(term).ids())
        else:
            #query words normalization 
            normalized_w = terms(w)
            if not normalized_w:
                continue #check if word was not in stepwords
            w = normalized_w[0] #terms method returns list, so take it's first element: either single element list or "covid-19" -> "covid"
            #get the word doc ids
            w_ids = list(index.postings(w).ids())
    
        if negate: #check if the word prior was negation 
            w_ids = and_not (index.all_doc_ids(), w_ids) #if previos term was a negation we need a list with all docs without the term 

        if result is not None: 
            if op == "AND":
                result = intersect (w_ids,result)
            else:
                result = union (w_ids,result)
        else: #if result is empty then make it the current w_ids list 
            result = w_ids

        op = "AND"
        negate = False 

    return result if result is not None else []
        

