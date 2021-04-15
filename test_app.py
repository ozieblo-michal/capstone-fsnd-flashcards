import os
from dotenv import load_dotenv
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import (setup_db, create_app)
from models import (Decks, Questions)

load_dotenv()

# it may be needed to log in to the app again if the token will expire
TOKEN_1 = os.environ.get('TOKEN_1')
TOKEN_2 = os.environ.get('TOKEN_2')

TOKEN_1 = f"Bearer {TOKEN_1}"
TOKEN_2 = f"Bearer {TOKEN_2}"

SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')

class CapstoneTestCase(unittest.TestCase):

    """
    This class represents the Capstone test cases.
    Includes:
     at least one test for expected success and error behavior for each endpoint;
     tests demonstrating role-based access control
    """

    def setUp(self):

        """Define test variables and initialize app."""

        self.app = create_app()
        self.client = self.app.test_client
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
        self.app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        self.app.config['SECRET_KEY'] = os.urandom(32)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.app = self.app
            self.db.init_app(self.app)
        pass

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_success_show_questions(self):

        """ a positive scenario for a simple reading of data from the backend """

        response = self.client().get('/')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['n_questions'], 11)
        self.assertTrue(data['questions'], True)

    def test_success_token_add_questions(self):

        """
        a positive scenario for adding data to the database (with the intention of connecting the endpoint
        to the batch from the form in subsequent versions of the application)
        """

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_2}
        response = self.client().post('/questions',
                                      headers=jwt,
                                      data=json.dumps(dict(sentence = 'TEST SENTENCE ADD QUESTION',
                                                           question = 'TEST QUESTION ADD QUESTION',
                                                           answer = 'TEST ANSWER ADD QUESTION',
                                                           username = 'TESTUSERNAMEADDQUESTION',
                                                           deck_name = 'TESTDECKNAMEADDQUESTION')))
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['message'], 'Question successfully created!')

    def test_error_no_token_add_questions(self):

        """ error behavior due to lack of token """

        jwt = {'Content-Type': 'application/json'}
        response = self.client().post('/questions',
                                      headers=jwt,
                                      data=json.dumps(dict(sentence='TEST SENTENCE ADD QUESTION',
                                                           question='TEST QUESTION ADD QUESTION',
                                                           answer='TEST ANSWER ADD QUESTION',
                                                           username='TESTUSERNAMEADDQUESTION',
                                                           deck_name='TESTDECKNAMEADDQUESTION')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertTrue(data['error'])
        self.assertEqual(data['success'], False)

    def test_error_insert_add_questions(self):

        """ error behavior due to lack of username (every insert parameter must be filled) """

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_1}
        response = self.client().post('/questions',
                                      headers=jwt,
                                      data=json.dumps(dict(sentence='TEST SENTENCE ADD QUESTION',
                                                           question='TEST QUESTION ADD QUESTION',
                                                           answer='TEST ANSWER ADD QUESTION',
                                                           username='',
                                                           deck_name='TESTDECKNAMEADDQUESTION')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    def test_success_update_question(self):

        """ a positive scenario for the modification of the question in the database """

        last_question = Questions.query.order_by(Questions.id.desc()).first()
        last_question_id = last_question.id

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_1}
        response = self.client().post('/updatequestion',
                                      headers=jwt,
                                      data=json.dumps(dict(oldquestionid=last_question_id,
                                                           newquestion='UPDATED QUESTION TEST')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully modified!')

    def test_error_insert_update_question(self):

        """ error behavior due to lack of new question string """

        last_question = Questions.query.order_by(Questions.id.desc()).first()
        last_question_id = last_question.id

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_1}
        response = self.client().post('/updatequestion',
                                      headers=jwt,
                                      data=json.dumps(dict(oldquestionid=last_question_id,
                                                           newquestion='')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)

    def test_success_update_sentence(self):

        """ a positive scenario for the modification of the sentence in the database """

        last_question = Questions.query.order_by(Questions.id.desc()).first()
        last_question_id = last_question.id

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_1}
        response = self.client().post('/updatesentence',
                                      headers=jwt,
                                      data=json.dumps(dict(oldsentenceid=last_question_id,
                                                           newsentence='UPDATED SENTENCE TEST')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Sentence successfully modified!')

    def test_error_update_sentence(self):

        """ error behavior due to lack of new sentence string """

        last_question = Questions.query.order_by(Questions.id.desc()).first()
        last_question_id = last_question.id

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_1}
        response = self.client().post('/updatesentence',
                                      headers=jwt,
                                      data=json.dumps(dict(oldsentenceid=last_question_id,
                                                           newsentence='')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)

    def test_success_update_answer(self):

        """ a positive scenario for the modification of the answer in the database """

        last_question = Questions.query.order_by(Questions.id.desc()).first()
        last_question_id = last_question.id
        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_1}
        response = self.client().post('/updateanswer',
                                      headers=jwt,
                                      data=json.dumps(dict(oldanswerid=last_question_id,
                                                           newanswer='UPDATED ANSWER TEST')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Answer successfully modified!')

    def test_error_insert_update_answer(self):

        """ error behavior due to lack of new answer string """

        last_question = Questions.query.order_by(Questions.id.desc()).first()
        last_question_id = last_question.id
        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_1}
        response = self.client().post('/updateanswer',
                                      headers=jwt,
                                      data=json.dumps(dict(oldanswerid=last_question_id,
                                                           newanswer='')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)

    def test_error_no_token_update_answer(self):

        """ error behavior due to lack of token """

        last_question = Questions.query.order_by(Questions.id.desc()).first()
        last_question_id = last_question.id
        response = self.client().post('/updateanswer',
                                      data=json.dumps(dict(oldanswerid=last_question_id,
                                                           newanswer='')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertTrue(data['error'])
        self.assertEqual(data['success'], False)

    def test_error_permission_update_answer(self):

        """ error behavior due to lack of permission """

        last_question = Questions.query.order_by(Questions.id.desc()).first()
        last_question_id = last_question.id
        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_2}
        response = self.client().post('/updateanswer',
                                      headers=jwt,
                                      data=json.dumps(dict(oldanswerid=last_question_id,
                                                           newanswer='')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertTrue(data['error'])

    def test_positive_question_remove(self):

        """ a positive scenario for the removal of the question from the database """

        last_question = Questions.query.order_by(Questions.id.desc()).first()
        last_question_id = last_question.id
        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_2}
        response = self.client().delete(f'/questionremove/{last_question_id}', headers=jwt)
        self.assertEqual(response.status_code, 204)

    def test_error_question_remove(self):

        """ a positive scenario for the removal of the question from the database due to invalid question ID """

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_2}
        response = self.client().delete('/questionremove/999999999', headers=jwt)
        self.assertEqual(response.status_code, 404)

    def test_positive_remove_deck(self):

        """ a positive scenario for the removal of the deck from the database """

        last_deck = Decks.query.order_by(Decks.id.desc()).first()
        last_deck_id = last_deck.id
        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_2}
        response = self.client().delete(f'/deckremove/{last_deck_id}', headers=jwt)
        self.assertEqual(response.status_code, 204)

    def test_error_remove_deck(self):

        """ a negative scenario for the removal of the deck from the database due to invalid deck ID """

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_2}
        response = self.client().delete('/deckremove/999999999', headers=jwt)
        self.assertEqual(response.status_code, 404)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()