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


import pyrebase

config = {
  'apiKey': "AIzaSyDyQi_BwRTdvDXQ8LjWeDVNgOLEccQW3CI",
  'authDomain': "lucia-back.firebaseapp.com",
  'storageBucket': "lucia-back.appspot.com",
  "databaseURL": "",
  "serviceAccount": "lucia-back-firebase.json"
}

firebase = pyrebase.initialize_app(config)

storage = firebase.storage()



app = Flask(__name__)

UPLOAD_FOLDER = 'imagenes'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    imagen = db.Column(db.String, nullable=False)
    fecha = db.Column(db.String(), nullable=False)


    def __init__(self, title, content, fecha, imagen):
        self.title = title
        self.content = content
        self.fecha=fecha
        self.imagen=imagen

class BlogSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "content", "fecha", "imagen")

blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True)


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
	
@app.route("/blog/add", methods=["POST"])
def add_blog():
    title = request.form.get("title")
    content = request.form.get("content")
    fecha = request.form.get("fecha")
    imagen = request.files["imagen"]
    storage.child(f'images/{imagen.filename}').put(imagen)
    record = Blog(title, content, fecha, f'images/{imagen.filename}')
    db.session.add(record)
    db.session.commit()

    return jsonify(blog_schema.dump(record))

@app.route("/delete/<id>", methods=["DELETE"])
def delete_blog(id):
    record = Blog.query.get(id)
    print(record.imagen)
    storage.delete(record.imagen)
    
    db.session.delete(record)
    db.session.commit()
    

    return jsonify(blog_schema.dump(record))

@app.route("/blog/<id>", methods=["PUT"])
def update_blog(id):
    record = Blog.query.get(id)
    title = request.form.get("title")
    content = request.form.get("content")
    fecha = request.form.get("fecha")
    imagen = request.files["imagen"]
    
    record.title=title
    record.content=content
    record.fecha=fecha
    storage.child(record.imagen).put(imagen)
    
    db.session.commit()

    return jsonify(blog_schema.dump(record))

@app.route("/blog/get", methods=["GET"])
def get_all_blogs():
    all_blogs = Blog.query.all()
    for blog in all_blogs:
        blog.imagen= storage.child(blog.imagen).get_url(1)
    return jsonify(blogs_schema.dump(all_blogs))

@app.route("/blog/get/<id>", methods=["GET"])
def get_blog(id):
    record = Blog.query.get(id)
    return jsonify(blog_schema.dump(record))


if __name__ == "__main__":
    app.run(debug=True)