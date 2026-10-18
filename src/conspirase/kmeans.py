from conspirase.tokenize import terms
from collections import Counter
import math
import random
import heapq

def doc_vector(text,index) -> dict[str,float]:
    """Turn one text into a normalized TF-IDF vector. If the text consists only of stopword an empty dictionary is returned"""
    counts = Counter(terms(text))
    term_w_dict = {}
    for term,tf in counts.items():
        if index.df(term) > 0: #skip terms with 0 df 
            idf = math.log10(index.num_docs()/index.df(term))
            w = (1+math.log10(tf)) * idf
            term_w_dict[term] = w 
    vector_l = math.sqrt(sum(w*w for w in term_w_dict.values()))

    if vector_l == 0:
        return {}
    
    for term,w in term_w_dict.items():
        term_w_dict[term] = w/vector_l
    
    return term_w_dict 

def sq_distance(a,b) -> float:
    """Calculated squared Euclidean distance between 2 vectors. Missing terms count as 0"""
    d = 0
    for term in (set(a) | set (b)):
        d += (a.get(term,0) - b.get(term,0))**2
    return d

def centroid(vectors) -> dict[str,float]:
    """Returns the average of the given vectors, terms missing from a vector counts as 0"""
    d = {}
    for v in vectors:
        for term,w in v.items():
            d[term] = d.get(term, 0.0) + w
    for centroid_t, centroid_w in d.items():
        d[centroid_t] = centroid_w / len(vectors)
    return d 

def kmeans(
    vectors: list[dict[str, float]],
    k: int,
    seed: int = 0,
    max_iter: int = 20,
) -> tuple[list[int], list[dict[str, float]]]:
    """Cluster sparse vectors into k groups with k-means.

    Starts from k randomly chosen documents as centers, then alternates
    between assigning each vector to its nearest center and moving each
    center to the average of its members, until no assignment changes or
    max_iter rounds have passed.

    Args:
        vectors: document vectors (term -> weight), e.g. from doc_vector.
        k: number of clusters. Reduced to len(vectors) if larger.
        seed: random seed for choosing the starting centers, so results
            are reproducible.
        max_iter: maximum number of assign/update rounds.

    Returns:
        A tuple (assignments, centers): assignments[i] is the cluster number
        of vectors[i], and centers[c] is the center of cluster c.
    """
    if not vectors:
        return [], []
    k = min(k, len(vectors))  # can't pick more distinct starting documents than exist

    # Start with k distinct documents as centers; the seed makes this repeatable.
    start = random.Random(seed).sample(range(len(vectors)), k)
    centers = [vectors[i] for i in start]

    assignments = None  # no previous round yet
    for _ in range(max_iter):
        # Assign: each vector goes to the center with the smallest distance.
        new_assignments = [
            min(range(k), key=lambda c: sq_distance(v, centers[c]))
            for v in vectors
        ]

        # Stop once a round changes nothing. Compare *before* overwriting.
        if new_assignments == assignments:
            break
        assignments = new_assignments

        # Update: move each center to the average of its members.
        for c in range(k):
            members = [v for v, a in zip(vectors, assignments) if a == c]
            if members:  # an empty cluster keeps its old center
                centers[c] = centroid(members)

    return assignments, centers


def rss(
    vectors: list[dict[str, float]],
    assignments: list[int],
    centers: list[dict[str, float]],
) -> list[float]:
    """Return the residual sum of squares (RSS) of each cluster.

    The RSS of a cluster is the sum of squared distances between its member
    vectors and its center. Lower values mean a tighter, more coherent cluster.

    Returns:
        A list where position c holds the RSS of cluster c.
    """
    totals = [0.0] * len(centers)
    for v, c in zip(vectors, assignments):
        totals[c] += sq_distance(v, centers[c])
    return totals


def label(center: dict[str, float], n: int = 3) -> list[str]:
    """Return the n highest-weighted terms of a cluster center, as its label."""
    top = heapq.nlargest(n, center.items(), key=lambda item: item[1])
    return [term for term, _ in top]




