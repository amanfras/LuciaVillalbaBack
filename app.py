# -*- coding: utf-8 -*-
"""
Created on Sun Dec 19 15:48:08 2021

@author: Adela
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')

db = SQLAlchemy(app)
ma = Marshmallow(app)

CORS(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "email", "password")

user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route("/user/add", methods=["POST"])
def add_user():
    email = request.json.get("email")
    password = request.json.get("password")

    record = User(email, password)
    db.session.add(record)
    db.session.commit()

    return jsonify(user_schema.dump(record))

@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = User.query.all()
    return jsonify(users_schema.dump(all_users))


if __name__ == "__main__":
    app.run(debug=True)