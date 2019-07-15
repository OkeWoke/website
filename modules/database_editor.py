
#from flaskSite.modules.database import galleryTable
from modules.database import galleryTable
#from database import galleryTable

class gallery():
    
    def __init__(self, db):
        self.db = db
     
    def printing(self):
        for entry in galleryTable.query.all():
            print(entry.title)
          
    def insert(self, title, date_acq, url, t_url, desc):
        query = galleryTable.query.all()
        if len(query)>0:
            id = query[-1].id+1
        else:
            id=0

        date_pos = date.today()
        new_entry = galleryTable(id,title,date_pos,date_acq,url,t_url,desc)
        self.db.session.add(new_entry)
        self.db.session.commit()      

    def edit(self, id_num, title, date_acq, desc, *args):
        entry = galleryTable.query.filter_by(id=id_num).first() 
        if len(args)>0:
            entry.img_uri = args[0]
            entry.img_thumb_uri = args[1]
     
        entry.title = str(title)
        entry.acquired_date = date_acq
        entry.description = desc
        self.db.session.commit()

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
