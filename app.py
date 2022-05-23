from sqlalchemy.ext.declarative import declarative_base
from flask import Flask, render_template, abort, request, redirect, g, session as flasksession, send_file, url_for
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
import requests
# import datetime
# from werkzeug.utils import secure_filename
app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'

app.secret_key = 'paifdshfaphfiapodufh2o83108u230219u32103u2139821uuhfaudoshdf___2137'
# app.config['UPLOAD_FOLDER'] = "static/profilephotos"
# UPLOAD_FOLDER = '/static/profilephotos'
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)
class Ranga(db.Model):
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
     rola = db.Column(db.Integer, db.ForeignKey('ranga.id'), nullable=False, default=0)
     def __init__ (self, name='', password='', rola=1):
          self.name = name
          self.password = password
          self.rola = rola
class Dzial(db.Model):
     id=db.Column(db.Integer, primary_key=True)
     tytul = db.Column(db.String)
     tresc = db.Column(db.String)
     def __init__(self, tytul, tresc):
          self.tytul=tytul
          self.tresc=tresc
     def __repr__(self):
          return self.tytul, self.tresc
class Post(db.Model):
     __tablename__="posty"
     id=db.Column(db.Integer, primary_key=True)
     tytul = db.Column(db.String)
     tresc = db.Column(db.String)
     autorid=db.Column(db.Integer, db.ForeignKey(Urzyszkodnik.id))
     dzialid=db.Column(db.Integer, db.ForeignKey(Dzial.id))
     create_date=db.Column(db.DateTime(timezone=False), server_default=db.func.now())
     # dzialid=db.Column(db.Integer, )
     def __init__(self, tytul, tresc, autorid, dzialid):
          self.tytul=tytul
          self.tresc=tresc
          self.autorid=autorid
          self.dzialid=dzialid
     def __repr__(self):
          return self.id, self.tytul, self.tresc, self.autorid
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

db.create_all()
session = db.session
def sprawdzenierangi(uprawnienie):
     permited=False
     try:
          user=session.query(Urzyszkodnik).filter(Urzyszkodnik.id == flasksession["user_id"]).first().rola
          permissions = session.query(Ranga).filter(Ranga.id == user).first()
          permited=getattr(permissions, str(uprawnienie))
     except:
          None
     return(permited)
def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)

if session.query(Ranga).filter(Ranga.id==1).all() == []:
     adminlogin = input("admin login: ")
     session.add(Ranga("Admin", True, True, True, True))
     password = input("admin password: ")
     session.add(Ranga("Wyciszony", False, False, False, False))
     session.add(Ranga("Normalny użytkownik", True, False, False, False))
     admin = session.query(Ranga).filter(Ranga.name == 'Admin').first()
     session.add(Urzyszkodnik(adminlogin, get_hashed_password(password)), admin.id)
     session.commit()

@app.route("/")
def index():
     dzialy = session.query(Dzial).order_by(Dzial.id).all()
     try:
          login=flasksession["user_name"]
     except:
          login="Not logged in"
     return(render_template('index.html',
     dzialy=dzialy,
     iloscdzialow=int(len(dzialy)),
     login=login,
     usersmanagment=sprawdzenierangi("usersmanagment"),
     postmanagment=sprawdzenierangi("postmanagment"),
     typ="dzial"
     ))
# @app.route("/postmanagment")
@app.route("/add/post", methods = ['POST', 'GET'])
def addpost():
     if sprawdzenierangi("addingpost") == True:
          if request.method == 'POST':
               # tytul, tresc, autorid, dzial
               session.add(Post(request.form['tytul'],
                request.form['trescpostu'],
                 flasksession["user_id"],
                 request.form["dzial"]
                 ))
               print(
               request.form['tytul'],
                request.form['trescpostu'],
                 flasksession["user_id"],
                 request.form["dzial"])
               session.commit()
               return redirect("/")
          elif request.method == 'GET':
               dzialy=session.query(Dzial).order_by(Dzial.id).all()
               return(render_template('dodaj.html', dzialy=dzialy))
     else:
          abort(403)
@app.route("/rejestracja", methods = ['POST', 'GET'])
def rejestruj():
     if request.method == 'POST':
          session.add(Urzyszkodnik(request.form['imie'], get_hashed_password(request.form['password']), 2))
          session.commit()
          return(redirect("/"))
     elif request.method == 'GET':
          return(render_template('rejestracja.html'))
@app.route("/dzial/<postid>")
def dzial(postid):
     autors = []
     posty=session.query(Post).filter(Post.dzialid == postid).all()
     usersmanagment=sprawdzenierangi("usersmanagment")
     postmanagment=sprawdzenierangi('postmanagment')
     try:
          login=flasksession["user_name"]
     except:
          login="Not logged in"
          usersmanagment=False
     for i in posty:
          try:
               autors.append(session.query(Urzyszkodnik).filter(Urzyszkodnik.id == i.autorid).first().name)
          except:
               autors.append("autor nieznany/usunięty")
     return(render_template("index.html",
      dzialy=posty,
      autors=autors,
      login=login,
      usersmanagment=usersmanagment,
      postmanagment=postmanagment,
      iloscdzialow=len(posty),
      dzialid=postid,
      typ="post"
     ))
@app.route("/admin/post/<postid>/remove")
def removepost(postid):
     if sprawdzenierangi("postmanagment"):
          dzial=session.query(Post).order_by(Post.id).filter(Post.id == postid).first().dzialid
          session.delete(session.query(Post).order_by(Post.id).filter(Post.id == postid).first())
          session.commit()
          return redirect(url_for('dzial', postid=dzial))
     else:
          abort(403)
@app.route("/dzial/add", methods=["POST", "GET"])
def adddzial():
     if request.method == "GET":
          return render_template("adddzial.html")
     elif request.method=='POST':
          name = request.form["name"]
          opis = request.form["opis"]
          session.add(Dzial(name, opis))
     return redirect(url_for('index'))
@app.route('/dzial/<dzialid>/remove')
def removedzial(dzialid):
     if sprawdzenierangi("postmanagment"):
          session.delete(session.query(Dzial).filter(Dzial.id==dzialid).first())
          session.query(Post).filter(Post.dzialid == dzialid).delete()
          session.commit()
     return redirect('/')
@app.route("/admin/comment/<commentid>/remove")
def removecomment(commentid):
     if sprawdzenierangi("postmanagment"):
          post = session.query(Comment).filter(Comment.id == commentid).first().postid
          session.delete(session.query(Comment).filter(Comment.id == commentid).first())
          return redirect(url_for('post', postid=post))
     else:
          abort(403)
@app.route("/post/<postid>", methods=["POST", "GET"])
def post(postid):
     if request.method == "GET":
          autors = []
          postt=session.query(Post).filter(Post.id == postid).first()
          try:
               autor=session.query(Urzyszkodnik).filter(Urzyszkodnik.id==postt.autorid).first().name
          except:
               autor="Autor nie dostępny/usunięty"
          try:
               flasksession["user_id"]
               zalogowany=True
          except:
               zalogowany=False
          komentarze=session.query(Comment).filter(Comment.postid == postid).all()
          postmanagment = sprawdzenierangi("postmanagment")
          for i in komentarze:
               autors.append(session.query(Urzyszkodnik).filter(Urzyszkodnik.id == i.autorid).first().name)
          return(render_template("artykul.html",
               autors=autors,
               ilosckomentarzy=len(komentarze),
               postmanagment=postmanagment,
               post=postt,
               zalogowany=zalogowany,
               dzial="",
               autor=autor,
               komentarze=komentarze
          ))
     elif request.method == "POST":
          autorid = flasksession["user_id"]
          komentarz = request.form["komentarz"]
          session.add(Comment(postid, autorid, komentarz))
          session.commit()
          return redirect(request.url)
@app.route("/login", methods = ['POST', 'GET'])
def login():
     if request.method == "POST":
          success=False
          flasksession.pop('user_id', None)
          nick=request.form["nick"]
          password=request.form["password"]
          users = session.query(Urzyszkodnik).filter(Urzyszkodnik.name == nick).all()
          for i in users:
               if i.name == nick and check_password(password, i.password):
                    flasksession['user_id'] = i.id
                    flasksession['user_name'] = i.name
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
     print(int(id)==int(flasksession["user_id"]))
     if int(id) == int(flasksession["user_id"]) or sprawdzenierangi("usersmanagment") == True:
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
          parametry=['addingpost', 'postmanagment' ,'usersmanagment', 'modyfingrules']
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
               session.add(Ranga(name, parametry[0], parametry[1] , parametry[2], parametry[3]))
               session.commit()
               return(redirect("/admin/users"))
     else:
          abort(403)
@app.route("/avatar.jpg")
def profilowka():
     try:
          userid=flasksession["user_id"]
          if str(userid)+".jpg" in os.listdir("static/profilephotos/"):
               return(send_file("static/profilephotos/"+str(userid)+".jpg"))
          else:
               return(send_file("static/profilephotos/default.jpg"))
     except:
          return(send_file("static/profilephotos/default.jpg"))
@app.route("/konto")
def zarzadzaniekontem():
     id=flasksession["user_id"]
     konto=session.query(Urzyszkodnik).filter(Urzyszkodnik.id == id).first()
     rola=session.query(Ranga).filter(Ranga.id==konto.rola).first().name
     return(render_template("konto.html", konto=konto))
@app.route('/konto/profilephoto', methods=['POST', 'GET'])
def changeprofilephoto():
     f=request.files.get("file")
     print(':*:*:*:*:*:', f)
     f.save('static/profilephotos/'+str(flasksession["user_id"])+'.jpg')
     return(redirect("/konto"))
app.run(host="0.0.0.0", port="8080")