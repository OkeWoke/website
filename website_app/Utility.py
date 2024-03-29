# Utility static class
import re
from datetime import date
from flask import Flask, jsonify, Response, url_for, send_from_directory, render_template, Markup, make_response, request
from PIL import Image
import imghdr
import string

FILE_EXTENSIONS = ['jpeg', 'png', 'gif', 'jpg']
    
def handleImg(img, direc, title=""):
    """Handles saving image, takes title string and img object, returns true and urls or false and error string"""

    if title != "":
        filename = title + "-" + img.filename
    else:
        filename = img.filename
    clean_filename, file_ext = filename.rsplit('.', maxsplit=1)
    if file_ext in FILE_EXTENSIONS:
        img.save(direc + "static/gallery/" + filename)
        if imghdr.what(direc + 'static/gallery/' + filename) in FILE_EXTENSIONS:
            im = Image.open(direc + "static/gallery/" + filename)
            im.thumbnail((300, 300))
            im = im.convert("RGB")
            t_filename = filename.rstrip('.')
            im.save(direc + "static/gallery/thumb/T_" + clean_filename+".jpg", 'JPEG')

            t_url = url_for('static', filename='gallery/thumb/T_' +clean_filename+".jpg")
            url = url_for('static', filename='gallery/' + filename)

            return (True, url, t_url)
    else:
        return (False, "Error: Please supply a valid format: {0}!".format(FILE_EXTENSIONS))


def htmlResp(content):
    """Common template line """
    return Response(render_template('home.html', content=Markup(content)), mimetype='text/html')

    
def dateFormat(date_acq):
    """Takes in date string, and returns date type"""
    date_acq = re.split('/|-', date_acq)
    date_acq = date(int(date_acq[0]), int(date_acq[1]), int(date_acq[2]))
    return date_acq


def dateCheck(date_acq):
    """Takes in date string, via regex checks for YYYY/MM/DD or YYYY-MM-DD format
    returns success bool and status string"""
    p = re.compile(r'^\d{4}[-|/]{1}[0-1]?\d{1}[-|/]{1}\d{1,2}$')
    if p.match(date_acq) is not None:
        return True, ""
    return False, "Error: Please format date as YYYY/MM/DD!"


def titleCheck(title):
    """Takes in title string, checks to ensure it contains(and only) alphanumeric chars,
    returns success bool and status string"""
    valid_chars = string.digits + string.ascii_letters + "." + "&"
    check = title.split(' ')
    if not check:
        return False, "Error: Title must contain alphanumeric characters!"
    for sub in check:
        if not sub.isalnum() and not any([x in valid_chars for x in sub]):
            return False, "Error: Title must contain alphanumeric characters!"
    return True, ""


def imgCheck(img, require_img):
    """Takes in image and if required bool, determines if image is of valid type,
    returns success bool and status string"""

    if img is None and require_img:
        return False, "Error: No file selected!"
    elif img is not None and img.filename != "":
        clean_filename, file_ext = img.filename.rsplit('.', maxsplit=1)
        if file_ext not in FILE_EXTENSIONS:
            return False, "Error: Please supply a valid format: {0}!".format(FILE_EXTENSIONS)
    return True, ""


def galleryValidate(title, acq_dat, img, req_img):
    """Validates form data, title, date and img, returns (success bool, status string)"""
    result = list(zip(titleCheck(title), dateCheck(acq_dat), imgCheck(img, req_img)))
    #result = [list(x) for x in result]
    return [all(result[0]), '\n'.join(result[1])]

def blogValidate(title):
    return titleCheck(title)
