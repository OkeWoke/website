from . import *
from ..__init__ import *

@routes.route('/blogEdit/<int:id_num>', methods = ['GET', 'POST'])
@auth.login_required
def blogEdit(id_num):
    if request.method == 'GET':
        entry = BlogTable.query.filter_by(id=id_num).first()
        return htmlResp(render_template('editBlog.html', id=id_num, title = entry.title, post_body = entry.post_body))
    
    elif request.method == 'POST':
        args = request.form
        title = args.get('title')
        post_body = args.get('post_body')
        f = open("debugnew.txt", "a+")
        img_indices = [(m.start()+9, m.end()-1) for m in re.finditer('img src="[\S^"]+"', post_body)]
        f.write("\n\n\n########\nPOST: title: {0}, post_body: #{1}#, img names detected: {2}\n\n\n".format(title, post_body, str([post_body[int(s):int(e)] for (s,e) in img_indices])))
        status = ""
        if len(img_indices) > 0: #If there are img tags found in the post body...
            f.write("Found img tags in body\n")
            offset = 0
            for indice_pair in img_indices:
                (s, e) = indice_pair
                s, e = int(s)+offset, int(e)+offset
                raw_img_string = post_body[s:e]
                f.write("Looking for img attached: {0}\n".format(raw_img_string))
                img = request.files.get(raw_img_string)
                if img is None: # No Image Attached
                    if "static/gallery/" not in raw_img_string: #not pre-existing img
                        status+='{0} <input type="file" name="{1}" accept="image/*"><br>\n'.format(raw_img_string, raw_img_string)
                else: # We found an attached image!
                    f.write("{0} was attached!\n".format(raw_img_string))
                    handle = handleImg(img) # bool, url, t_url
                    f.write("Img Handle Status: {0}\n".format(handle[0]))
                    if handle[0]:
                        post_body = post_body[:s] + handle[1] + post_body[e:]
                        offset+=(len(handle[1])-len(raw_img_string))

        if status=="":
            blogdbe.edit(id_num, title, post_body)
            return htmlResp(render_template('editBlog.html', status="Success!"))
        else:
            return htmlResp(render_template('editBlog.html',  id=id_num, title=title, post_body=post_body, status=status))


@routes.route('/blogAdd', methods=['GET', 'POST'])
@auth.login_required
def blogAdd():
    
    if request.method == 'GET':
        return htmlResp(render_template('addBlog.html'))
    elif request.method == 'POST':
        f = open("debugnew.txt", "a+")
               
        args = request.form
        title = args.get('title')
        post_body = args.get('post_body')
       
        img_indices = [(m.start()+9, m.end()-1) for m in re.finditer('img src="[\S^"]+"', post_body)]
        f.write("\n\n\n########\nPOST: title: {0}, post_body: #{1}#, img names detected: {2}\n\n\n".format(title, post_body, str([post_body[int(s):int(e)] for (s,e) in img_indices])))
        status = ""
        if len(img_indices) > 0: #If there are img tags found in the post body...
            f.write("Found img tags in body\n")
            offset = 0
            for indice_pair in img_indices:
                (s, e) = indice_pair
                s, e = int(s)+offset, int(e)+offset
                raw_img_string = post_body[s:e]
                f.write("Looking for img attached: {0}\n".format(raw_img_string))
                img = request.files.get(raw_img_string)
                if img is None: # No Image Attached
                    if "static/gallery/" not in raw_img_string: #not pre-existing img
                        status+='{0} <input type="file" name="{1}" accept="image/*"><br>\n'.format(raw_img_string, raw_img_string)
                else: # We found an attached image!
                    f.write("{0} was attached!\n".format(raw_img_string))
                    handle = handleImg(img) # bool, url, t_url
                    f.write("Img Handle Status: {0}\n".format(handle[0]))
                    if handle[0]:
                        post_body = post_body[:s] + handle[1] + post_body[e:]
                        offset+=(len(handle[1])-len(raw_img_string))

        if status=="":
            blogdbe.insert(title, post_body)
            return htmlResp(render_template('addBlog.html', status="Success!"))
        else:
            return htmlResp(render_template('addBlog.html', title=title, post_body=post_body, status=status))

@routes.route('/blog/<int:id_num>')
def blogEntry(id_num):
    entry = BlogTable.query.filter_by(id=id_num).first()
    html_post_body = markdown.markdown(entry.post_body)

        
    html_content = render_template('blogPost.html', title=entry.title, date_pos = entry.post_date, post_body=html_post_body)
    return htmlResp(html_content)

@routes.route('/blog')
def blogGet():
    html_content = "<div class='blog'><ul>"
    blog_entries = BlogTable.query.all()[::-1]
    for entry in blog_entries:
        id = entry.id
        title = entry.title
        html_content+="<li><a href='/blog/"+str(id)+"'>"+title+"</a><br>"+str(entry.post_date)+"</li><hr>"
    html_content+="</ul></div>"
    return htmlResp(html_content)