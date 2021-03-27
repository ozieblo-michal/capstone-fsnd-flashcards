from flask_wtf import FlaskForm
import wtforms
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from .models import Decks

#----------------------------------------------------------------------------#
# Forms.
#----------------------------------------------------------------------------#

#### https://wtforms.readthedocs.io/en/2.3.x/fields/
class CreateQuestions(FlaskForm):
    note = wtforms.TextAreaField('Copy below your note:', validators=[DataRequired()])
    deck_name = wtforms.StringField('Put the deck name:', validators=[DataRequired()])

class SubmitNote(FlaskForm):
    submit = wtforms.SubmitField()

def dropdown_query():
    return Decks.query.order_by(Decks.id.desc())

#### https://stackoverflow.com/questions/33832940/flask-how-to-populate-select-field-in-wtf-form-when-database-files-is-separate
class SelectDeck(FlaskForm):
    pick_the_deck = QuerySelectField(query_factory=dropdown_query,
                                     label="Decks:",
                                     #allow_blank=True,
                                     #blank_text="Select the deck",
                                     id="removedeck" )

#### https://stackoverflow.com/questions/49037015/is-posible-to-render-wtf-form-field-with-out-label
class NoLabelMixin(object):
    def __init__(self, *args, **kwargs):
        super(NoLabelMixin, self).__init__(*args, **kwargs)
        for field_name in self._fields:
            field_property = getattr(self, field_name)
            field_property.label = ""

#### https://dev.to/sampart/combining-multiple-forms-in-flask-wtforms-but-validating-independently-cbm
class MainForm(FlaskForm):
    create_questions = wtforms.FormField(CreateQuestions)
    submit_note = wtforms.FormField(SubmitNote)

class MainFormNoLabel(NoLabelMixin, MainForm):
    pass
