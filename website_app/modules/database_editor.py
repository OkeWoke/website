from website_app.modules.database import GalleryTable, BlogTable
#from database import GalleryTable, BlogTable, db
from datetime import date


class Gallery():

    def __init__(self, db):
        self.db = db
        self.table = GalleryTable

    def printing(self):
        for entry in self.table.query.all():
            print(entry.title)

    def insert(self, title, date_acq, url, t_url, desc, desc_acq, desc_pro):
        query = self.table.query.all()
        if len(query) > 0:
            id = query[-1].id + 1
        else:
            id = 0

        date_pos = date.today()
        new_entry = self.table(id, title, date_pos, date_acq, url, t_url, desc, desc_acq, desc_pro)  # change to kwargs?
        self.db.session.add(new_entry)
        self.db.session.commit()

    def edit(self, id_num, title, date_acq, desc, desc_acq, desc_pro, *args):
        entry = self.table.query.filter_by(id=id_num).first()
        if len(args) > 0:
            entry.img_uri = args[0]
            entry.img_thumb_uri = args[1]

        entry.title = str(title)
        entry.acquired_date = date_acq
        entry.description = desc
        entry.acquisition_desc = desc_acq
        entry.processing_desc = desc_pro
        self.db.session.commit()

    def delete(self, entry):
        self.db.session.delete(entry)
        self.db.session.commit()


class Blog():

    def __init__(self, db):
        self.db = db
        self.table = BlogTable

    def printing(self):
        for entry in self.table.query.all():
            print(entry.title)

    def insert(self, title, post_body):
        query = self.table.query.all()
        if len(query) > 0:
            id = query[-1].id + 1
        else:
            id = 0

        date_pos = date.today()
        new_entry = self.table(id, title, date_pos, post_body)  # change to kwargs?
        self.db.session.add(new_entry)
        self.db.session.commit()

    def edit(self, id_num, title, post_body):
        entry = self.table.query.filter_by(id=id_num).first()
        entry.title = str(title)
        entry.post_body = post_body
        self.db.session.commit()

    def delete(self, entry):
        self.db.session.delete(entry)
        self.db.session.commit()


if __name__ == "__main__":
    g = Blog(db, BlogTable)
    g.printing()
    g.insert("dddddddd", "dsdasdfhsduddiohfds dsfdsfg")
    g.printing()
