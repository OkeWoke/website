from . import *
from ..__init__ import *


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
        valid = galleryValidate(title, acq_dat, img, True)

        if valid[0]:
            handle = handleImg(img, config_data['directory'], title=title)
            acq_dat = dateFormat(acq_dat)
            if handle[0]:
                dbe.insert(title, acq_dat, handle[1], handle[2], desc, acq_desc, pro_desc)
                valid[1] = "Success!"
            else:
                valid[1] = handle[1]
        return htmlResp(render_template('addImg.html', status=valid[1]))


@app.route('/edit', methods=['GET', 'POST'])
@auth.login_required
def editGallery():
    html_content = "<div class='gallery'> Click on an image to edit it<br>"
    images = GalleryTable.query.all()[::-1]
    for entry in images:
        url = entry.img_thumb_uri
        id = entry.id

        html_content += "<a href='/edit/" + str(id) + "' ><img src='" + url + "'></a>"
    html_content += "</div>"
    return htmlResp(html_content)


@app.route('/edit/<int:id_num>', methods=['GET', 'POST'])
@auth.login_required
def editImg(id_num):
    if request.method == 'GET':
        entry = GalleryTable.query.filter_by(id=id_num).first()
        return htmlResp(render_template('editImg.html', title=entry.title, date=entry.acquired_date, desc=entry.description, id=id_num, acq_desc=entry.acquisition_desc, pro_desc=entry.processing_desc))

    elif request.method == 'POST':
        args = request.form
        title = args.get('title')
        acq_dat = args.get('acq_dat')
        desc = args.get('description')
        acq_desc = args.get('acq_description')
        pro_desc = args.get('pro_description')
        img = request.files.get('img')
        valid = galleryValidate(title, acq_dat, img, False)

        if valid[0]:
            acq_dat = dateFormat(acq_dat)
            if img is not None and img.filename != "":
                handle = handleImg(img, config_data['directory'], title=title)
                if handle[0]:
                    dbe.edit(id_num, title, acq_dat, desc, acq_desc, pro_desc, handle[1], handle[2])
                else:
                    valid[1] = handle[1]
            else:
                dbe.edit(id_num, title, acq_dat, desc, acq_desc, pro_desc)
                valid[1] = "Success!"
        return htmlResp(render_template('editImg.html', title=title, date=acq_dat, desc=desc, id=id_num, status=valid[1], acq_desc=acq_desc, pro_desc=pro_desc))


@app.route('/gallery')
def galleryGet():
    html_content = "<div class='gallery'>Click on an image for larger res and details!<br>"
    images = GalleryTable.query.all()[::-1]

    for entry in images:
        url = entry.img_thumb_uri
        id = entry.id

        html_content += "<a href='/gallery/" + str(id) + "' ><img src='" + url + "'></a>"
    html_content += "</div>"
    return htmlResp(html_content)


@app.route('/gallery/<int:id_num>')
def galleryEntry(id_num):
    entry = GalleryTable.query.filter_by(id=id_num).first()
    html_content = render_template('post.html', title=entry.title, dat_cre=entry.acquired_date, dat_pos=entry.post_date, img_url=entry.img_uri, description=entry.description, acq_description=entry.acquisition_desc, pro_description=entry.processing_desc)
    return htmlResp(html_content)
