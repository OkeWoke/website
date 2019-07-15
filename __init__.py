from flask import Flask, jsonify,Response,url_for, send_from_directory, render_template, Markup,make_response
from flask_restful import Api, Resource, reqparse
from flask_httpauth import HTTPBasicAuth

#Two lines below are commented out as namespace changes when deployed on apache
#from flaskSite.modules.database import galleryTable, db
#from flaskSite.modules.database_editor import gallery as galDBE
from modules.database_editor import gallery as galDBE
from modules.database import galleryTable, db


from PIL import Image
from datetime import date
import os, math, werkzeug, imghdr, re


app  = Flask(__name__) #Not needed, this is performed inside database, might need to restructure this
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
api = Api(app)
auth = HTTPBasicAuth()
db.init_app(app)
dbe = galDBE(db)
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
    response.cache_control.max_age = 0
    return response

    
def htmlResp(content):
    return Response(render_template('home.html',content=Markup(content)),mimetype='text/html')

class favicon(Resource):

    def get(self):
        return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')
                               
class front(Resource):

    def get(self):
        latImg= galleryTable.query.all()[-1]
        htmlContent = render_template('front.html', title=latImg.title, img_url=latImg.img_uri, gallery_url="/gallery/"+str(latImg.id) )
        return htmlResp(htmlContent)
        
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
            
class editGallery(Resource):
    decorators = [auth.login_required]
 
    def get(self):
        htmlContent= "<div class='gallery'> Click on an image to edit it<br>"
        images = galleryTable.query.all()[::-1]
        for entry in images:
            url = entry.img_thumb_uri
            id = entry.id
            
            htmlContent+="<a href='/edit/"+str(id)+"' ><img src='"+url+"'></a>"
        htmlContent+="</div>"
        return htmlResp(htmlContent)

class editImg(Resource):
    decorators = [auth.login_required]
    
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type = str, required = True)
        self.reqparse.add_argument('acq_dat', type = str, required = True)
        self.reqparse.add_argument('img', location='files', type = werkzeug.datastructures.FileStorage)#is required but handeled differently
        self.reqparse.add_argument('description', type = str, required = True)
        
    def get(self, id_num):
        entry = galleryTable.query.filter_by(id=id_num).first()
        return htmlResp(render_template('editImg.html',title=entry.title,date=entry.acquired_date, desc=entry.description,id=id_num))
        
    def post(self, id_num):
        #Dont necessarily need new image
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
    
class gallery(Resource):

    def get(self):
        htmlContent= "<div class='gallery'>Click on an image for larger res and details!<br>"
        images = galleryTable.query.all()[::-1] 

        for entry in images:
            url = entry.img_thumb_uri
            id = entry.id
            
            htmlContent+="<a href='/gallery/"+str(id)+"' ><img src='"+url+"'></a>"
        htmlContent+="</div>"
        return htmlResp(htmlContent)       

class galleryEntry(Resource):

    def get(self, id_num):
        entry = galleryTable.query.filter_by(id=id_num).first()        
        htmlContent= render_template('post.html', title=entry.title, dat_cre=entry.acquired_date, dat_pos=entry.post_date, img_url =entry.img_uri,description=entry.description)
        return htmlResp(htmlContent)
       
class contact(Resource):

    def get(self):
        htmlContent=render_template('contact.html')
        return htmlResp(htmlContent)
        
class about(Resource):

    def get(self):
        htmlContent= render_template('about.html')
        return htmlResp(htmlContent)

api.add_resource(galleryEntry, '/gallery/<int:id_num>',endpoint='gal')
api.add_resource(front, '/', endpoint='galL')
api.add_resource(gallery, '/gallery')
api.add_resource(favicon,'/favicon.ico')
api.add_resource(addImg,'/add')
api.add_resource(contact, '/contact')
api.add_resource(about, '/about')
api.add_resource(editGallery,'/edit',endpoint='edit')
api.add_resource(editImg,'/edit/<int:id_num>',endpoint='editImg')

if __name__ == '__main__':
    app.run()

