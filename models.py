#from sqlalchemy import Column, String, Table, create_engine
from flask_sqlalchemy import SQLAlchemy
#import json
from datetime import datetime

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Decks(db.Model):

    __tablename__ = "decks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)

    # https://stackoverflow.com/questions/25002620/argumenterror-relationship-expects-a-class-or-mapper-argument
    # "Explicit is better than implicit" (Zen of Python)
    auditTrail = db.relationship("AuditTrail", back_populates="decks", cascade = "all, delete, delete-orphan")

    def __repr__(self):
        return f'{self.name}'

    def __init__(self, name):
        self.name = name

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id'   : self.id,
            'name' : self.name
        }


class AuditTrail(db.Model):

    __tablename__ = 'auditTrail'

    id         = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now())
    username = db.Column(db.String)
    deckID = db.Column(db.Integer, db.ForeignKey('decks.id'))
    #questionID = db.Column(db.Integer, autoincrement=True, unique=True)

    decks = db.relationship("Decks", back_populates="auditTrail", cascade = "all, delete")

    questions = db.relationship("Questions", backref="auditTrail", uselist=False, cascade="all, delete",
                                 passive_deletes=True)

    def __repr__(self):
        return f'<AuditTrail {self.id} {self.timestamp}>'

    def __init__(self, username):
        self.username = username

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id'         : self.id,
            'timestamp'  : self.timestamp,
            'username'   : self.username,
            'deckID'     : self.deckID,
            'questionID' : self.questionID,
        }

class Questions(db.Model):

    __tablename__ = 'questions'

    id = db.Column(db.Integer, db.ForeignKey('auditTrail.id', ondelete='CASCADE'), primary_key=True)
    sentence = db.Column(db.String)
    question = db.Column(db.String)
    answer = db.Column(db.String)

    def __repr__(self):
        return f'<Questions {self.id} {self.question}>'

    def __init__(self, sentence, question, answer, auditTrail):
        self.sentence   = sentence
        self.question   = question
        self.answer     = answer
        self.auditTrail = auditTrail

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id'       : self.id,
            'sentence': self.sentence,
            'question' : self.question,
            'answer'   : self.answer
        }
