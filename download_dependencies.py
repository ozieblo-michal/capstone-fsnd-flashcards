import stanza

try:
    stanza.download('en', processors="tokenize,lemma,pos,depparse")
except AssertionError:
    pass