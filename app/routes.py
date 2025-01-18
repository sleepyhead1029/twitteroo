from flask import Blueprint,render_template, url_for, flash, redirect,request, abort
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt, cache
from app.models import User, Tweet
from app.forms import RegistrationForm, ProfileForm,LoginForm, TweetForm

#Creating of Blueprint
routes = Blueprint('routes', __name__)

def displayTweet():
    displayTweet = Tweet.query.all()
    return displayTweet

def displayUser():
    displayUser = User.query.all()
    return displayUser

@routes.route("/")
@routes.route("/home")
def home():
    tweet = Tweet.query.all()
    return render_template('home.html',tweet=tweet)

#Registration
@routes.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)

        print(user.username, user.email, user.password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created!', 'success')
            return redirect(url_for('routes.login'))
        except Exception as e:
            print(f"Error: {e}")
            flash('An error occurred while saving to the database.', 'danger')
    else:
        if form.errors:
            print(f"Form Errors: {form.errors}")  

    return render_template('register.html', title='Register',form=form)

#Login
@routes.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.new_tweet'))
    
    form = LoginForm()
    print("Rendering login form.")
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('routes.login'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form, cache=cache)

#View Profile
@routes.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        try:
            db.session.commit()
            flash("Your profile has been updated!", "success")
            return redirect(url_for('routes.profile'))
        except Exception as e:
            print(f"Error: {e}")
            flash('An error occurred while updating the database.', 'danger')
            return redirect(url_for('routes.profile'))
        
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("profile.html", title="Profile", form=form)

#Logout
@routes.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('routes.login'))

#New Tweet
@routes.route("/tweet/new", methods=['GET','POST'])
@login_required
def new_tweet():
    form = TweetForm()
    if form.validate_on_submit():
        tweet = Tweet(content=form.content.data, author=current_user)
        db.session.add(tweet)
        db.session.commit()
        flash('Your tweet has been created!', 'success')
        return redirect(url_for('routes.login'))
    return render_template('tweet.html', title='New Tweet', form=form)

#Update Tweet
@routes.route("/update/<int:tweet_id>", methods=['GET','POST'])
@login_required
def update_tweet(tweet_id):
    tweet = Tweet.query.get_or_404(tweet_id)
    if tweet.author != current_user:
        abort(403)
    form = TweetForm()
    if form.validate_on_submit():
        tweet.content = form.content.data
        db.session.commit()
        flash('Your tweet has been updated!', 'success')
        return redirect(url_for('routes.home'))
    elif request.method == 'GET':
        form.content.data = tweet.content
    return render_template('tweet.html', title='Update Tweet', form=form)
    

#Search
@routes.route("/search", methods=['GET'])
def search():
    query = request.args.get('query','').strip()
    if not query:
        flash('Please enter a search term.', 'warning')
        return redirect(url_for('routes.home'))
    
    results = Tweet.query.filter(Tweet.content.ilike(f"%{query}")).all()
    return render_template('search_results.html', results=results, query=query)

@routes.route('/test_flash')
def test_flash():
    flash('This is a test flash message.', 'success')
    return render_template('base.html')