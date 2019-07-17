from flaskSite.modules.database import GalleryTable

from datetime import date

class Gallery():
    
    def __init__(self, db):
        self.db = db
     
    def printing(self):
        for entry in GalleryTable.query.all():
            print(entry.title)
          
    def insert(self, title, date_acq, url, t_url, desc):
        query = GalleryTable.query.all()
        if len(query)>0:
            id = query[-1].id+1
        else:
            id=0

        date_pos = date.today()
        new_entry = GalleryTable(id,title,date_pos,date_acq,url,t_url,desc)
        self.db.session.add(new_entry)
        self.db.session.commit()      

    def edit(self, id_num, title, date_acq, desc, *args):
        entry = GalleryTable.query.filter_by(id=id_num).first() 
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
   g = Gallery(db)
   g.printing()
   g.edit(11,"dddddddd","1000/12/12","del")
   g.printing()
