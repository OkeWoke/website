#Utility static class
import re
from datetime import date

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
    
def validate(title, acq_dat, desc, img, req_img):
    """Validates form data, title, date and img, returns True if valid else error string"""

    if not titleCheck(title):
        return "Error: Title must contain alphanumeric characters!"
    if not dateCheck(acq_dat):
        return "Error: Please format date as YYYY/MM/DD!"
    
    if img == None and req_img:
        return "Error: No file selected!"
    elif img!= None and img.filename !="":
        if img.filename[-4:]!="jpeg" and img.filename[-3:] != "jpg":
            return "Error: Please supply a jpg!"+str(img.filename)
        
    return True