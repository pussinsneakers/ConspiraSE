from conspirase.postings import PostingsList, intersect, union, and_not
import pytest
import random

#---Class methods---
def test_add_and_len():
    p = PostingsList()
    p.add(0,2)
    p.add(5,1)
    assert len(p) == 2
    assert list(p.ids()) == [0,5]

def test_empty_list_len():
    p = PostingsList()
    assert len(p) == 0
 
def test_out_of_order_ids():
    p = PostingsList()
    p.add(2,1)
    with pytest.raises(ValueError):
        p.add(0,3)

def test_duplicate_ids():
    p = PostingsList()
    p.add (3,2)
    with pytest.raises(ValueError):
        p.add(3,4)

def test_iter_yields_pairs():
    p = PostingsList()
    p.add(0,2)
    p.add(5,1)
    assert list(p) == [(0,2), (5,1)]

def test_repr_return_df():
    p = PostingsList()
    p.add(1,3)
    p.add(2,4)
    p.add(5,1)
    assert "df = 3" in repr(p)

#---Merge methods:intersect, union, and_not---
def test_normal_overlap():
    a = [1,3,5,8]
    b = [3,4,8,9]
    assert intersect(a,b) == [3,8]
    assert union(a,b) == [1,3,4,5,8,9]
    assert and_not(a,b) == [1,5]

def test_empty_list():
    a = [] 
    b = [2,3]
    assert intersect(a,b) == []
    assert union(a,b) == [2,3]
    assert and_not(a,b) == []
    assert and_not(b,a) == [2,3] 

def test_both_empty_lists():
    a = [] 
    b = [] 
    assert intersect(a,b) == []
    assert union(a,b) == []
    assert and_not(a,b) == []

def test_identical_lists():
    a = [1,2,3]
    b = [1,2,3]
    assert intersect(a,b) == [1,2,3]
    assert union(a,b) == [1,2,3]
    assert and_not(a,b) == []

def test_disjoint():
    a = [1,3]
    b = [2,4]
    assert intersect(a,b) == []
    assert union(a,b) == [1,2,3,4]
    assert and_not(a,b) == [1,3]


def test_different_length():
    b = [1]
    a = [1,3,5,7,9,10,14,15]
    assert intersect (a,b) == [1]
    assert union (a,b) == [1,3,5,7,9,10,14,15]
    assert and_not (a,b) == [3,5,7,9,10,14,15]

def test_contais_zero():
    a = [0,2]
    b = [0,5]
    assert intersect (a,b) == [0]
    assert union (a,b) == [0,2,5]
    assert and_not (a,b) == [2]

def test_with_postings_list():
    p = PostingsList()
    for doc_id in [0,3,5,8]:
        p.add(doc_id,1)
    q = PostingsList()
    for doc_id in [3,4,8]:
        q.add(doc_id,1)
    assert intersect(p.ids(),q.ids()) == [3,8]
    assert union(p.ids(),q.ids()) == [0,3,4,5,8]
    assert and_not(p.ids(),q.ids()) == [0,5]

def test_merges_match_set_operations():
    rng = random.Random(42)
    for _ in range (500):
        a = sorted (rng.sample(range(50), rng.randint(0,20)))
        b = sorted (rng.sample(range(50), rng.randint(0,20)))
        assert intersect(a,b) == sorted(set(a) & set(b))
        assert union(a,b) == sorted (set(a) | set(b))
        assert and_not(a,b) == sorted (set(a) - set(b))


