#from flaskSite.modules.database import galleryTable, db
from modules.database import galleryTable, db
from datetime import date
from sqlalchemy import desc
import re

def titleCheck(title):
    check = title.split(' ')
    if len(check) == 0:
        return False
    for sub in check:
        if not sub.isalnum():
            return False
                
    return True

def dateFormat(dat_acq):
    dat_a = re.split('/|-',dat_acq)
    for sub in dat_a:
        if not sub.isdigit():
            return "ER"
        
    return date(int(dat_a[0]),int(dat_a[1]),int(dat_a[2]))
    
class gallery():
    def printing(self):
        for entry in galleryTable.query.all():
            print(entry.title)

    def insert(title, dat_acq, url,t_url, desc):
        """inserts data, gives string status in response, should replace with custom exception"""
        query = galleryTable.query.all()
        if len(query)>0:
            id = query[-1].id+1
        else:
            id=0
        dat_pos = date.today()
        
        if not titleCheck(title):
            return "Error: Title must contain alphanumeric characters"

        
        date_acq = dateFormat(dat_acq)
        if date_acq == "ER":
            return "Error: Please format date as YYYY/MM/DD"
            
        new_entry = galleryTable(id,title,dat_pos,date_acq,url,t_url,desc)
        
       
        db.session.add(new_entry)
        db.session.commit()
        return "Submitted!"
    
    def edit(idNum,title,acq_dat,desc,*args):
        entry = galleryTable.query.filter_by(id=idNum).first()
        if len(args)>0:
            entry.img_uri = args[0]
            entry.imgThumb_uri = args[1]
            
        if not titleCheck(title):
            return "Error: Title must contain alphanumeric characters"
     
        date_acq = dateFormat(acq_dat)
        if date_acq == "ER":
            return "Error: Please format date as YYYY/MM/DD"
        entry.title = title
        entry.acquired_date = date_acq
        entry.desc = desc
        print(entry.desc)
        db.session.update(entry)
        db.session.commit()
        return "Success!"
        
    def delete(self,entry):

        db.session.delete(entry)
        db.session.commit()

    def console_input(self):
        aaa = input()
        aaa = aaa.split(' ')
        #date should be entered as 22/22/11
        #dates are 2 and 3
        dat_p = aaa[2].split('/')
        date_pos = date(int(dat_p[0]),int(dat_p[1]),int(dat_p[2]))
        dat_a = aaa[3].split('/')
        date_acq = date(int(dat_a[0]),int(dat_a[1]),int(dat_a[2]))

        insert(int(aaa[0]),aaa[1],date_pos,date_acq,aaa[4],aaa[5],aaa[6])
        #2 title_test1 11/11/11 12/12/12 url_1 t_url_1 thisIsADescripTion
   

if __name__ == "__main__":
   g = gallery()
   g.printing()


"""Examples
Adding something to DB
new_entry = galleryTable(val0,val1....)
db.session.add(new_entry)
db.session.commit()



Updating

update_this = galleryTable.query/filter_by(id=3).first()
update_this.data = 'updated'
db.session.commit()



Deleting

del_this = galleryTable.query/filter_by(id=3).first()
db.session.delete(delet_this)
db.session.commit()
"""
