import pytest
from conspirase.query import search 
from conspirase.index import InvertedIndex


@pytest.fixture
def index():
    idx = InvertedIndex()
    idx.add_document("t0", "Malaria vaccine is the best vaccine in the world")
    idx.add_document("t1", "Vaccine causes autism claims")
    idx.add_document("t2", "Autism not that bad")
    idx.add_document("t3", "Impfung gegen Malaria; schützt gegen Malaria")
    idx.add_document("t4", "dinos are cool")
    return idx

def test_single_term(index):
    assert search("autism",index) == [1,2]

def test_and_or_not(index):
    assert search("malaria AND vaccine",index) == [0]
    assert search("impfung OR vaccine",index) == [0,1,3]
    assert search("vaccine AND NOT autism",index) == [0]

def test_leading_not(index):
    assert search("NOT Malaria AND vaccine",index) == [1]

def test_implicit_explicit_and_match(index):
    assert search("dinos AND cool",index) == search("dinos cool",index) == [4]

def test_stopword_in_the_middle(index):
    assert search ("vaccine isn't best",index) == [0] 

def test_capitalized_imlaut_match(index):
    assert search ("schützt",index) == [3]
    assert search ("Vaccine",index) == search ("vaccine",index)

def test_unknown_and_known(index):
    assert search ("adhd AND vaccine",index) == []

def test_left_to_right_order(index):
    assert search ("autism OR dinos AND vaccine",index) == [1]


