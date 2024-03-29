from . import *
from ..__init__ import *


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
 

@app.route('/')
def front():
    print('aa')
    latImg = GalleryTable.query.all()[-1]
    html_content = render_template('front.html', title=latImg.title, img_url=latImg.img_uri, gallery_url="/gallery/" + str(latImg.id))
    return htmlResp(html_content)


@app.route('/about')
def about():
    html_content = render_template('about.html')
    return htmlResp(html_content)


@app.route('/contact')
def contact():
    html_content = render_template('contact.html')
    return htmlResp(html_content)


@app.route('/feed')
def feed():
    with open('rss.xml', 'r') as file:
        return Response(file.read(), mimetype='text/xml')
