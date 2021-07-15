from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, Integer, String, desc, update, create_engine, ForeignKey
from flask import Flask, render_template, abort, request, redirect, g, session as flasksession
import bcrypt
import os
app = Flask(__name__, static_folder='static')
app.secret_key = 'SECRET_KEY'
posty=dict()
autors=list()
Base = declarative_base()

# flasksession["user_id"] = None
# flasksession["user_name"] = "Nie zalogowany"
class Ranga(Base):
     __tablename__="rangi"
     id = Column(Integer(), primary_key=True)
     name = Column(String, unique=True)
     addingpost = Column(Boolean)
     usersmanagment = Column(Boolean)
     modyfingrules = Column(Boolean)
     def __init__(self, name, addingpost, usersmanagment, modyfingrules):
          self.name = name
          self.addingpost = addingpost
          self.usersmanagment = usersmanagment
          self.modyfingrules = modyfingrules
     def __repr__(self):
          return(self.id, self.name, self.addingpost, self.usersmanagment, self.modyfingrules)
class Urzyszkodnik(Base):
     __tablename__='urzyszkodniki'
     id = Column(Integer, primary_key=True)
     name = Column(String, unique=True)
     password = Column(String, nullable=False)
     rola = Column(Integer, nullable=False, default=0)
     def __init__(self, id, name, password, rola):
          self.id = id
          self.name = name
          self.password=password
          self.rola=rola
     def __repr__(self):
          return self.id, self.name, self.password, self.rola
class Post(Base):
     __tablename__="posty"
     id=Column(Integer, primary_key=True)
     tytul = Column(String)
     tresc = Column(String)
     autorid=Column(Integer, ForeignKey(Urzyszkodnik.id))
     dzial=Column(Integer, ForeignKey(Dzial.id))
     # dzialid=Column(Integer, )
     def __init__(self, tytul, tresc, autorid):
          self.tytul=tytul
          self.tresc=tresc
          self.autorid=autorid

     def __repr__(self):
          return self.id, self.tytul, self.tresc, self.autorid

class Dzial(Base):
     __tablename__="dzialy"
     id=Column(Integer, primary_key=True)
     tytul = Column(String)
     opis = Column(String)
     def __init__(self, tytul, opis):
          self.tytul=tytul
          self.opis=opis
     def __repr__(self):
          return self.tytul, self.opis


engine = create_engine('sqlite:///base.db', echo=True,
     connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
def sprawdzenierangi(uprawnienie):
     rola=session.query(Urzyszkodnik).filter(Urzyszkodnik.id == flasksession["user_id"]).first().rola
     permited=getattr(session.query(Ranga).filter(Ranga.id == rola).first(), str(uprawnienie))
     print( session.query(Urzyszkodnik).filter(Urzyszkodnik.id == flasksession["user_id"]).first().name,rola  )
     return(permited)
def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())
def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)

if session.query(Ranga).filter(Ranga.id==1).all() == []:
     session.add(Ranga("Wyciszony", False, False, False))
     session.add(Ranga("Normalny użytkownik", True, False, False))
     session.add(Ranga("Admin", True, True, True))
     session.add(Urzyszkodnik(0 ,"Administrator", get_hashed_password("tajnehaslo123"), 3))
     session.commit()

@app.route("/")
def index():
     for i in session.query(Post).order_by(Post.id).all():
          try:
               posty[i.id]=session.query(Urzyszkodnik).order_by(Urzyszkodnik.id).filter(Urzyszkodnik.id==i.autorid).first().name
          except:
               posty[i.id]="konto niedostępne/usunięte"
     for i in session.query(Post).order_by(Post.id).all():
          posty[i.id]=posty[i.id], i.tytul, i.tresc[0:23]
     try:
          usersmanagment=sprawdzenierangi("usersmanagment")
          login=flasksession["user_name"]
     except:
          usersmanagment=False
          login="Nie zalogowany"
     return(render_template('index.html',
     posty=posty,
     iloscpostow=len(posty),
     login=login,
     usersmanagment=usersmanagment
     ))
@app.route("/dodaj", methods = ['POST', 'GET'])
def dodaj():
     if sprawdzenierangi("addingpost") == True:
          if request.method == 'POST':
               session.add(Post(request.form['tytul'], request.form['trescpostu'], autorid=flasksession["user_id"]))
               session.commit()
               return redirect("/")
          elif request.method == 'GET':
               return render_template("dodaj.html")
     else:
          abort(403)
@app.route("/rejestracja", methods = ['POST', 'GET'])
def rejestruj():
     if request.method == 'POST':
          nextid=session.query(Urzyszkodnik).order_by(Urzyszkodnik.id.desc()).first().id
          session.add(Urzyszkodnik(int(nextid)+1 ,request.form['imie'], get_hashed_password(request.form['password']), 2))
          session.commit()
          return(redirect("/"))
     elif request.method == 'GET':
          return(render_template('rejestracja.html'))
@app.route("/<postid>")
def post(postid):
     autorid=session.query(Post).filter(Post.id==postid).first().autorid
     try:
          autorname=session.query(Urzyszkodnik).order_by(Urzyszkodnik.id).filter(Urzyszkodnik.id==autorid).first().name
     except:
          autorname="konto niedostępne/usunięte"
     return(render_template("artykul.html",
     tresc=session.query(Post).filter(Post.id==postid).first().tresc,
      tytul=session.query(Post).filter(Post.id==postid).first().tytul,
       autor=autorname
       ))
@app.route("/login", methods = ['POST', 'GET'])
def login():
     if request.method == "POST":
          success=False
          flasksession.pop('user_id', None)
          nick=request.form["nick"]
          password=request.form["password"]
          urzyszkodniki=session.query(Urzyszkodnik).order_by(Urzyszkodnik.id).all()
          for i in range(len(urzyszkodniki)):
               if urzyszkodniki[i].name == nick and check_password(password, urzyszkodniki[i].password):
                    flasksession['user_id'] = i
                    flasksession['user_name'] = urzyszkodniki[i].name
                    print("Udało się zalogować")
                    success=True
          if success:
               return(redirect("/"))
          else:
               return("failed")
     elif request.method == "GET":
          return(render_template("login.html")) 
@app.route("/logout")
def logout():
     flasksession.pop("user_id", None)
     flasksession.pop("user_name", None)
     return redirect("/")
@app.route("/admin/users")
def zarzadzanieurzytkonikami():
     if sprawdzenierangi("usersmanagment") == True:
          users=session.query(Urzyszkodnik).order_by(Urzyszkodnik.id).all()
          rangi=session.query(Ranga).order_by(Ranga.id).all()
          return render_template("usersmanagement.html", users=users, rangi = rangi)
     else:
          abort(403)
@app.route("/admin/users/<id>/remove")
def removeuser(id):
     if sprawdzenierangi("usersmanagment") == True or id == flasksession["user_id"]:
          session.delete(session.query(Urzyszkodnik).order_by(Urzyszkodnik.id).filter(Urzyszkodnik.id == id).first())
          session.commit()
          return(redirect("/admin/users"))
     else:
          abort(403)
@app.route("/admin/users/<id>/manage", methods = ['POST', 'GET'])
def manage(id):
     if sprawdzenierangi("usersmanagment") == True:
          if request.method == "GET":
               rangi=session.query(Ranga).order_by(Ranga.id).all()
               username=session.query(Urzyszkodnik).order_by(Urzyszkodnik.id).filter(Urzyszkodnik.id == id).first().name
               return(render_template("usermanage.html",
               user=username,
               rangi=rangi)
               )
          elif request.method == "POST":
               # id, name, password, rola
               rola=request.form["rola"]
               roleid=session.query(Ranga).order_by(Ranga.id).filter(Ranga.name == request.form["rola"]).first().id
               session.query(Urzyszkodnik).filter(Urzyszkodnik.id == id).\
               update({Urzyszkodnik.rola: roleid}, synchronize_session = False)
               session.commit()
               return(redirect("/admin/users"))
     else:
          abort(403)
@app.route("/admin/users/role/add", methods = ['POST', 'GET'])
def dodajrole():
     if sprawdzenierangi("modyfingrules") == True:
          parametry=['addingpost', 'usersmanagment', 'modyfingrules']
          if request.method == "GET":
               return(render_template("addrole.html"))
          elif request.method == "POST":
               for i in range(len(parametry)):
                    try:
                         if request.form[parametry[i]] == "on":
                              parametry[i] = bool(True)
                    except:
                         parametry[i] = bool(False)
               name = request.form["name"]
               print(parametry)
               session.add(Ranga(name, parametry[0], parametry[1], parametry[2]))
               session.commit()
               return(redirect("/admin/users"))
     else:
          abort(403)
app.run(host="0.0.0.0", port="8080")