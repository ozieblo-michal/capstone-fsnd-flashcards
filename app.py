import os
from flask import (Flask,
                   request,
                   abort,
                   jsonify,
                   render_template,
                   redirect,
                   url_for,
                   flash,
                   session)
from flask_cors import CORS
from flask_bootstrap import Bootstrap

from forms import (SelectDeck, MainFormNoLabel)

from models import (db,
                     Decks,
                     AuditTrail,
                     Questions)

import pandas as pd

from auth import AuthError #, requires_auth)





from functools import wraps
import json

from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv

from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.urandom(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')




    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id='NifC5AEOqX78XrBBsDDMf5OlKEqT2YFl',
        client_secret='uSbbd3nPSKuSXKj7xF8Is875Hh0SigeiJDPnHB6fX5WSHTQToLK0mawtuWpnzv1j',
        api_base_url='https://solitary-base-2169.eu.auth0.com',
        access_token_url='https://solitary-base-2169.eu.auth0.com/oauth/token',
        authorize_url='https://solitary-base-2169.eu.auth0.com/authorize',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )




    def requires_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'profile' not in session:
                # Redirect to Login page here
                return redirect('/')
            return f(*args, **kwargs)

        return decorated




    Bootstrap(app) # Flask-Bootstrap requires this line
    db.app = app
    db.init_app(app)
    CORS(app)
    cors = CORS(app, resources={r"*": {"origins": "*"}})




    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response






    @app.route('/callback')
    def callback_handling():
        # Handles response from token endpoint
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()

        # Store the user information in flask session.
        session['jwt_payload'] = userinfo
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
        return redirect('/')

    @app.route('/login')
    def login():
        return auth0.authorize_redirect(redirect_uri='https://capstone-fsnd-flashcards.herokuapp.com')

    @app.route('/dashboard')
    @requires_auth
    def dashboard():
        return render_template('dashboard.html',
                               userinfo=session['profile'],
                               userinfo_pretty=json.dumps(session['jwt_payload'],
                                                          indent=4))

    @app.route('/logout')
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {'returnTo': url_for('/', _external=True),
                  'client_id': 'NifC5AEOqX78XrBBsDDMf5OlKEqT2YFl'}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))









    #----------------------------------------------------------------------------#
    # Controllers.
    #----------------------------------------------------------------------------#

    #### https://python-adv-web-apps.readthedocs.io/en/latest/flask_forms.html
    @app.route('/', methods=['GET'])
    def index():
        form = MainFormNoLabel()
        questions = Questions.query.all()
        return render_template('index.html',
                               form=form,
                               questions=questions)

    @app.route('/managedecks', methods=['GET'])
    @requires_auth
    def managedecks():
        form = SelectDeck()
        questions = Questions.query.order_by('id').all()
        return render_template('managedecks.html',
                               form=form,
                               questions=questions)

    @app.route('/', methods=['POST'])
    @requires_auth
    def manage_deck():

        form = MainFormNoLabel()

        sentence = form.create_questions.sentence.data.strip()
        question = form.create_questions.question.data.strip()
        answer = form.create_questions.answer.data.strip()

        deck_name = form.create_questions.deck_name.data.strip()

        stanza_output = pd.DataFrame([[question, answer, sentence]],
                                     columns=['Question', 'Answer', 'Sentence'])

        if form.validate():
            flash(form.errors)
            return redirect(url_for('/'))

        else:
            error_in_insert = False

            try:

                is_it_current_deck = Decks.query.filter(Decks.name == deck_name).one_or_none()

                if is_it_current_deck is None:
                    new_deck = Decks(name=deck_name)
                    db.session.add(new_deck)

                for index, record in stanza_output.iterrows():

                    new_record = AuditTrail(username="testUser")

                    db.session.add(new_record)

                    new_question = Questions(question=record['Question'],
                                             answer=record['Answer'],
                                             sentence=record['Sentence'],
                                             auditTrail=new_record)

                    db.session.add(new_question)

                    if is_it_current_deck is None:
                        # https://stackoverflow.com/questions/16433338/inserting-new-records-with-one-to-many-relationship-in-sqlalchemy
                        new_deck.auditTrail.append(new_record)
                    else:
                        is_it_current_deck.auditTrail.append(new_record)

                db.session.commit()

            except Exception as e:
                error_in_insert = True
                print(f'Exception "{e}" in manage_deck()')
                db.session.rollback()
            finally:
                db.session.close()

            if not error_in_insert:
                return redirect(url_for('index'))
            else:
                print("Error in manage_deck()")
                abort(500)

    @app.route('/questionremove/<questionId>', methods=['DELETE'])
    @requires_auth
    def questionremove(questionId):
        try:
            question_to_remove = Questions.query.filter(Questions.id == questionId).one_or_none()
            question_to_remove.delete()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({'success': True,
                        'deleted': questionId,
                        'message': "Question successfully deleted"})

    @app.route('/deckremove/<deckId>', methods=['DELETE'])
    @requires_auth
    def removedeck(deckId):
        try:
            deck_to_remove = Decks.query.filter(Decks.id == deckId).one_or_none()
            deck_to_remove.delete()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return redirect("/managedecks")

    # https://knowledge.udacity.com/questions/419323
    @app.route("/updatesentence", methods=["POST"])
    @requires_auth
    def updatesentence():
        questionId = request.form.get("oldsentenceid")
        newsentence = request.form.get("newsentence")
        questions = Questions.query.filter(Questions.id==questionId).first()
        questions.sentence = newsentence
        db.session.commit()
        return redirect("/managedecks")

    @app.route("/updatequestion", methods=["POST"])
    @requires_auth
    def updatequestion():
        questionId = request.form.get("oldquestionid")
        newquestion = request.form.get("newquestion")
        questions = Questions.query.filter(Questions.id==questionId).first()
        questions.question = newquestion
        db.session.commit()
        return redirect("/managedecks")

    @app.route("/updateanswer", methods=["POST"])
    @requires_auth
    def updateanswer():
        questionId = request.form.get("oldanswerid")
        newanswer = request.form.get("newanswer")
        questions = Questions.query.filter(Questions.id==questionId).first()
        questions.answer = newanswer
        db.session.commit()
        return redirect("/managedecks")

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

# Launch.
if __name__ == "__main__":
    app.run()


# https://bitadj.medium.com/completely-uninstall-and-reinstall-psql-on-osx-551390904b86
# https://medium.com/@richardgong/how-to-upgrade-postgres-db-on-mac-homebrew-99516db3e57f
# https://stackoverflow.com/questions/61899041/how-to-fix-the-error-permission-denied-apply2files-usr-local-lib-node-modul
