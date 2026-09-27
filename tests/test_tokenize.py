from conspirase.tokenize import tokenize, normalize, terms, TokenizerConfig

#---tokenize---
def test_tokenize_splits_on_punctuation():
    assert tokenize ("Hi, nice weather, isn't it") == ["Hi", "nice", "weather", "isn't", "it"]

def test_tokenize_empty_string():
    assert tokenize ("") == []

def test_tokenize_unifies_apostrophs_variants():
    assert tokenize ("what`s") == ["what's"]

def test_tokenize_trailing_apostrophe_dropped():
    assert tokenize ("hello'") == ["hello"]


#---normalize---
def test_normalize_casefold_sharp_s():
    assert normalize ("Straße") == "strasse"

def test_normalize_translate_umlauts():
    assert normalize ("Übung") == "uebung"

#---terms(full pipeline)---
def test_terms_real_tweet():
    text = "@FischerKurt Lady, what´s a tumor? #KippCharts"
    assert terms (text) == ["lady", "tumor", "kippcharts"]

def test_terms_german_stopwords_with_umlauts():
    assert terms("Das ist für die Übergewicht-Studie") == ["uebergewicht", "studie"]

def test_terms_drops_urls():
    assert terms("see https://t.co/abc") == ["see"]

def test_terms_keeps_mentions_when_configured():
    config = TokenizerConfig(drop_mentions=False)
    assert terms("@FischerKurt Lady", config) == ["fischerkurt", "lady"]

def test_terms_min_length():
    config = TokenizerConfig(min_length=3)
    assert terms("go to Japan", config) == ["japan"]