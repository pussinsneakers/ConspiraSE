import pytest
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
