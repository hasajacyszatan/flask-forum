from __main__ import *

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
db = SQLAlchemy(app)
class Rank(db.Model):
     id = db.Column(db.Integer(), primary_key=True)
     name = db.Column(db.String, unique=True)
     addingpost = db.Column(db.Boolean)
     postmanagment = db.Column(db.Boolean)
     usersmanagment = db.Column(db.Boolean)
     modyfingrules = db.Column(db.Boolean)
     users = db.relationship('Urzyszkodnik', lazy=True)
     def __init__(self, name, addingpost, postmanagment, usersmanagment, modyfingrules):
          self.name = name
          self.addingpost = addingpost
          self.postmanagment = postmanagment
          self.usersmanagment = usersmanagment
          self.modyfingrules = modyfingrules
          # self.postmanagment = postmanagment
     def __repr__(self):
          return(self.id, self.name, self.addingpost, self.usersmanagment, self.modyfingrules)
class Urzyszkodnik(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     name = db.Column(db.String, unique=True)
     password = db.Column(db.String, nullable=False)
     rola = db.Column(db.Integer, db.ForeignKey('rank.id'))
     def __init__ (self, name='', password='', rola=1):
          self.name = name
          self.password = password
          self.rola = rola
class Section(db.Model):
     id=db.Column(db.Integer, primary_key=True)
     title = db.Column(db.String)
     description = db.Column(db.String)
     posts = db.relationship('Post', lazy=True)
     def __init__(self, title, description):
          self.description=description
          self.title=title
class Post(db.Model):
     id=db.Column(db.Integer, primary_key=True)
     title = db.Column(db.String)
     content = db.Column(db.String)
     autorid=db.Column(db.Integer, db.ForeignKey(Urzyszkodnik.id))
     create_date=db.Column(db.DateTime(timezone=False), server_default=db.func.now())
     section = db.Column(db.Integer(), db.ForeignKey('section.id'))
class Comment(db.Model):
     __tablename__="comments"
     id = db.Column(db.Integer, primary_key=True)
     postid = db.Column(db.Integer)
     autorid= db.Column(db.Integer, db.ForeignKey(Urzyszkodnik.id))
     comment = db.Column(db.String)
     def __init__(self, postid, autorid, comment):
          self.postid = postid
          self.autorid=autorid
          self.comment= comment
user = Urzyszkodnik()
db.create_all()
session = db.session
