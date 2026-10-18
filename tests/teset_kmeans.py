import math

import pytest

from conspirase.kmeans import doc_vector, sq_distance, centroid, kmeans, rss, label
from conspirase.index import InvertedIndex


# --- doc_vector ---

def test_doc_vector_has_unit_length(index):
    v = doc_vector("Vaccine causes autism claims", index)
    length = math.sqrt(sum(w * w for w in v.values()))
    assert length == pytest.approx(1.0)


def test_doc_vector_contains_only_document_terms(index):
    v = doc_vector("Autism not that bad", index)
    assert set(v) == {"autism", "bad"}


def test_doc_vector_rarer_term_gets_higher_weight(index):
    # "bad" appears in 1 document, "autism" in 2, so "bad" has the higher idf
    v = doc_vector("Autism not that bad", index)
    assert v["bad"] > v["autism"]


def test_doc_vector_stopwords_only_is_empty(index):
    assert doc_vector("the and is", index) == {}


def test_doc_vector_unknown_terms_are_skipped(index):
    assert doc_vector("zebra giraffe", index) == {}


def test_doc_vector_zero_idf_is_empty():
    # with a single document, every term has idf log10(1/1) = 0
    idx = InvertedIndex()
    idx.add_document("t0", "malaria vaccine")
    assert doc_vector("malaria vaccine", idx) == {}


# --- sq_distance ---

def test_sq_distance_disjoint_vectors():
    assert sq_distance({"a": 1.0}, {"b": 1.0}) == pytest.approx(2.0)


def test_sq_distance_identical_vectors_is_zero():
    v = {"a": 0.6, "b": 0.8}
    assert sq_distance(v, v) == 0


def test_sq_distance_is_symmetric():
    a = {"malaria": 0.8, "vaccine": 0.6}
    b = {"vaccine": 0.6, "autism": 0.8}
    assert sq_distance(a, b) == pytest.approx(sq_distance(b, a))
    assert sq_distance(a, b) == pytest.approx(1.28)


# --- centroid ---

def test_centroid_averages_over_all_vectors():
    c = centroid([{"a": 1.0}, {"b": 1.0}])
    assert c == pytest.approx({"a": 0.5, "b": 0.5})


def test_centroid_missing_terms_count_as_zero():
    c = centroid([{"malaria": 0.8, "vaccine": 0.6}, {"malaria": 0.6, "autism": 0.8}])
    assert c == pytest.approx({"malaria": 0.7, "vaccine": 0.3, "autism": 0.4})


def test_centroid_of_one_vector_is_itself():
    assert centroid([{"a": 0.6, "b": 0.8}]) == pytest.approx({"a": 0.6, "b": 0.8})


# --- kmeans ---

AB_VECTORS = [{"a": 1.0}, {"a": 1.0}, {"b": 1.0}, {"b": 1.0}]


def test_kmeans_separates_obvious_groups():
    assignments, centers = kmeans(AB_VECTORS, 2)
    # cluster numbers are arbitrary, so check which documents share a cluster
    assert assignments[0] == assignments[1]
    assert assignments[2] == assignments[3]
    assert assignments[0] != assignments[2]
    assert len(centers) == 2


def test_kmeans_separates_groups_for_any_seed():
    for seed in range(10):
        assignments, _ = kmeans(AB_VECTORS, 2, seed=seed)
        assert assignments[0] == assignments[1] != assignments[2] == assignments[3]


def test_kmeans_is_reproducible_with_same_seed():
    vectors = [{"a": 1.0}, {"a": 0.6, "c": 0.8}, {"b": 1.0}, {"c": 1.0}, {"b": 0.8, "c": 0.6}]
    assert kmeans(vectors, 2, seed=7) == kmeans(vectors, 2, seed=7)


def test_kmeans_one_assignment_per_vector():
    assignments, _ = kmeans(AB_VECTORS, 2)
    assert len(assignments) == len(AB_VECTORS)
    assert all(0 <= a < 2 for a in assignments)


def test_kmeans_reduces_k_when_too_large():
    assignments, centers = kmeans(AB_VECTORS[:3], 10)
    assert len(centers) == 3
    assert len(assignments) == 3


def test_kmeans_empty_input():
    assert kmeans([], 3) == ([], [])


# --- rss ---

def test_rss_perfect_clusters_is_zero():
    assignments, centers = kmeans(AB_VECTORS, 2)
    assert rss(AB_VECTORS, assignments, centers) == pytest.approx([0.0, 0.0])


def test_rss_one_value_per_cluster():
    assignments, centers = kmeans(AB_VECTORS, 2)
    assert len(rss(AB_VECTORS, assignments, centers)) == len(centers)


def test_rss_hand_computed_value():
    vectors = [{"a": 1.0}, {"b": 1.0}]
    center = {"a": 0.5, "b": 0.5}
    # each vector is at squared distance 0.5 from the center
    assert rss(vectors, [0, 0], [center]) == pytest.approx([1.0])


# --- label ---

def test_label_picks_highest_weights():
    assert label({"a": 0.9, "b": 0.1, "c": 0.5}, n=2) == ["a", "c"]


def test_label_with_fewer_terms_than_n():
    assert label({"x": 1.0}, n=3) == ["x"]


def test_label_empty_center():
    assert label({}) == []