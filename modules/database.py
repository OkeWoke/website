#database.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#app  = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy()

class galleryTable(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(64), index= True, unique=False)
    post_date = db.Column(db.Date, index=True,unique=False)
    acquired_date = db.Column(db.Date,index=True,unique=False)
    img_uri = db.Column(db.String(128),unique=True)
    imgThumb_uri = db.Column(db.String(128),unique=True)
    description = db.Column(db.Text,unique=True)
    
    def __init__(self,id,title,post_date,acquired_date,img_uri,imgThumb_uri,description):
        self.id = id
        self.title = title
        self.post_date = post_date
        self.acquired_date = acquired_date
        self.img_uri = img_uri
        self.imgThumb_uri = imgThumb_uri
        self.description = description
        
     
    def __repr__(self):
        return '<id %r>' % self.id