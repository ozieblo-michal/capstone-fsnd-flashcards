#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
from flask import (Flask,
                   request,
                   abort,
                   jsonify,
                   render_template,
                   redirect,
                   url_for,
                   flash)
from flask_cors import CORS

from models import (db,
                     Decks,
                     AuditTrail,
                     Questions)

from drop_everything import drop_everything

import pandas as pd

from auth import AuthError, requires_auth

QUESTIONS_PER_PAGE = 10

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

def setup_db(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.urandom(32)

    # DB_URL = "postgresql:///herok"
    # app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///herokutest" # os.environ.get('SQLALCHEMY_DATABASE_URI')

    db.app = app
    db.init_app(app)

    # drop_everything()

    # db.drop_all()
    # db.create_all()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    setup_db(app)

    CORS(app)

    cors = CORS(app, resources={r"*": {"origins": "*"}})

    @app.after_request
    def after_request(response):

        response.headers.add("Access-Control-Allow-Headers",
                             "Content-Type, Authorization")

        response.headers.add("Access-Control-Allow-Methods",
                             "GET, POST, PATCH, DELETE, OPTIONS")

        return response

    #----------------------------------------------------------------------------#
    # Controllers.
    #----------------------------------------------------------------------------#

    #### https://python-adv-web-apps.readthedocs.io/en/latest/flask_forms.html

    def paginate_questions(request, questions_list):

        page = request.args.get('page', 1, type=int)

        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in questions_list]

        paginated_questions = questions[start:end]

        return paginated_questions

    @app.route('/', methods=['GET'])
    def show_questions():
        questions = Questions.query.all()
        paginated_questions = paginate_questions(request, questions)
        if len(paginated_questions) == 0:
            abort(404)
        return jsonify({
            'success': True,
            'n_questions': len(questions),
            'questions': paginated_questions
        })

    @app.route('/questions', methods=['POST'])
    @requires_auth('post:question')
    def add_questions(jwt):
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
            stanza_output = pd.DataFrame([[question, answer, sentence]], columns=['Question', 'Answer', 'Sentence'])
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
                        # https://stackoverflow.com/questions/16433338/inserting-new-records-with-one-to-many-relationship-in-sqlalchemy
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
                return jsonify({
                    'success': True,
                    'message': 'Question successfully created!'
                }), 201
            else:
                abort(500)

    @app.route('/questionremove/<questionId>', methods=['DELETE'])
    @requires_auth('delete:question')
    def question_remove(jwt, questionId):
        try:
            question_to_remove = Questions.query.filter(Questions.id == questionId).one_or_none()
            question_to_remove.delete()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({'success': True,
                        'deleted': questionId,
                        'message': "Question successfully deleted"}), 204

    @app.route('/decks', methods=['GET'])
    def decks():
        decks = Decks.query.order_by('id').all()
        return jsonify({
            'success': True,
            'n_decks': len(decks),
            'decks': decks
        })

    @app.route('/deckremove/<deckId>', methods=['DELETE'])
    @requires_auth('delete:deck')
    def remove_deck(jwt, deckId):
        try:
            deck_to_remove = Decks.query.filter(Decks.id == deckId).one_or_none()
            deck_to_remove.delete()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({
            'success': True,
            'deleted': deckId,
            'message': 'Deck successfully removed!'
        }), 204

# https://knowledge.udacity.com/questions/419323
    @app.route("/updatesentence", methods=["POST"])
    @requires_auth('patch:sentence')
    def update_sentence(jwt):
        data = request.get_json()
        questionId = data.get('oldsentenceid', '')
        newsentence = data.get('newsentence', '')
        if ((questionId == '') or (newsentence == '')):
            abort(422)
        questions = Questions.query.filter(Questions.id==questionId).first()
        questions.sentence = newsentence
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Sentence successfully modified!'
        }), 201

    @app.route("/updatequestion", methods=["POST"])
    @requires_auth('path:question')
    def update_question(jwt):
        data = request.get_json()
        questionId = data.get('oldquestionid', '')
        newquestion = data.get('newquestion', '')
        if ((questionId == '') or (newquestion == '')):
            abort(422)
        questions = Questions.query.filter(Questions.id==questionId).first()
        questions.question = newquestion
        db.session.commit()
        return jsonify({
                    'success': True,
                    'message': 'Question successfully modified!'
                }), 201

    @app.route("/updateanswer", methods=["POST"])
    @requires_auth('patch:answer')
    def update_answer(jwt):
        data = request.get_json()
        questionId = data.get('oldanswerid', '')
        newanswer = data.get('newanswer', '')
        if ((questionId == '') or (newanswer == '')):
            abort(422)
        questions = Questions.query.filter(Questions.id==questionId).first()
        questions.answer = newanswer
        db.session.commit()
        return jsonify({
            'success': True,
            'message': 'Answer successfully modified!'
        }), 201

    #----------------------------------------------------------------------------#
    # Error handlers for expected errors.
    #----------------------------------------------------------------------------#

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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

if __name__ == "__main__":
    #port = int(os.environ.get("PORT", 5000))
    #app.run(host='0.0.0.0', port=port)
    app.run()
        #host='0.0.0.0',
         #    port=8080) #,
             #debug=True)

# https://bitadj.medium.com/completely-uninstall-and-reinstall-psql-on-osx-551390904b86
# https://medium.com/@richardgong/how-to-upgrade-postgres-db-on-mac-homebrew-99516db3e57f
# https://stackoverflow.com/questions/61899041/how-to-fix-the-error-permission-denied-apply2files-usr-local-lib-node-modul
