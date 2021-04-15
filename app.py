import os
from dotenv import load_dotenv
from flask import (Flask,
                   request,
                   abort,
                   jsonify)
from flask_cors import CORS
import pandas as pd

from models import (db,
                    Decks,
                    AuditTrail,
                    Questions)
from drop_everything import drop_everything
from auth import AuthError, requires_auth

load_dotenv()

SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')
RESET_DATABASE = os.environ.get('RESET_DATABASE')

def setup_db(app):

    db.app = app
    db.init_app(app)

def create_app(test_config=None):

    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SECRET_KEY'] = os.urandom(32)
    setup_db(app)

    if RESET_DATABASE:
        drop_everything()
        db.drop_all()
        db.create_all()

    CORS(app)
    cors = CORS(app, resources={r"*": {"origins": "*"}})

    @app.after_request
    def after_request(response):

        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")

        return response

    @app.route('/', methods=['GET'])
    def show_questions():

        """
        an endpoint to handle base GET request for questions in the database
        """

        try:
            questions = Questions.query.all()
            questions = [question.format() for question in questions]
        except:
            abort(404)

        return jsonify({'success': True,
                        'n_questions': len(questions),
                        'questions': questions})

    @app.route('/questions', methods=['POST'])
    @requires_auth('post:question')
    def add_questions(jwt):

        """
        an endpoint to handle POST request for adding data to the database (with the intention of connecting
        the endpoint to the batch from the form in subsequent versions of the application); requires a token
        """

        data = request.get_json()
        sentence = data.get('sentence', '')
        question = data.get('question', '')
        answer = data.get('answer', '')
        username = data.get('username', '')
        deck_name = data.get('deck_name', '')

        if ((sentence == '') or (question == '') or (answer == '') or (username == '') or (deck_name == '')):
            abort(422)
        else:
            error_in_insert = False
            stanza_output = pd.DataFrame([[question, answer, sentence]],
                                         columns=['Question', 'Answer', 'Sentence'])
            try:
                existing_deck = Decks.query.filter(Decks.name == deck_name).one_or_none()

                if existing_deck is None:
                    new_deck = Decks(name=deck_name)
                    db.session.add(new_deck)

                for index, record in stanza_output.iterrows():
                    new_record = AuditTrail(username)
                    db.session.add(new_record)
                    new_question = Questions(question=record['Question'],
                                             answer=record['Answer'],
                                             sentence=record['Sentence'],
                                             auditTrail=new_record)
                    db.session.add(new_question)

                    if existing_deck is None:
                        new_deck.auditTrail.append(new_record)
                    else:
                        existing_deck.auditTrail.append(new_record)

                db.session.commit()
            except Exception as e:
                error_in_insert = True
                print(f'Exception "{e}" in add_questions()')
                db.session.rollback()
            finally:
                db.session.close()

            if not error_in_insert:
                return jsonify({'success': True,
                                'message': 'Question successfully created!'}), 201
            else:
                abort(500)

    @app.route('/questionremove/<questionId>', methods=['DELETE'])
    @requires_auth('delete:question')
    def question_remove(jwt, questionId):

        """
        an endpoint to handle DELETE request for the removal of the question from the database; requires a token
        """

        try:
            question_to_remove = Questions.query.filter(Questions.id == questionId).one_or_none()
            question_to_remove.delete()
        except:
            db.session.rollback()
            abort(404)
        finally:
            db.session.close()

        return jsonify({'success': True,
                        'deleted': questionId,
                        'message': "Question successfully deleted"}), 204

    @app.route('/decks', methods=['GET'])
    def decks():

        """
        an endpoint to handle base GET request for decks in the database
        """

        decks = Decks.query.order_by('id').all()

        try:
            decks = Decks.query.order_by('id').all()
            decks = [deck.format() for deck in decks]
        except:
            abort(404)

        return jsonify({'success': True,
                        'n_decks': len(decks),
                        'decks': decks})

    @app.route('/deckremove/<deckId>', methods=['DELETE'])
    @requires_auth('delete:deck')
    def remove_deck(jwt, deckId):

        """
        an endpoint to handle DELETE request for the removal of the deck from the database; requires a token
        """

        try:
            deck_to_remove = Decks.query.filter(Decks.id == deckId).one_or_none()
            deck_to_remove.delete()
        except:
            db.session.rollback()
            abort(404)
        finally:
            db.session.close()

        return jsonify({'success': True,
                        'deleted': deckId,
                        'message': 'Deck successfully removed!'}), 204

    @app.route("/updatesentence", methods=["POST"])
    @requires_auth('patch:sentence')
    def update_sentence(jwt):

        """
        an endpoint to handle PATCH/POST request for the modification of the sentence in the database; requires a token
        """

        data = request.get_json(force=True)
        questionId = data.get('oldsentenceid', '')
        newsentence = data.get('newsentence', '')

        if ((questionId == '') or (newsentence == '')):
            abort(422)

        questions = Questions.query.filter(Questions.id==questionId).first()
        questions.sentence = newsentence
        db.session.commit()

        return jsonify({'success': True,
                        'message': 'Sentence successfully modified!'}), 201

    @app.route("/updatequestion", methods=["POST"])
    @requires_auth('path:question')
    def update_question(jwt):

        """
        an endpoint to handle PATCH/POST request for the modification of the question in the database; requires a token
        """

        data = request.get_json(force=True)
        questionId = data.get('oldquestionid', '')
        newquestion = data.get('newquestion', '')

        if ((questionId == '') or (newquestion == '')):
            abort(422)

        questions = Questions.query.filter(Questions.id==questionId).first()
        questions.question = newquestion
        db.session.commit()

        return jsonify({'success': True,
                        'message': 'Question successfully modified!'}), 201

    @app.route("/updateanswer", methods=["POST"])
    @requires_auth('patch:answer')
    def update_answer(jwt):

        """
        an endpoint to handle PATCH/POST request for the modification of the answer in the database; requires a token
        """

        data = request.get_json(force=True)
        questionId = data.get('oldanswerid', '')
        newanswer = data.get('newanswer', '')

        if ((questionId == '') or (newanswer == '')):
            abort(422)

        questions = Questions.query.filter(Questions.id==questionId).first()
        questions.answer = newanswer
        db.session.commit()

        return jsonify({'success': True,
                        'message': 'Answer successfully modified!'}), 201

    """ error handlers for expected errors """

    @app.errorhandler(400)
    def bad_request(error):

        return jsonify({"success": False,
                        "error": 400,
                        "message": "Bad request"}), 400

    @app.errorhandler(404)
    def not_found(error):

        return jsonify({"success": False,
                        "error": 404,
                        "message": "Resource not found"}), 404

    @app.errorhandler(422)
    def unprocessable(error):

        return jsonify({"success": False,
                        "error": 422,
                        "message": "Unprocessable"}), 422

    @app.errorhandler(500)
    def unprocessable(error):

        return jsonify({"success": False,
                        "error": 500,
                        "message": "Internal server error"}), 500

    @app.errorhandler(AuthError)
    def autherror(error):

        error_code = error.status_code

        return jsonify({'success': False,
                        'error': error_code,
                        'message': error.error['description']}), error_code

    return app

app = create_app()

if __name__ == "__main__":
    app.run()
