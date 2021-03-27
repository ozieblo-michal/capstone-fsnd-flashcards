import stanza
import pandas as pd

def suggest_gaps(parsed_text: stanza.Document, original_text: str) -> pd.DataFrame:

    """
    Cut out given parts of speech (entities/gaps) from the sentence.
    :param parsed_text: stanza Document based on original_text
    :param original_text: single sentence
    :return: dataframe with the sentence, the related gap question and the answer
    """

    entities = ["NN", "NNP"]
    gaps = []

    try:
        for word in parsed_text.iter_tokens():
            # xpos [str] The treebank-specific part-of-speech of this word. Example: ‘NNP’.
            if word.to_dict()[0]["xpos"] in entities:
                gap = original_text[word.start_char : word.end_char]
                question = original_text.replace(gap, "_____")
                gaps.append({"Sentence": original_text,
                             "Question": question,
                             "Answer": gap})
    except EnvironmentError:
        print("Error during gap creation. Please check the console.")

    return pd.DataFrame(gaps)