from conspirase.index import InvertedIndex, build_index
from conspirase.corpus import load

#---Class methods---
def test_term_in_two_documents_postings():
    index = InvertedIndex()
    index.add_document("1500001", "Vaccines!!")
    index.add_document("1500002", "Malaria")
    index.add_document("1499873", "Vaccines")
    assert list(index.postings("vaccines").ids())  == [0,2]
    assert index.df("vaccines") == 2 

def test_repeated_term_tf():
    index = InvertedIndex()
    index.add_document("1500001", "Vaccines, vaccines everywhere!!")
    assert list (index.postings("vaccines")) == [(0,2)]

def test_absent_term_empty_postings():
    index = InvertedIndex()
    assert list(index.postings("autism")) == []
    assert index.df("autism") == 0

def test_external_id_transformation():
    index = InvertedIndex()
    index.add_document("1500001", "Vaccines!!")
    index.add_document("1499873", "Vaccines")
    assert index.external_id(0) == "1500001"
    assert index.external_id(1) == "1499873"

def test_stop_word_document():
    index = InvertedIndex()
    index.add_document("1500001", "and!!")
    assert index.dictionary == {}
    assert index.num_docs() == 1 
    assert 0 in index.all_doc_ids()

def test_normalization():
    index = InvertedIndex()
    index.add_document("1500001", "übersetzen Vaccines!!")
    assert "uebersetzen" in index.dictionary.keys()
    assert "vaccines" in index.dictionary.keys()

def test_unknown_term_do_not_modify_index():
    index = InvertedIndex()
    index.postings("autism")
    assert "autism" not in index.dictionary.keys()

#---Build function--
def test_build_index_from_file(tmp_path): #temporary folder for test
    path = tmp_path / "tweets.csv"
    path.write_text(
        "2018-02-20 00:48:59 +0100\t1\t@a\tA\tVaccines work\n"
        "2018-02-20 00:49:00 +0100\t2\t@b\tB\tMalaria vaccines\n",
        encoding="utf-8",
    )
    index = build_index(load(path))
    assert index.num_docs() == 2
    assert index.df("vaccines") == 2




