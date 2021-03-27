import random
import genanki
import pandas as pd
import sys

DATA_FILENAME = "results.csv" # Filename of the data file
DECK_FILENAME = "flashcards-pipeline.apkg" # Filename of the Anki deck to generate
ANKI_DECK_TITLE = "flashcards-pipeline-deck-title" # Title of the deck as shown in Anki
ANKI_MODEL_NAME = "flashcards-pipeline-model-name" # Name of the card model
MODEL_ID = 1 # Model ID

style = """
.card {
 font-family: arial;
 font-size: 24px;
 text-align: center;
 color: black;
 background-color: white;
}
.frontside {
 font-size: 12px;
}
"""

def deck_creator():

    anki_model = genanki.Model(MODEL_ID,
                               ANKI_MODEL_NAME,
                               fields=[{"name": "frontside"}, {"name": "backside"}],
                               templates=[{"name": "Card 1",
                                           "qfmt": '<p class="frontside">{{frontside}}</p>',
                                           "afmt": '{{FrontSide}}<hr id="answer"><p class="backside">{{backside}}</p>'},
                                          {"name": "Card 2",
                                           "qfmt": '<p class="backside">{{backside}}</p>',
                                           "afmt": '{{FrontSide}}<hr id="answer"><p class="frontside">{{frontside}}</p>'}],
                               css=style)

    anki_notes = []  # The list of flashcards

    df = pd.read_csv(DATA_FILENAME)

    num_of_rows = len(df)

    for i, row in enumerate(df.values):

        print("Record:", i + 1, "/", num_of_rows)
        print("Question: ", row[2])
        print("Answer:", row[3])

        user_answer = input("Do you want to keep this question? (y/n) \n")

        try:
            assert user_answer in ["y", "n", "s"]
        except AssertionError:
            raise ValueError("Invalid input. Please use y, n or s (yes, no, skip to the end).")

        if user_answer == 'y':
            try:
                anki_note = genanki.Note(model=anki_model,
                                         fields=[row[2], row[3]])
                anki_notes.append(anki_note)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise
        elif user_answer == "s":
            print("Skipping rest of input file")
            break

    random.shuffle(anki_notes)  # Shuffle flashcards

    anki_deck = genanki.Deck(MODEL_ID,
                             ANKI_DECK_TITLE)

    anki_package = genanki.Package(anki_deck)

    # Add flashcards to the deck
    for anki_note in anki_notes:
        anki_deck.add_note(anki_note)

    anki_package.write_to_file(DECK_FILENAME)  # Save the deck to a file

    print("Created deck with {} flashcards".format(len(anki_deck.notes)))

if __name__ == "__main__":
    deck_creator()