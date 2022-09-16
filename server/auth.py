from flask import Blueprint, render_template, redirect, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user

from . import db, login_manager
from .models import User
from .helper import no_login

auth = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@auth.route("/signup")
@no_login
def signup():
    return render_template("signup.jinja")

@auth.route("/signup", methods=['POST'])
def signup_post():
    
    form = request.form
    email = form.get('email')
    
    if not email:
        flash("Enter a valid email address")
        return redirect(url_for("auth.signup"))
    
    user = User.query.filter_by(email=form['email']).first()
    
    if user:
        flash(f"Email address already in use. Login to your account at <a href={url_for('auth.login')}>login page</a>")
        return redirect(url_for('auth.signup'))
    
    if form['password'] != form['passwordRepeat']:
        flash("Passwords do not match")
        return redirect(url_for('auth.signup'))
    
    password = generate_password_hash(form['password'], method="sha256")
    # ip = request.remote_addr
    # response = urlopen(f"https://ipinfo.io/{ip}/json")
    # data = json.load(response)
        
    newUser = User(email=form['email'], username=form['username'], password=password, country='test')
    
    db.session.add(newUser)
    db.session.commit()
    
    return redirect(url_for('auth.login'))


@auth.route("/login")
@no_login
def login():
    return render_template('login.jinja')

@auth.route("/login", methods=['POST'])
def login_post():
    
    email = request.form.get('email')
    password = request.form.get('password')    
    
    user = User.query.filter_by(email=email).first()
    remember = bool(request.form.get('remember'))
    
    if user and check_password_hash(user.password, password):
        login_user(user, remember=remember)
        return redirect('/')
    elif not user:
        string = f"Email address not in use. Make an account at <a href={url_for('auth.signup')}>signup page</a>"
        flash(string)
    else:
        flash("Please check your user account details and try again")

    
    return redirect(url_for('auth.login'))
