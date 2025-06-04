from datetime import datetime

from .. import db


class VariableDictionary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    variables = db.relationship('DictionaryVariable', backref='dictionary', lazy=True, cascade='all, delete-orphan')


class DictionaryVariable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.String(255))
    dictionary_id = db.Column(db.Integer, db.ForeignKey('variable_dictionary.id'), nullable=False)
