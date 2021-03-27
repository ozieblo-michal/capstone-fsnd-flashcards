def text_area_field_handler(text_area_field) -> list:
    """
    Read source TextAreaField and prepare it for the future wrangling.
    It gives a list of single sentences.
    """

    try:
        raw_sentences = text_area_field.strip().split(".")
        sentences_list = list((i for i in raw_sentences if ("#" not in i) and i))
        return sentences_list

    except:
        print("Error in text_area_field_handler()")
        abort(500)