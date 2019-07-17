from flask import Flask, jsonify,Response,url_for, send_from_directory, render_template, Markup,make_response
from flask_restful import Api, Resource, reqparse
from flask_httpauth import HTTPBasicAuth

#Two lines below are commented out as namespace changes when deployed on apache
#from flaskSite.modules.database import GalleryTable, db
#from flaskSite.modules.database_editor import gallery as galDBE
from modules.database_editor import Gallery as galDBE
from modules.database import GalleryTable, db

from PIL import Image
from datetime import date
import os, math, werkzeug, imghdr, re, json

try:
    with open('config.json','r') as config_file:
        config_data = json.load(config_file)
except FileNotFoundError:
    print('No config file found, writing a default one')
    config_data = {'db':'sqlite:///app.db', 'username':'userNameHere', 'password':'passwordHere'}
    with open('config.json','w') as config_file:
        json.dump(config_data, config_file, indent=4)

app  = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = config_data['db']
api = Api(app)
auth = HTTPBasicAuth()
db.init_app(app)
dbe = galDBE(db)

#basic auth used, requires SSL for any security.
@auth.get_password
def get_password(username):
    if username == config_data['username']:
        return config_data['password']
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'Error': 'Unauthorized access'}), 401)
    
@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response

def dateCheck(date_acq):
    p = re.compile('^\d{4}[-|/]{1}[0-1]?\d{1}[-|/]{1}\d{1,2}$')
    if p.match(date_acq) != None:
        return True  
    return False

def dateFormat(date_acq):
     date_acq = re.split('/|-',date_acq)
     date_acq = date(int(date_acq[0]),int(date_acq[1]),int(date_acq[2]))  
     return date_acq   
     
def titleCheck(title):
    check = title.split(' ')
    if len(check) == 0:
        return False
    for sub in check:
        if not sub.isalnum():
            return False
                
    return True     
    
def validate(args, req_img):
    """Validates form data, title, date and img, returns True if valid else error string"""
    title = args['title']
    acq_dat = args['acq_dat']
    desc = args['description']
    img = args['img']
   
    if not titleCheck(title):
        return "Error: Title must contain alphanumeric characters!"
    if not dateCheck(acq_dat):
        return "Error: Please format date as YYYY/MM/DD!"
    
    if img == None and req_img:
        return "Error: No file selected!"
    elif img!= None:
        if img.filename[-4:]!="jpeg" and img.filename[-3:] != "jpg":
            return "Error: Please supply a jpg!"
        
    return True
    
def handleImg(title, img):
    """Handles saving image, takes title string and img object, returns true and urls or false and error string"""
    direc = ""#"/var/www/flaskSite/flaskSite/" 
    filename = title+"-"+img.filename
    img.save(direc+"static/gallery/"+filename)
    if imghdr.what(direc+'static/gallery/'+filename) =='jpeg':
               
        im = Image.open(direc+"static/gallery/"+filename)
        im.thumbnail((300,300))
        im = im.convert("RGB")
        im.save(direc+"static/gallery/thumb/T_"+filename,'JPEG')
                
        t_url = url_for('static',filename='gallery/thumb/T_'+filename)
        url = url_for('static', filename='gallery/'+filename)
                
        return (True, url, t_url)
    else:
        return (False, "Error: Please supply a jpg!")
            
def htmlResp(content):
    """Common template line """
    return Response(render_template('home.html',content=Markup(content)),mimetype='text/html')

class Favicon(Resource):

    def get(self):
        return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')
                               
class Front(Resource):

    def get(self):
        latImg= GalleryTable.query.all()[-1]
        html_content = render_template('front.html', title=latImg.title, img_url=latImg.img_uri, gallery_url="/gallery/"+str(latImg.id) )
        return htmlResp(html_content)
        
class AddImg(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, required = True)
        self.reqparse.add_argument('acq_dat', type = str, required = True)
        self.reqparse.add_argument('img', location='files', type = werkzeug.datastructures.FileStorage)#is required but handeled differently
        self.reqparse.add_argument('description', type = str, required = True)
        
        
        
    def get(self):
        return htmlResp(render_template('addImg.html'))
        
    def post(self):
        args = self.reqparse.parse_args()
        valid = validate(args, True)
        title = args['title']
        acq_dat = args['acq_dat']
        desc = args['description']
        img = args['img']
        
        print(type(desc))
        if type(valid) != str:
            handle = handleImg(title, img)
            acq_dat = dateFormat(acq_dat)
            if handle[0]:
                dbe.insert(title,acq_dat,handle[1],handle[2],desc)
                valid = "Success!"
            else:
                valid = handle[1]
        return htmlResp(render_template('addImg.html',status=valid))
        

class EditGallery(Resource):
    decorators = [auth.login_required]
 
    def get(self):
        html_content= "<div class='gallery'> Click on an image to edit it<br>"
        images = GalleryTable.query.all()[::-1]
        for entry in images:
            url = entry.img_thumb_uri
            id = entry.id
            
            html_content+="<a href='/edit/"+str(id)+"' ><img src='"+url+"'></a>"
        html_content+="</div>"
        return htmlResp(html_content)

class EditImg(AddImg):
    """ Inherits from addImg's parsed request arguments"""
    decorators = [auth.login_required]
    
    def __init__(self):
        super(editImg, self).__init__()
        
    def get(self, id_num):
        entry = GalleryTable.query.filter_by(id=id_num).first()
        return htmlResp(render_template('editImg.html',title=entry.title,date=entry.acquired_date, desc=entry.description,id=id_num))
        
    def post(self, id_num):
        args = self.reqparse.parse_args()
        title = args['title']
        acq_dat = args['acq_dat']
        desc = args['description']
        img = args['img']
        valid = validate(args, False)

        if type(valid) != str:
            acq_dat = dateFormat(acq_dat)
            if img != None:
                handle = handleImg(title, img)
                
                if handle[0]:
                    dbe.edit(id_num, title, acq_dat,desc, handle[1], handle[2])
                    valid = "Success!"
                else:
                    valid = handle[1]
            else:
                dbe.edit(id_num, title, acq_dat, desc)
                valid = "Success!"
        return htmlResp(render_template('editImg.html',title=title,date=acq_dat, desc=desc,id=id_num, status=valid))
    
class Gallery(Resource):

    def get(self):
        html_content= "<div class='gallery'>Click on an image for larger res and details!<br>"
        images = GalleryTable.query.all()[::-1] 

        for entry in images:
            url = entry.img_thumb_uri
            id = entry.id
            
            html_content+="<a href='/gallery/"+str(id)+"' ><img src='"+url+"'></a>"
        html_content+="</div>"
        return htmlResp(html_content)       

class GalleryEntry(Resource):

    def get(self, id_num):
        entry = GalleryTable.query.filter_by(id=id_num).first()        
        html_content= render_template('post.html', title=entry.title, dat_cre=entry.acquired_date, dat_pos=entry.post_date, img_url =entry.img_uri,description=entry.description)
        return htmlResp(html_content)
       
class Contact(Resource):

    def get(self):
        html_content=render_template('contact.html')
        return htmlResp(html_content)
        
class About(Resource):

    def get(self):
        html_content= render_template('about.html')
        return htmlResp(html_content)

api.add_resource(GalleryEntry, '/gallery/<int:id_num>',endpoint='gal')
api.add_resource(Front, '/', endpoint='galL')
api.add_resource(Gallery, '/gallery')
api.add_resource(Favicon,'/favicon.ico')
api.add_resource(AddImg,'/add')
api.add_resource(Contact, '/contact')
api.add_resource(About, '/about')
api.add_resource(EditGallery,'/edit',endpoint='edit')
api.add_resource(EditImg,'/edit/<int:id_num>',endpoint='editImg')

if __name__ == '__main__':
    app.run()

