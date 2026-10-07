import pytest
from conspirase.rank import rank, doc_norms
from conspirase.index import InvertedIndex

#---Norms---
@pytest.fixture
def norms(index):
    return doc_norms(index)

def test_doc_norms(norms):
    assert norms[2] == pytest.approx(0.804, abs=0.001)

def test_one_norm_per_document(index,norms):
    assert len(norms) == index.num_docs()

def test_stopwords_doc_norms():
    index = InvertedIndex()
    index.add_document("t5", "is and are")
    norms = doc_norms(index)
    assert norms[0] == 0 

#---Ranks---
def test_order_rank(index,norms):
    rank_order = rank("vaccine autism", index, norms)
    ids_l = [doc_id for doc_id,_ in rank_order]
    assert ids_l == [1,2,0]

def test_not_mathcing_docs_excluded(index,norms):
    rank_order = rank("vaccine autism", index, norms)
    ids_l = [doc_id for doc_id,_ in rank_order]
    assert 3 not in ids_l
    assert 4 not in ids_l

def test_descending_scores(index,norms):
    rank_order = rank("vaccine autism", index, norms)
    scores_l = [score for _,score in rank_order]
    for i in range(len(scores_l)-1):
        assert scores_l[i] >= scores_l[i+1] 

def test_k_limits(index,norms):
    rank_order = rank("vaccine autism", index, norms,k=1)
    assert len(rank_order) == 1 

def test_candidates(index,norms):
    rank_order = rank("vaccine autism", index, norms, candidates={0,2})
    ids_l = [doc_id for doc_id,_ in rank_order]
    assert ids_l == [2,0]

def test_unknown_query_term(index,norms):
    rank_order = rank("soup", index, norms)
    assert rank_order == []

def test_stopword_query(index,norms):
    rank_order = rank("are and", index, norms)
    assert rank_order == []









