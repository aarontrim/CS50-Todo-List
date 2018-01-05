import os
from flask import Flask, jsonify, render_template, request, url_for, redirect, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
# Flask initalisation
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

# import database - needs to be done AFTER inialising Flask
from models import db, User, Item


# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for('login'))
    else:
        return render_template("index.html", Item=Item, userid=session.get("user_id"), func=func)

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # do login
        user = User.query.filter_by(name=request.form.get("email")).first()
        if user:
            if check_password_hash(user.password, request.form.get("password")):
                session['user_id'] = user.id
                return redirect(url_for("index"))
            else:
                flash("Invalid password!")
                return redirect(url_for("login"))
        else:
            flash("Invalid email address")
            return redirect(url_for("login"))
    else:
        # show login page
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        # register user
        if len(request.form.get("email")) > 0 and len(request.form.get("password")) > 0 and len(request.form.get("confirm")) > 0 and request.form.get("password") == request.form.get("confirm"):
            newuser = User(name=request.form.get("email"), password=generate_password_hash(request.form.get("password")))
            if User.query.filter_by(name=newuser.name).count() == 0:
                db.session.add(newuser)
                db.session.commit()
                flash("Successfully registered!")
                return redirect(url_for("login"))
            else:
                flash("Username already exists!")
                return redirect(url_for("register")) 
        else:
            flash("Passwords do not match!")
            return redirect(url_for("register"))
    else:
        # show registration page
        return render_template("register.html")

@app.route("/edititem", methods=["POST", "GET"])
def edit_item():
    userid = session.get('user_id', False)
    if userid:    
        if request.method == "POST":
            text = request.form.get('text', False)
            id = request.form.get('id', False)
            if text and id:
                try:
                    item = Item.query.filter_by(id=id)[0]
                except IndexError:
                    return abort(501)

                item.text = text
                db.session.commit()

                # success - return the updated text value
                return text
            else:
                # invalid request - return 'not yet implemented'
                abort(501)
        else:
            # shouldn't be here on a GET request, lets hide ;)
            abort(404)
    else:
        # not logged in so get lost
        abort(404)

@app.route("/additem", methods=["POST", "GET"])
def add_item():
    userid = session.get('user_id', False)
    if userid:
        if request.method == "POST":            
            parentid = request.form.get('parentid', -1)

            try:
                parentid = int(parentid)
            except ValueError:
                abort(501)

            if parentid > 0:
                # not a top-level node
                try:
                    rank = Item.query.session.query(func.max(Item.rank)).filter_by(parentid=parentid).first()[0] + 1
                except TypeError:
                    # when the parent has no children
                    rank = 0
                item = Item(userid=userid, parentid=parentid, text="", rank=rank)
            elif parentid == 0:
                # is a top-level node
                try:
                    rank = Item.query.session.query(func.max(Item.rank)).filter_by(parentid=None).first()[0] + 1
                except TypeError:
                    # when the parent has no children
                    rank = 0
                item = Item(userid=userid, parentid=None, text="", rank=rank)
            else:
                # invalid request - return 'not yet implemented'
                abort(501)

            db.session.add(item)
            db.session.commit()
            #success - return the new id
            return str(item.id)
        else:
            # shouldn't be here on a GET request, lets hide ;)
            abort(404)
    else:
        # not logged in so get lost
        abort(404)

@app.route("/delitem", methods=["POST", "GET"])
def del_item():
    userid = session.get('user_id', False)
    if userid:
        if request.method == "POST":
            id = request.form.get('id', False)

            if id:
                item = Item.query.filter_by(id=id,userid=userid).first()
                if item:
                    db.session.delete(item)
                    db.session.commit()
                else:
                    abort(501)

                return str(id)
            else:
                # invalid request - return 'not yet implemented'
                abort(501)
        else:
            abort(404)
    else:
        # not logged in so get lost
        abort(404)

@app.route("/upitem", methods=["POST", "GET"])
def up_item():
    userid = session.get('user_id', False)
    if userid:
        if request.method == "POST":
            id = int(request.form.get('id', -1))
            parentid = int(request.form.get('parentid', -1))

            if id >= 0 and parentid >= 0:
                if parentid == 0:
                    parentid = None
                item = Item.query.filter_by(id=id, userid=userid).first()
                if item:
                    upitem = Item.query.filter_by(userid=userid, parentid=parentid, rank=item.rank - 1).first()
                    if upitem:
                        # swap the ranks, if there doesn't exist one above just do nothing
                        rank = item.rank
                        item.rank = upitem.rank
                        upitem.rank = rank
                        db.session.commit()
                        return "#text_%s" % upitem.id
                    else:
                        return ""
                else:
                    abort(501)
            else:
                # invalid request - return 'not yet implemented'
                abort(501)
        else:
            abort(404)
    else:
        # not logged in so get lost
        abort(404)

@app.route("/downitem", methods=["POST", "GET"])
def down_item():
    userid = session.get('user_id', False)
    if userid:
        if request.method == "POST":
            id = int(request.form.get('id', -1))
            parentid = int(request.form.get('parentid', -1))

            if id >= 0 and parentid >= 0:
                if parentid == 0:
                    parentid = None
                item = Item.query.filter_by(id=id, userid=userid).first()
                if item:
                    upitem = Item.query.filter_by(userid=userid, parentid=parentid, rank=item.rank + 1).first()
                    if upitem:
                        # swap the ranks, if there doesn't exist one below just do nothing
                        rank = item.rank
                        item.rank = upitem.rank
                        upitem.rank = rank
                        db.session.commit()
                        return "#text_%s" % upitem.id
                    else:
                        return ""
                else:
                    abort(501)
            else:
                # invalid request - return 'not yet implemented'
                abort(501)
        else:
            abort(404)
    else:
        # not logged in so get lost
        abort(404)
