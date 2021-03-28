import stanza

try:
    stanza.download('en', processors="tokenize,lemma,pos,depparse")
except AssertionError:
    pass

nlp = stanza.Pipeline("en", processors="tokenize,lemma,pos,depparse")

def parse_sentence(input_text: str, nlp) -> stanza.Document:

    """
    Parse sentence into an intermediate representation.
    :param input_text: an element/sentence from the list
    :param language: of the given sentence
    :return:
    """

    try:
        # nlp = stanza.Pipeline(language, processors="tokenize,lemma,pos,depparse")
        return nlp(input_text)
    except:
        try:
            stanza.download(language)
            nlp = stanza.Pipeline(language, processors="tokenize,lemma,pos,depparse")
            return nlp(input_text)
        except:
            print("Unknown error. Please read the console output.")