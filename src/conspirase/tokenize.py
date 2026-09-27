"""
Turning raw text into terms
"""

from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True,slots=True)
class TokenizerConfig:
    """Normalization settings"""
    drop_urls:bool = True
    drop_mentions:bool = True 
    min_length: int = 1 

DEFAULT_CONFIG = TokenizerConfig()

# setting up constants 
_UMLAUT_TABLE = str.maketrans({
    "ä": "ae",
    "ö":"oe",
    "ü":"ue"
})

# list of stopwords is taken from NLTK library
STOPWORDS_EN = {"i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", 
    "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", 
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", 
    "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", 
    "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", 
    "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", 
    "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", 
    "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", 
    "very", "can", "will", "just", "don't", "should", "now", "it's", "isn't", "doesn't", "aren't", "I'm", "he's", "she's", "we're", "they're",
    "it's","what's"}

STOPWORDS_DE = {"aber", "alle", "allem", "allen", "aller", "alles", "als", "also", "am", "an",
    "ander", "andere", "anderem", "anderen", "anderer", "anderes", "anderm", "andern", "anderr", "anders",
    "auch", "auf", "aus", "bei", "bin", "bis", "bist", "da", "damit", "dann",
    "der", "den", "des", "dem", "die", "das", "dass", "daß", "derselbe", "derselben",
    "denselben", "desselben", "demselben", "dieselbe", "dieselben", "dasselbe", "dazu", "dein", "deine", "deinem",
    "deinen", "deiner", "deines", "denn", "derer", "dessen", "dich", "dir", "du", "dies",
    "diese", "diesem", "diesen", "dieser", "dieses", "doch", "dort", "durch", "ein", "eine",
    "einem", "einen", "einer", "eines", "einig", "einige", "einigem", "einigen", "einiger", "einiges",
    "einmal", "er", "ihn", "ihm", "es", "etwas", "euer", "eure", "eurem", "euren",
    "eurer", "eures", "für", "gegen", "gewesen", "hab", "habe", "haben", "hat", "hatte",
    "hatten", "hier", "hin", "hinter", "ich", "mich", "mir", "ihr", "ihre", "ihrem",
    "ihren", "ihrer", "ihres", "euch", "im", "in", "indem", "ins", "ist", "jede",
    "jedem", "jeden", "jeder", "jedes", "jene", "jenem", "jenen", "jener", "jenes", "jetzt",
    "kann", "kein", "keine", "keinem", "keinen", "keiner", "keines", "können", "könnte", "machen",
    "man", "manche", "manchem", "manchen", "mancher", "manches", "mein", "meine", "meinem", "meinen",
    "meiner", "meines", "mit", "muss", "musste", "nach", "nicht", "nichts", "noch", "nun",
    "nur", "ob", "oder", "ohne", "sehr", "sein", "seine", "seinem", "seinen", "seiner",
    "seines", "selbst", "sich", "sie", "ihnen", "sind", "so", "solche", "solchem", "solchen",
    "solcher", "solches", "soll", "sollte", "sondern", "sonst", "über", "um", "und", "uns",
    "unsere", "unserem", "unseren", "unser", "unseres", "unter", "viel", "vom", "von", "vor",
    "während", "war", "waren", "warst", "was", "weg", "weil", "weiter", "welche", "welchem",
    "welchen", "welcher", "welches", "wenn", "werde", "werden", "wie", "wieder", "will", "wir",
    "wird", "wirst", "wo", "wollen", "wollte", "würde", "würden", "zu", "zum", "zur",
    "zwar", "zwischen"}

STOPWORDS = STOPWORDS_EN | STOPWORDS_DE #forming a union for 2 sets 

_APOSTROPHES = {"'", "’", "´", "`"}

def tokenize (text: str) -> list[str]:
    """Walking through the text one character at a time. Words with apostrophes are kept intact"""
    current = []
    tokens = []
    for ind,char in enumerate(text):
        if char.isalnum(): 
            current.append(char) #keep the chars that are alphabetic and numberic
        elif (char in _APOSTROPHES 
              and current
              and ind+1 < len(text)
              and text[ind+1].isalnum()): #chech if current is not empty and num or alphabetic char follows it 
            current.append("'") #keep the apostroph but get rid of apostrophe variants 
        else:
            if current:
                tokens.append("".join(current)) #join the chars together into token, but only if current is not empty string
                current=[]
    if current:            
        tokens.append("".join(current)) #join the last token in the text, but only if current is not empty
    return tokens


def _strip_noise (text:str, config: TokenizerConfig) -> str:
    """ Remove URLs and mentions"""
    stripped_text = []
    for word in text.split(): 
        if config.drop_urls and ("http://" in word or "https://" in word or word.startswith("www.")):
            continue
        if config.drop_mentions and word.startswith("@"):
            continue
        stripped_text.append(word) 
    return " ".join(stripped_text)


def normalize (token:str) -> str:
    """Mapping different spelling of the same word to one form"""
    token = token.casefold() #stronger version of lowercasing, making ẞ - ss
    return token.translate(_UMLAUT_TABLE) 
    
# since stopwords removal happens after token normalization, stopwords need to be normalized too
_STOPWORDS_NORMALIZED = frozenset (normalize(w) for w in STOPWORDS)

def terms (text: str, config: TokenizerConfig = DEFAULT_CONFIG) -> list[str]:
    final_l = []
    no_url_text=_strip_noise(text,config)
    tokenized_text = tokenize(no_url_text)
    for token in tokenized_text:
        normalized_token= normalize(token)
        if normalized_token in _STOPWORDS_NORMALIZED:
            continue
        if len(normalized_token) < config.min_length:
            continue
        final_l.append(normalized_token)
    return final_l


