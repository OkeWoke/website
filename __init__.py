from flask import Flask, jsonify,Response,url_for, send_from_directory, render_template, Markup,make_response, request
from flask_restful import Api, Resource, reqparse
from flask_httpauth import HTTPBasicAuth

from flaskSite.modules.database import GalleryTable, BlogTable, db
from flaskSite.modules.database_editor import Gallery as galDBE
from flaskSite.modules.database_editor import Blog as blogDBE

from PIL import Image
from datetime import date
import Utility as util
import os, math, werkzeug, imghdr, re, json, markdown

try:
    with open('config.json','r') as config_file:
        config_data = json.load(config_file)
except FileNotFoundError:
    print('No config file found, writing a default one')
    config_data = {'db':'sqlite:///app.db', 'username':'userNameHere', 'password':'passwordHere','directory':''}
    with open('config.json','w') as config_file:
        json.dump(config_data, config_file, indent=4)

app  = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = config_data['db']
api = Api(app)
auth = HTTPBasicAuth()
db.init_app(app)
dbe = galDBE(db)
blogdbe = blogDBE(db)

class GalleryAPI(Resource):
    def get(self):
        images = GalleryTable.query.all()[::-1]
        return jsonify([i.serialize() for i in images])

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
    
def handleImg(img, title=""):
    """Handles saving image, takes title string and img object, returns true and urls or false and error string"""
    direc = config_data['directory']#"/var/www/flaskSite/flaskSite/"
    if title !="": 
        filename = title+"-"+img.filename
    else:
        filename = img.filename
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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')                          

@app.route('/')
def front():
    latImg= GalleryTable.query.all()[-1]
    html_content = render_template('front.html', title=latImg.title, img_url=latImg.img_uri, gallery_url="/gallery/"+str(latImg.id) )
    return htmlResp(html_content)

@app.route('/add', methods=['GET', 'POST'])
@auth.login_required
def addImg():
    if request.method == 'GET':
        return htmlResp(render_template('addImg.html'))
        
    elif request.method == 'POST':
        
        args = request.form
        title = args.get('title')
        acq_dat = args.get('acq_dat')
        desc = args.get('description')
        acq_desc = args.get('acq_description')
        pro_desc = args.get('pro_description')
        img = request.files.get('img')
        valid = util.validate(title, acq_dat, desc, img, True)
       
        
        if type(valid) != str:
            handle = handleImg(img, title=title)
            acq_dat = util.dateFormat(acq_dat)
            if handle[0]:
                dbe.insert(title,acq_dat,handle[1],handle[2],desc,acq_desc,pro_desc)
                valid = "Success!"
            else:
                valid = handle[1]
        return htmlResp(render_template('addImg.html',status=valid))
        
@app.route('/edit', methods=['GET', 'POST'])
@auth.login_required
def editGallery():
    html_content= "<div class='gallery'> Click on an image to edit it<br>"
    images = GalleryTable.query.all()[::-1]
    for entry in images:
        url = entry.img_thumb_uri
        id = entry.id
        
        html_content+="<a href='/edit/"+str(id)+"' ><img src='"+url+"'></a>"
    html_content+="</div>"
    return htmlResp(html_content)

@app.route('/edit/<int:id_num>', methods=['GET', 'POST'])
@auth.login_required
def editImg(id_num):       
    if request.method == 'GET':
        entry = GalleryTable.query.filter_by(id=id_num).first()
        return htmlResp(render_template('editImg.html',title=entry.title,date=entry.acquired_date, desc=entry.description,id=id_num,acq_desc=entry.acquisition_desc, pro_desc=entry.processing_desc))
        
    elif request.method=='POST':
        args = request.form
        title = args.get('title')
        acq_dat = args.get('acq_dat')
        desc = args.get('description')
        acq_desc = args.get('acq_description')
        pro_desc = args.get('pro_description')
        img = request.files.get('img')
        valid = util.validate(title, acq_dat, desc, img, False)

        if type(valid) != str:
            acq_dat = util.dateFormat(acq_dat)
            if img != None and img.filename!="":
                handle = handleImg(img, title=title)
                
                if handle[0]:
                    dbe.edit(id_num, title, acq_dat,desc,acq_desc, pro_desc, handle[1], handle[2])
                    valid = "Success!"
                else:
                    valid = handle[1]
            else:
                dbe.edit(id_num, title, acq_dat, desc, acq_desc, pro_desc)
                valid = "Success!"
        return htmlResp(render_template('editImg.html',title=title,date=acq_dat, desc=desc,id=id_num, status=valid,acq_desc=acq_desc, pro_desc=pro_desc))

@app.route('/gallery')
def galleryGet():
    html_content= "<div class='gallery'>Click on an image for larger res and details!<br>"
    images = GalleryTable.query.all()[::-1] 

    for entry in images:
        url = entry.img_thumb_uri
        id = entry.id
        
        html_content+="<a href='/gallery/"+str(id)+"' ><img src='"+url+"'></a>"
    html_content+="</div>"
    return htmlResp(html_content)       

@app.route('/gallery/<int:id_num>')
def galleryEntry(id_num):
    entry = GalleryTable.query.filter_by(id=id_num).first()        
    html_content= render_template('post.html', title=entry.title, dat_cre=entry.acquired_date, dat_pos=entry.post_date, img_url =entry.img_uri,description=entry.description, acq_description=entry.acquisition_desc,pro_description=entry.processing_desc)
    return htmlResp(html_content)

@app.route('/blogEdit/<int:id_num>', methods = ['GET', 'POST'])
@auth.login_required
def blogEdit(id_num):
    if request.method == 'GET':
        entry = BlogTable.query.filter_by(id=id_num).first()
        return htmlResp(render_template('editBlog.html', id=id_num, title = entry.title, post_body = entry.post_body))
    
    elif request.method == 'POST':
        args = request.form
        title = args.get('title')
        post_body = args.get('post_body')

        #add validation?
        print('DOING THING')
        blogdbe.edit(id_num, title, post_body)
        valid = "Success!"

        return htmlResp(render_template('editBlog.html', id=id_num, title=title, post_body=post_body, status=valid))

@app.route('/blogAdd', methods=['GET', 'POST'])
@auth.login_required
def blogAdd():
    if request.method == 'GET':
        return htmlResp(render_template('addBlog.html'))
    elif request.method == 'POST':
        args = request.form
        title = args.get('title')
        post_body = args.get('post_body')
       
        img_indices = [(m.start()+9, m.end()-1) for m in re.finditer('img src="[\S^"]+"', post_body)]
        status = ""
      
        for indice_pair in img_indices:
            (s, e) = indice_pair
            s, e = int(s), int(e)
            img_src = post_body[s:e].split("/")[-1] # strip any possible folder structure.
            
            direc = config_data['directory']+"static/gallery/"
            if img_src in os.listdir(direc):
                post_body = post_body[:s] + direc + img_src + post_body[e:]
            else:
                img = request.files.get(img_src)
                if img is not None:
                    handle = handleImg(img) # bool, url, t_url?
                    post_body = post_body[:s] + handle[1] + post_body[e:]
                else:
                   
                    status = status + '{0} <input type="file" name="{1}" accept="image/*"><br>'.format(img_src, img_src)
        #todo add validation?
        
        if status=="":
            blogdbe.insert(title, post_body)
            status="Success!"
            return htmlResp(render_template('addBlog.html', status=status))
        else:
            return htmlResp(render_template('addBlog.html', title=title, post_body=post_body, status=status))

@app.route('/blog/<int:id_num>')
def blogEntry(id_num):
    entry = BlogTable.query.filter_by(id=id_num).first()
    html_post_body = markdown.markdown(entry.post_body)

        
    html_content = render_template('blogPost.html', title=entry.title, date_pos = entry.post_date, post_body=html_post_body)
    return htmlResp(html_content)

@app.route('/blog')
def blogGet():
    html_content = "<div class='blog'><ul>"
    blog_entries = BlogTable.query.all()[::-1]
    for entry in blog_entries:
        id = entry.id
        title = entry.title
        html_content+="<li><a href='/blog/"+str(id)+"'>"+title+"</a><br>"+str(entry.post_date)+"</li><hr>"
    html_content+="</ul></div>"
    return htmlResp(html_content)

@app.route('/about')       
def about():
    html_content= render_template('about.html')
    return htmlResp(html_content)

@app.route('/contact')
def contact():
    html_content=render_template('contact.html')
    return htmlResp(html_content)

@app.route('/feed')
def feed():
    with open('rss.xml', 'r') as file:
        return Response(file.read(), mimetype='text/xml')

api.add_resource(GalleryAPI, '/api/')
if __name__ == '__main__':
    app.run()