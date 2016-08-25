from flask import Flask, render_template, request, url_for, redirect
from flask_login import LoginManager, login_required, login_user, logout_user
from flask_wtf import Form
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from steamapi import core, user
import pprint

pp = pprint.PrettyPrinter()


steam_api_key = "ED778FC40C97C2904BFE3E0BE402ACBD"
core.APIConnection(api_key=steam_api_key)
app = Flask(__name__)
app.config['SECRET_KEY'] = "thisisoursecretkey"

# db = MongoClient("mongodb://khgaming:KnuckleHeads1994@ds040349.mlab.com:40349/khgaming")
db = MongoClient()["khg"]["users"]
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
Bootstrap(app)


class User():
    def __init__(self, username):
        self.username = username
        self.email = None

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(Form):
    first_name = StringField('first_name', validators=[DataRequired()])
    last_name = StringField('last_name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

    psn = StringField('psn')
    steam_id = IntegerField('steam_id')
    youtube = StringField('youtube')
    twitch = StringField('twitch')

@app.route('/')
@app.route('/index')
def index():
    steam_user = user.SteamUser(userurl="bhaanuroo")
    print steam_user
    return render_template('index.html', title="KHGaming")


@app.route('/members/<username>', methods=['GET'])
def members(username):
    user = db.find_one({"_id": username})
    print user
    member = dict()
    member['name'] = username
    return render_template('member.html', member=member)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = db.find_one({"_id": form.username.data})
        if user and User.validate_login(user['password'], form.password.data):
            user_obj = User(user['_id'])
            login_user(user_obj)
            return redirect(request.args.get("next") or url_for("edit"))
    return render_template('login.html', title="Member Login", form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and not form.validate_on_submit():
        print form.errors
    if request.method == 'POST' and form.validate_on_submit():
        new_member = {
            'first_name': form.first_name.data,
            'last_name': form.last_name.data,
            'username': form.username.data,
            'password':generate_password_hash(form.password.data, method='pbkdf2:sha256'),
            'psn': form.psn.data,
            'steam_id': form.steam_id.data,
            'youtube': form.youtube.data,
            'twitch': form.twitch.data
        }
        db.insert_one(new_member)
    return render_template('register.html', form=form)
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/edit')
@login_required
def edit():
    return render_template('edit.html')


@login_manager.user_loader
def load_user(username):
    u = db.find_one({"_id": username})
    if not u:
        return None
    return User(u["_id"])


if __name__ == '__main__':
    app.run(port=5003)
