
# curl http://localhost:5000/questions -X POST -H "Content-Type: application/json" -d "{\"sentence\": \"testsentence\", \"question\":\"testquestion\", \"answer\":\"testanswer\", \"username\":\"testusername\", \"deck_name\":\"testdeckname\"}"
# {"message":"Question successfully created!","success":true}

# curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d "{"sentence": "testsentence", "question":"testquestion", "answer":"testanswer", "username":"testusername", "deck_name\":"testdeckname"}"
# > "
# {"error":400,"message":"Bad request","success":false}

# curl http://127.0.0.1:5000/questions -X POST
# {"error":500,"message":"Internal server error","success":false}

# curl http://127.0.0.1:5000/questions
# {"error":404,"message":"Resource not found","success":false}

#https://dev-11opmcqr.eu.auth0.com/authorize?audience=https://capstone-fsnd-flashcards.herokuapp.com/&response_type=token&client_id=0qqHkqo6w24mc3PysFwUVdj4A5y5x9Qq&redirect_uri=https://capstone-fsnd-flashcards.herokuapp.com/questions



#curl --request POST \
#  --url 'https://YOUR_DOMAIN/oauth/token' \
#  --header 'content-type: application/x-www-form-urlencoded' \
#  --data 'grant_type=password&username=USERNAME&password=PASSWORD&audience=API_IDENTIFIER&scope=SCOPE&client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET"
# }'



import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import setup_db, create_app

from models import (Decks,
                    AuditTrail,
                    Questions)

from drop_everything import drop_everything

# it may be needed to log in to the app again if the token will expire
TOKEN_BASE_PERMISSION = "" #os.environ.get('TOKEN_BASE_PERMISSION')
TOKEN_FULL_PERMISSION = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjRiSmxmVktEOGx0SXBtUVJ6dmg1MiJ9.eyJpc3MiOiJodHRwczovL2Rldi0xMW9wbWNxci5ldS5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjAzMzg4N2ZiNzcxYjIwMDZiOWNkMzBmIiwiYXVkIjoiaHR0cHM6Ly9jYXBzdG9uZS1mc25kLWZsYXNoY2FyZHMuaGVyb2t1YXBwLmNvbS8iLCJpYXQiOjE2MTgwOTA4MTYsImV4cCI6MTYxODA5ODAxNiwiYXpwIjoiMHFxSGtxbzZ3MjRtYzNQeXNGd1VWZGo0QTV5NXg5UXEiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTpkZWNrIiwiZGVsZXRlOnF1ZXN0aW9uIiwicGF0Y2g6YW5zd2VyIiwicGF0Y2g6c2VudGVuY2UiLCJwYXRoOnF1ZXN0aW9uIiwicG9zdDpxdWVzdGlvbiJdfQ.iv18q0eI_HaV88dVG0dUWxk30O4CwK5LlRonhqJajAReeT9h_Ygi_oWZve2zLZ54wYFDA0DLsCCZp90qep8v_YwQhXQgmK6BBmKya1yhL_-G30MVx6IyhercHn2E6QFTBNvGb4cCRkDJGoyr2lldtUOF8qdG2mEOpGZXrdobs_3SO4fMu6aypSkaD6CNm_MGmC5_oYDI4j0LrZzRJywm-mAceSEU-C_m1l-NooIMNbeH_UQ2zTloR4ifEG5jFJK3lDKq47aFDFnzPL0a-l80JeUeh6jnwr2pTl_BaXpN1XnW3leH25XNmttlkP82Sap3W7VrEVhASNR-BBqjV8aXFw' #os.environ.get('TOKEN_FULL_PERMISSION')

TOKEN_BASE_PERMISSION = f"Bearer {TOKEN_BASE_PERMISSION}"
TOKEN_FULL_PERMISSION = f"Bearer {TOKEN_FULL_PERMISSION}"


def question_insert():
    auditTrail = AuditTrail(username='TESTUSERNAMEADDQUESTION')
    question = Questions(sentence='TEST SENTENCE ADD QUESTION',
                         question='TEST QUESTION ADD QUESTION',
                         answer='TEST ANSWER ADD QUESTION',
                         auditTrail=auditTrail)
    question.insert()
    return question.id

class CapstoneTestCase(unittest.TestCase):
    """This class represents the Capstone test case"""



    def setUp(self):
        """Define test variables and initialize app."""



        self.app = create_app()
        self.client = self.app.test_client

        setup_db(self.app)

        #self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        #self.app.config['SECRET_KEY'] = os.urandom(32)
        #self.app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
        #self.db.app = self.app
        #self.db.init_app(self.app)


        with self.app.app_context():
            self.db = SQLAlchemy()
            drop_everything()
            self.db.drop_all()
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # https://knowledge.udacity.com/questions/422782

    # (1) success
    def test_show_questions(self):

        question_insert()

        response = self.client().get('/')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['n_questions'], 11)
        self.assertEqual(data['questions'], 1)

    # (2) success
    def test_add_questions(self):
        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
        response = self.client().post('/questions',
                                      headers=jwt,
                                      data=json.dumps(dict(sentence = 'TEST SENTENCE ADD QUESTION',
                                                           question = 'TEST QUESTION ADD QUESTION',
                                                           answer = 'TEST ANSWER ADD QUESTION',
                                                           username = 'TESTUSERNAMEADDQUESTION',
                                                           deck_name = 'TESTDECKNAMEADDQUESTION')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['message'], 'Question successfully created!')

    # (3) error behavior due to lack of permission
    def test_add_questions(self):
        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
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

    # (4) error behavior due to lack of token
    def test_cannot_add_questions_due_to_lack_of_token(self):
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

    # (5) error behavior due to lack of username (every insert parameter must be filled)
    def test_cannot_add_questions(self):
        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
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

    # (6) success
    def test_question_remove(self):

        question_id = question_insert()

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
        response = self.client().delete(f'/questionremove/{question_id}',
                                        headers=jwt)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully deleted"')

    # (7) error behavior
    def test_cannot_question_remove(self):
        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
        response = self.client().delete('/questionremove/9999', headers=jwt)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    # (8) success
    def test_remove_deck(self):
        deck = Decks(name="TESTDECKNAME")
        deck_id = deck.id
        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
        response = self.client().get(f'/deckremove/{deck_id}', headers=jwt)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Deck successfully removed!')

    # (9) error behavior
    def test_cannot_remove_deck(self):
        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
        response = self.client().delete('/deckremove/9999', headers=jwt)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    # (10) success
    def test_update_question(self):

        question_id = question_insert()

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
        response = self.client().post('/updatequestion',
                                      headers=jwt,
                                      data=json.dumps(dict(oldsentenceid=question_id,
                                                           newsentence='UPDATED SENTENCE TEST')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Sentence successfully modified!')

    # (11) error behavior due to lack of new sentence string
    def test_cannot_update_question_due_to_lack_of_sentence_string(self):

        question_id = question_insert()

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
        response = self.client().post('/updatequestion',
                                      headers=jwt,
                                      data=json.dumps(dict(oldsentenceid=question_id,
                                                           newsentence='')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    # (12) success
    def test_update_question(self):

        question_id = question_insert()

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
        response = self.client().post('/updatequestion',
                                      headers=jwt,
                                      data=json.dumps(dict(oldquestionid=question_id,
                                                           newquestion='UPDATED QUESTION TEST')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully modified!')

    # (13) error behavior due to lack of new question string
    def test_cannot_update_question_due_to_lack_of_new_question_string(self):

        question_id = question_insert()

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
        response = self.client().post('/updatequestion',
                                      headers=jwt,
                                      data=json.dumps(dict(oldquestionid=question_id,
                                                           newquestion='')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    # (14) success
    def test_update_answer(self):

        question_id = question_insert()

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
        response = self.client().post('/updateanswer',
                                      headers=jwt,
                                      data=json.dumps(dict(oldanswerid=question_id,
                                                           newanswer='UPDATED QUESTION TEST')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Answer successfully modified!')

    # (15) error behavior due to lack of new answer string
    def test_cannot_update_answer_due_to_lack_of_answer_string(self):

        question_id = question_insert()

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
        response = self.client().post('/updateanswer',
                                      headers=jwt,
                                      data=json.dumps(dict(oldanswerid=question_id,
                                                           newanswer='')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable')

    # (16) error behavior due to lack of token
    def test_cannot_update_answer_due_to_lack_ot_token(self):

        question_id = question_insert()

        jwt = {'Content-Type': 'application/json'}
        response = self.client().post('/updateanswer',
                                      headers=jwt,
                                      data=json.dumps(dict(oldanswerid=question_id,
                                                           newanswer='')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertTrue(data['error'])
        self.assertEqual(data['success'], False)

    # (17) error behavior due to lack of permission
    def test_update_answer_due_to_lack_of_permission(self):

        question_id = question_insert()

        jwt = {'Content-Type': 'application/json', 'Authorization': TOKEN_FULL_PERMISSION}
        response = self.client().post('/updateanswer',
                                      headers=jwt,
                                      data=json.dumps(dict(oldanswerid=question_id,
                                                           newanswer='UPDATED QUESTION TEST')),
                                      content_type='application/json')
        data = json.loads(response.data)
        self.assertTrue(data['error'])
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()