from flask import Flask, jsonify,Response,url_for, send_from_directory, render_template, Markup,make_response
from flask_restful import Api, Resource, reqparse
from flask_httpauth import HTTPBasicAuth
#Two lines below are commented out as namespace changes when deployed on apache
#from flaskSite.modules.database import galleryTable, db
#from flaskSite.modules.database_editor import gallery as dbe
from modules.database_editor import gallery as dbe
from modules.database import galleryTable, db
from PIL import Image
import os, math,werkzeug,imghdr


app  = Flask(__name__) #Not needed, this is performed inside database, might need to restructure this
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
api = Api(app)
auth = HTTPBasicAuth()
db.init_app(app)

#basic auth used, requires SSL for any security.
@auth.get_password
def get_password(username):
    if username == 'userNameHere':
        return 'passwordHere'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)
    
@app.after_request
def add_header(response):
    response.cache_control.max_age = 600
    return response
    
class addImg(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, required = True)
        self.reqparse.add_argument('acq_dat', type = str, required = True)
        self.reqparse.add_argument('img', location='files', type = werkzeug.datastructures.FileStorage)#is required but handeled differently
        self.reqparse.add_argument('description', type = str, required = True)
      
        super(addImg, self).__init__()
        
    def get(self):
        return Response(render_template('home.html',content=Markup(render_template('addImg.html'))),mimetype='text/html')
        
    def post(self):
        args = self.reqparse.parse_args()
        title = args['title']
        acq_dat = args['acq_dat']
        desc = args['description']
        print('current working dir{0}'.format(os.getcwd()))
        img = args['img']
        direc = "/var/www/flaskSite/flaskSite/"
        if img !=None:
            filename = title+"-"+img.filename
            img.save(direc+"static/gallery/"+filename)
            if imghdr.what(direc+'static/gallery/'+filename) =='jpeg':
               
                im = Image.open(direc+"static/gallery/"+filename)
                im.thumbnail((300,300))
                im = im.convert("RGB")
                im.save(direc+"static/gallery/thumb/T_"+filename,'JPEG')
                
                t_url = url_for('static',filename='gallery/thumb/T_'+filename)
                url = url_for('static', filename='gallery/'+filename)
                
                form_status = dbe.insert(title,acq_dat,url,t_url,desc)
            else:
                form_status = "Error: Please supply a jpg!"
        else:
            form_status = "Error: No file selected!"
       
        return Response(render_template('home.html',content=Markup(render_template('addImg.html',status=form_status))),mimetype='text/html')
        
class gallery(Resource):

    def get(self):
        htmlContent= "<div class='gallery'>Click on an image for larger res and details!<br>"
        images = galleryTable.query.all()[::-1] 
        print(type(images))
        for entry in images:
            url = entry.imgThumb_uri
            id = entry.id
            
            htmlContent+="<a href='https://okewoke.com/gallery/"+str(id)+"' ><img src='"+url+"'></a>"
        htmlContent+="</div>"
        return Response(render_template('home.html', content = Markup(htmlContent)),mimetype='text/html')

        
class favicon(Resource):

    def get(self):
        return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')
                               
class front(Resource):

    def get(self):
        latImg= galleryTable.query.all()[-1]
        htmlContent = render_template('front.html', title=latImg.title, img_url=latImg.img_uri, gallery_url="https://okewoke.com/gallery/"+str(latImg.id) )
        return Response(render_template('home.html', content = Markup(htmlContent),mimetype='text/html'))
        
class galleryEntry(Resource):

    def get(self, idNum):
        entry = galleryTable.query.filter_by(id=idNum).first()        
        htmlContent= render_template('post.html', title=entry.title, dat_cre=entry.acquired_date, dat_pos=entry.post_date, img_url =entry.img_uri,description=entry.description)
        return Response(render_template('home.html', content = Markup(htmlContent)),mimetype='text/html')
        
class contact(Resource):

    def get(self):
        htmlContent=render_template('contact.html')
        return Response(render_template('home.html', content = Markup(htmlContent)),mimetype='text/html')
        
class about(Resource):

    def get(self):
        htmlContent= render_template('about.html')
        return Response(render_template('home.html', content = Markup(htmlContent)),mimetype='text/html')
        
       
api.add_resource(galleryEntry, '/gallery/<int:idNum>',endpoint='gal')
api.add_resource(front, '/', endpoint='galL')
api.add_resource(gallery, '/gallery')
api.add_resource(favicon,'/favicon.ico')
api.add_resource(addImg,'/add')
api.add_resource(contact, '/contact')
api.add_resource(about, '/about')
if __name__ == '__main__':
    app.run()

