#from flaskSite.modules.database import galleryTable, db
from modules.database import galleryTable
#from database import galleryTable, db
from datetime import date
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
    
    def __init__(self,db):
        self.db = db
     
    def printing(self):
        for entry in galleryTable.query.all():
            print(entry.title)
          
    def insert(self,title, dat_acq, url,t_url, desc):
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

        self.db.session.add(new_entry)
        self.db.session.commit()
        return "Submitted!"
        

    def edit(self, idNum,title,acq_dat,desc,*args):
        entry = galleryTable.query.filter_by(id=idNum).first()
       
        if len(args)>0:
            entry.img_uri = args[0]
            entry.imgThumb_uri = args[1]
            
        if not titleCheck(title):
            return "Error: Title must contain alphanumeric characters"
     
        date_acq = dateFormat(acq_dat)
        if date_acq == "ER":
            return "Error: Please format date as YYYY/MM/DD"
        entry.title = str(title)
        entry.acquired_date = date_acq
        entry.description = desc
        self.db.session.commit()
        return "Success!"
        

    def delete(self, entry):

        self.db.session.delete(entry)
        self.db.session.commit()


if __name__ == "__main__":
   g = gallery(db)
   g.printing()
   g.edit(11,"dddddddd","1000/12/12","del")
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
