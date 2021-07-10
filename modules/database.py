#database.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_script import Manager
#from flask_migrate import Migrate, MigrateCommand

db = SQLAlchemy()
"""Migration Code"""
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)


"""
migrate = Migrate(app, db)
migrate.init_app(app,db) #,ender_as_batch=True
manager = Manager(app)
manager.add_command('db', MigrateCommand)


#Run python database.py db init, then migrate, edit the .py generated, then run upgrade
"""
class GalleryTable(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(64), index= True, unique=False)
    post_date = db.Column(db.Date, index=True,unique=False)
    acquired_date = db.Column(db.Date,index=True,unique=False)
    img_uri = db.Column(db.String(128),unique=True)
    img_thumb_uri = db.Column(db.String(128),unique=True)
    description = db.Column(db.Text,unique=True)
    acquisition_desc = db.Column(db.Text,unique=True)
    processing_desc = db.Column(db.Text,unique=True)
    
    def __init__(self, id,title, post_date, acquired_date, img_uri, img_thumb_uri, description, acquisition_desc, processing_desc):
        self.id = id
        self.title = title
        self.post_date = post_date
        self.acquired_date = acquired_date
        self.img_uri = img_uri
        self.img_thumb_uri = img_thumb_uri
        self.description = description
        self.acquisition_desc = acquisition_desc
        self.processing_desc = processing_desc

    def __repr__(self):
        return '<id %r>' % self.id
        
    def serialize(self):
        return {
            "id" : self.id,
            "title" : self.title,
            "post date" : self.post_date,
            "acquired date" : self.acquired_date,
            "img url" : self.img_uri,
            "img t url" : self.img_thumb_uri,
            "description" : self.description,
            "acquistion description": self.acquisition_desc,
            "processing description": self.processing_desc
            }


class BlogTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index= True, unique=False)
    post_date = db.Column(db.Date, index=True,unique=False)
    post_body = db.Column(db.Text,unique=True)

    def __init__(self, id, title, post_date, post_body):
        self.id = id
        self.title = title
        self.post_date = post_date
        self.post_body = post_body

    def __repr__(self):
        return '<id %r>' % self.id
        
    def serialize(self):
        return {
            "id" : self.id,
            "title" : self.title,
            "post date" : self.post_date,
            "post body" : self.post_body
            }



#if __name__ == "__main__":
#migration
#manager.run()
#db.create_all()
#db.session.commit()