#database.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class GalleryTable(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(64), index= True, unique=False)
    post_date = db.Column(db.Date, index=True,unique=False)
    acquired_date = db.Column(db.Date,index=True,unique=False)
    img_uri = db.Column(db.String(128),unique=True)
    img_thumb_uri = db.Column(db.String(128),unique=True)
    description = db.Column(db.Text,unique=True)
    
    def __init__(self, id,title, post_date, acquired_date, img_uri, img_thumb_uri, description):
        self.id = id
        self.title = title
        self.post_date = post_date
        self.acquired_date = acquired_date
        self.img_uri = img_uri
        self.img_thumb_uri = img_thumb_uri
        self.description = description

    def __repr__(self):
        return '<id %r>' % self.id