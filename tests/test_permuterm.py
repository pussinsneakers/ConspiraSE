from conspirase.permuterm import PermutermIndex
import pytest

@pytest.fixture 
def p():
    return PermutermIndex(["grippeimpfung", "impfstoff", "impfung",
                           "malaria", "vaccine", "banana"])

def test_rotations_correct():
    perm = PermutermIndex(["ab"]) 
    assert perm.rotations == ["$ab", "ab$", "b$a"]
    assert perm.terms == ["ab", "ab", "ab"]

def test_prefix(p):
    assert p.lookup("impf*") == ["impfstoff", "impfung"]

def test_suffix(p):
    assert p.lookup ("*ung") == ["grippeimpfung", "impfung"]

def test_middle(p):
    assert p.lookup("ma*ia") == ["malaria"]

def test_contains(p):
    assert p.lookup("*cin*") == ["vaccine"]

def test_exact_match(p):
    assert p.lookup ("banana") == ["banana"]

def test_no_partial_exact_match(p):
    assert p.lookup("banan") == []

def test_no_duplicates(p):
    assert p.lookup("*an*") == ["banana"]

def test_several_matches(p):
    assert p.lookup("*a*") == ["banana","malaria","vaccine"]

def test_no_match(p):
    assert p.lookup("*xyz") == []

def test_unsupported_pattern(p):
    with pytest.raises(ValueError):
        p.lookup("x*y*z*")

def test_only_star(p):
    with pytest.raises(ValueError):
        p.lookup("*")