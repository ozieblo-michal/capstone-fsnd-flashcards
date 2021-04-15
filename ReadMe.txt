# FSND - Capstone

Final project for the Udacity Nanodegree:

https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044

The application was deployed on the Heroku platform using Docker. Please check: https://capstone-fsnd-flashcards.herokuapp.com/

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server.

#### Style guideline
backend code follows PEP8

## Database Setup (local run)
With Postgres running, create a database using the below command in terminal, then update the environment variable SQLALCHEMY_DATABASE_URI:
```bash
psql createdb DBNAME
```

To reset local database set RESET_DATABASE='True' before app run.

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
python app.py
```

or

```bash
export FLASK_APP=app
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

## Endpoints

Descriptions are included in the `app.py` file.

For RBAC endpoints it is recommended to use Postman | The Collaboration Platform for API Development https://www.postman.com ;

Example tokens are included in the package and in the submission note to the Reviewer, but it may be needed to re-create the API in Auth0 if u re open this repo in the future, when it will not be longer supported.
All details about how to do it are on Udacity FSND course or on Auth0 platform helpdesk.

Log-in link to the app to obtain access-token (permissions are given by the admin; the app has been submitted on 15 Apr 2021 and example tokens will be valid until the submission be checked)

https://dev-11opmcqr.eu.auth0.com/authorize?audience=https://capstone-fsnd-flashcards.herokuapp.com/&response_type=token&client_id=0qqHkqo6w24mc3PysFwUVdj4A5y5x9Qq&redirect_uri=https://capstone-fsnd-flashcards.herokuapp.com/questions

example cURLs:

```bash
curl http://localhost:5000/questions -X POST -H "Content-Type: application/json" -d "{\"sentence\": \"testsentence\", \"question\":\"testquestion\", \"answer\":\"testanswer\", \"username\":\"testusername\", \"deck_name\":\"testdeckname\"}"

{"message":"Question successfully created!","success":true}
```

```bash
curl http://localhost:5000/

{"n_questions":1,"questions":[{"answer":"testanswer","id":1,"question":"testquestion","sentence":"testsentence"}],"success":true}
```

## Users / Auth0 API

There are two types of roles, first can patch data (token 1), second can remove data (token 2), both can post data.

## Testing
To run the tests, make sure the postgres database is set, then run:

```bash
python test_app.py
```

Detailed test descriptions are included in the scripts.

## Useful links to get the flow

- https://auth0.com/docs/quickstart/backend/python/01-authorization
- https://python-adv-web-apps.readthedocs.io/en/latest/flask_forms.html
- https://stackoverflow.com/questions/16433338/inserting-new-records-with-one-to-many-relationship-in-sqlalchemy
- https://stackoverflow.com/questions/61899041/how-to-fix-the-error-permission-denied-apply2files-usr-local-lib-node-modul
- https://stackoverflow.com/questions/25002620/argumenterror-relationship-expects-a-class-or-mapper-argument
- https://bitadj.medium.com/completely-uninstall-and-reinstall-psql-on-osx-551390904b86
- https://medium.com/@richardgong/how-to-upgrade-postgres-db-on-mac-homebrew-99516db3e57f
- https://knowledge.udacity.com/questions/419323
- https://knowledge.udacity.com/questions/422782

## Short comment on the motivation for project and further plans

The application was created according to the PROJECT SPECIFICATION FSND - Capstone criteria.
The backend was designed to be paired with the frontend using WTForms in the future.
The idea is for the future development of this app to handle input from the user - any text note.
Then, the backend, expanded with a function supporting finding entities in sentences, will create decks with questions
containing a gap to fill in, which can be managed from the frontend level.

Plan to submit an application in this format was squandered by the Heroku cache limits for free access (500MB, but
the quite nice demo demanded around 20% more).

Note for the future, it's best to use Angular to handle Auth0 tokens from the frontend. Simple javascript is not enough
for RBAC, but for regular access only for logged in users already yes.

Check inspirations:
https://stanfordnlp.github.io/stanza/
https://apps.ankiweb.net
