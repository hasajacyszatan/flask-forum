from flask import Flask, render_template, abort, request, redirect, g, session as flasksession, send_file, url_for
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import os
import requests
from flaskext.markdown import Markdown

# import datetime
# from werkzeug.utils import secure_filename
app = Flask(__name__, static_folder='static')
Markdown(app)
app.secret_key = 'paifdshfaphfiapodufh2o83108u230219u32103u2139821uuhfaudoshdf___2137'
from base import *

@app.context_processor
def inject_dict_for_all_templates():
     try:
          user = session.query(Urzyszkodnik).filter(Urzyszkodnik.id==flasksession['user_id']).first()
          return dict(user = user, len=len, range=range)
     except:
          user = Urzyszkodnik('niezalogowany','',1)
          return dict(user = user, len=len, range=range)
def sprawdzenierangi(uprawnienie):
     permited=False
     try:
          user=session.query(Urzyszkodnik).filter(Urzyszkodnik.id == flasksession["user_id"]).first().rola
          permissions = session.query(Rank).filter(Rank.id == user).first()
          permited=getattr(permissions, str(uprawnienie))
     except:
          None
     return(permited)
def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)

if session.query(Rank).filter(Rank.id==1).all() == []:
     adminlogin = input("admin login: ")
     session.add(Rank("Admin", True, True, True, True))
     password = input("admin password: ")
     session.add(Rank("Wyciszony", False, False, False, False))
     session.add(Rank("Normalny użytkownik", True, False, False, False))
     admin = session.query(Rank).filter(Rank.name == 'Admin').first()
     session.add(Urzyszkodnik(adminlogin, get_hashed_password(password)), admin.id)
     session.commit()

@app.route("/")
def index():
     sections = session.query(Section).order_by(Section.id).all()
     try:
          login=flasksession["user_name"]
     except:
          login="Not logged in"
     return(render_template('posts/sections.html',
     sections=sections,
     iloscdzialow=int(len(sections)),
     login=login,
     usersmanagment=sprawdzenierangi("usersmanagment"),
     postmanagment=sprawdzenierangi("postmanagment"),
     urlfor="section",
     autors = []
     ))
# @app.route("/postmanagment")
@app.route("/add/post", methods = ['POST', 'GET'])
def addpost():
     if sprawdzenierangi("addingpost") == True:
          if request.method == 'POST':
               # tytul, tresc, autorid, section
               session.add(Post(
                    title = request.form['title'],
                    content = request.form['content'],
                    autorid = flasksession["user_id"],
                    section = request.form["section"]
                 ))
               session.commit()
               return redirect("/")
          elif request.method == 'GET':
               dzialy=session.query(Section).order_by(Section.id).all()
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
@app.route("/section/<postid>")
def section(postid):
     autors = []
     posts=session.query(Section).filter(Section.id == postid).first().posts
     usersmanagment=sprawdzenierangi("usersmanagment")
     postmanagment=sprawdzenierangi('postmanagment')
     try:
          login=flasksession["user_name"]
     except:
          login="Not logged in"
          usersmanagment=False
     for i in posts:
          try:
               autors.append(session.query(Urzyszkodnik).filter(Urzyszkodnik.id == i.autorid).first().name)
          except:
               autors.append("autor nieznany/usunięty")
     return(render_template("posts/posts.html",
      posts=posts,
      autors=autors,
      login=login,
      usersmanagment=usersmanagment,
      postmanagment=postmanagment,
      iloscdzialow=len(posts),
      dzialid=postid,
     ))
@app.route("/admin/post/<postid>/remove")
def removepost(postid):
     if sprawdzenierangi("postmanagment"):
          post=session.query(Post).order_by(Post.id).filter(Post.id == postid).first()
          session.delete(post)
          session.commit()
          return redirect(url_for('section', postid=post.section))
     else:
          abort(403)
@app.route("/section/add", methods=["POST", "GET"])
def adddzial():
     if request.method == "GET":
          return render_template("adddzial.html")
     elif request.method=='POST':
          title = request.form.get("title")
          description = request.form.get("description")
          print(title, description)
          session.add(Section(
               title=title, 
               description=description
          ))
          session.commit()
     return redirect(url_for('index'))
@app.route('/section/<dzialid>/remove')
def removedzial(dzialid):
     if sprawdzenierangi("postmanagment"):
          sekcja = session.query(Section).filter(Section.id == dzialid).first()
          session.delete(sekcja.posts)
          session.delete(sekcja)
          session.commit()
     return redirect('/')
@app.route("/admin/comment/<commentid>/remove")
def removecomment(commentid):
     if sprawdzenierangi("postmanagment"):
          post = session.query(Comment).filter(Comment.id == commentid).first().postid
          session.delete(session.query(Comment).filter(Comment.id == commentid).first())
          session.commit()
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
          return(render_template("posts/post.html",
               autors=autors,
               ilosckomentarzy=len(komentarze),
               postmanagment=postmanagment,
               post=postt,
               zalogowany=zalogowany,
               section="",
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
          rangi=session.query(Rank).order_by(Rank.id).all()
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
               rangi=session.query(Rank).order_by(Rank.id).all()
               username=session.query(Urzyszkodnik).order_by(Urzyszkodnik.id).filter(Urzyszkodnik.id == id).first().name
               return(render_template("users/usermanage.html",
               user=username,
               rangi=rangi)
               )
          elif request.method == "POST":
               # id, name, password, rola
               rola=request.form["rola"]
               roleid=session.query(Rank).order_by(Rank.id).filter(Rank.name == request.form["rola"]).first().id
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
               session.add(Rank(name, parametry[0], parametry[1] , parametry[2], parametry[3]))
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
     rola=session.query(Rank).filter(Rank.id==konto.rola).first().name
     return(render_template("konto.html"))
@app.route('/konto/profilephoto', methods=['POST', 'GET'])
def changeprofilephoto():
     f=request.files.get("file")
     print(':*:*:*:*:*:', f)
     f.save('static/profilephotos/'+str(flasksession["user_id"])+'.jpg')
     return(redirect("/konto"))
app.run(host="0.0.0.0", port="8080")