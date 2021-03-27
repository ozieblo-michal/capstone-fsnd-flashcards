from suggest_gaps import suggest_gaps
from parse_sentence import parse_sentence
import pandas as pd

#OUTPUT_FILE_NAME = "results.csv" #TODO# connect to the database

def stanza_wrapper(sentences_list) -> pd.DataFrame:

    """
    Create .csv file with gap questions related to source text from TextAreaField
    """

    output = pd.DataFrame(data = None,
                          columns=("Sentence","Question"))

    n_sentences = len(sentences_list)

    try:
        for n, sentence in enumerate(sentences_list):
            parsed_text = parse_sentence(sentence)
            new_record = suggest_gaps(parsed_text,
                                      sentence)
            print(f"Processed sentence {n+1} of {n_sentences}: ",
                  sentence)
            output = pd.concat([output, new_record])
    except EnvironmentError:
        print("Error in main file. Please check the console output.")

    n_questions = len(output)

    print("-" * 80)
    print(f"{n_questions} gap questions have been created based on {n_sentences} sentences.")

    #try:
    #    output.to_csv(OUTPUT_FILE_NAME)
    #    print("Please review the output csv file.")
    #except:
    #    "Error: Cannot create output file. Please check the console."

    return output

if __name__ == "__main__":
    stanza_wrapper()