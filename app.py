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
                   flash,
                   session)
from flask_cors import CORS
from flask_bootstrap import Bootstrap

from forms import (SelectDeck, MainFormNoLabel)

from models import (db,
                     Decks,
                     AuditTrail,
                     Questions)

from drop_everything import drop_everything

import pandas as pd

from auth import AuthError, requires_auth

import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.urandom(32)

    #DB_URL = "postgresql:///herok"
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

    #app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')

    # Flask-Bootstrap requires this line
    Bootstrap(app)

    db.app = app
    db.init_app(app)

    #drop_everything()

    #db.drop_all()
    #db.create_all()

    CORS(app)

    cors = CORS(app, resources={r"*": {"origins": "*"}})

    #----------------------------------------------------------------------------#
    # Controllers.
    #----------------------------------------------------------------------------#

# https://stackoverflow.com/questions/19069701/python-requests-library-how-to-pass-authorization-header-with-single-token

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    #### https://python-adv-web-apps.readthedocs.io/en/latest/flask_forms.html

    @app.route('/', methods=['GET'])
    def index():
        form = MainFormNoLabel()
        questions = Questions.query.all()

        YOUR_DOMAIN = os.environ.get('YOUR_DOMAIN')
        API_IDENTIFIER = os.environ.get('API_IDENTIFIER')
        YOUR_CLIENT_ID = os.environ.get('YOUR_CLIENT_ID')
        YOUR_CALLBACK_URI = os.environ.get('YOUR_CALLBACK_URI')

        AUTH0_AUTHORIZE_URL = f"https://{YOUR_DOMAIN}/authorize?audience={API_IDENTIFIER}&response_type=token&client_id={YOUR_CLIENT_ID}&redirect_uri={YOUR_CALLBACK_URI}"

        return render_template('index.html',
                               form=form,
                               questions=questions,
                               AUTH0_AUTHORIZE_URL=AUTH0_AUTHORIZE_URL)

    @app.route('/', methods=['POST'])
    def manage_deck():

        form = MainFormNoLabel()

        # insert for the Stanza
        sentence = form.create_questions.sentence.data.strip()
        question = form.create_questions.question.data.strip()
        answer = form.create_questions.answer.data.strip()

        deck_name = form.create_questions.deck_name.data.strip()

        stanza_output = pd.DataFrame([[question, answer, sentence]], columns=['Question', 'Answer', 'Sentence'])

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

    @app.route('/managedecks', methods=['GET'])
    #@requires_auth('get:managedecks')
    def managedecks():
        form = SelectDeck()
        questions = Questions.query.order_by('id').all()
        return render_template('managedecks.html',
                               form=form,
                               questions=questions)

    @app.route('/deckremove/<deckId>', methods=['DELETE'])
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
    def updatesentence():
        questionId = request.form.get("oldsentenceid")
        newsentence = request.form.get("newsentence")
        questions = Questions.query.filter(Questions.id==questionId).first()
        questions.sentence = newsentence
        db.session.commit()
        return redirect("/managedecks")

    @app.route("/updatequestion", methods=["POST"])
    def updatequestion():
        questionId = request.form.get("oldquestionid")
        newquestion = request.form.get("newquestion")
        questions = Questions.query.filter(Questions.id==questionId).first()
        questions.question = newquestion
        db.session.commit()
        return redirect("/managedecks")

    @app.route("/updateanswer", methods=["POST"])
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



# https://stackoverflow.com/questions/18752995/how-to-get-access-to-the-url-segments-after-a-in-python-flask
# https://stackoverflow.com/questions/22276170/unable-to-get-access-token-from-url-as-argument

    @app.route('/token', methods=["POST"])
    def token():

        #location_href = request.url
        #print(location_href)
        #sys.stdout.flush()

        location_href = location_href.split("access_token=")[1]

        token = location_href.split("&")[0]

        token_type = location_href.split("&")[1]
        token_type = token_type.split("token_type=")[1]
        token_type = token_type.split("&")[0]

        session['Authorization'] = token_type + " " + token

        print(session['Authorization'])
        sys.stdout.flush()

        return redirect("/permission")

    @app.route('/permission')
    @requires_auth("get:managedecks")
    def permission():
        print("Authorization success!")
        sys.stdout.flush()
        return redirect("/")



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
