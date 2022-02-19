from flask import Flask, render_template, request, flash, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "laon!82ne#$19=-1!"
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

db.create_all()


@login_manager.user_loader
def load_user(i_d):
    return users.query.get(int(i_d))


class users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(500))
    username = db.Column(db.String(500))
    password = db.Column(db.String(500))
    bio = db.Column(db.String(500))
    public_url = db.Column(db.String(500))

    def __init__(self, email, username, password, bio, public_url):
        self.email = email
        self.username = username
        self.password = generate_password_hash(password)
        self.bio = bio
        self.public_url = public_url

    def verify_password(self, password_in):
        return check_password_hash(self.password, password_in)


class urls(db.Model):
    url_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(500))
    url_name = db.Column(db.String(500))
    url = db.Column(db.String(500))

    def __init__(self, email, url_name, url):
        self.email = email
        self.url_name = url_name
        self.url = url


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/read_mode/<name>', methods=['GET', 'POST'])
def read_mode(name):
    print("Yha aagya")
    user_data = users.query.filter_by(public_url=name).one()
    data = urls.query.filter_by(email=user_data.email).all()
    userName = users.query.filter_by(email=user_data.email).one().username
    return render_template('user/view_url.html', data=data, username=userName)


@app.route('/SignUp', methods=['GET', 'POST'])
def SignUp():
    if current_user.is_authenticated:
        return redirect('/user')
    else:
        if request.method == 'POST':
            username = request.form['UserName']
            email = request.form['Email']
            password = request.form['Password']
            bio = request.form['Bio']
            usr = users.query.filter_by(email=email).first()
            if usr:
                flash('This email id already exists. Please try with some other email id')
                return redirect('/SignIn')

            usr = users(email, username, password, bio, email)

            db.session.add(usr)
            db.session.commit()
            return redirect('/user')

        return render_template('register.html')


@app.route('/SignIn', methods=['GET', 'POST'])
def SignIn():
    if not current_user.is_authenticated:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            usr = users.query.filter_by(email=email).first()

            if usr != None:
                if usr.verify_password(password):
                    login_user(usr)
                    return redirect('/user')

            flash('Please check your login details and try again!')
            return redirect('/SignIn')

        return render_template('Signin.html')
    else:
        return redirect('/user')


@app.route('/LogOut')
def LogOut():
    if current_user.is_authenticated:
        logout_user()
        return redirect('/')
    else:
        return redirect('/SignIn')


@app.route('/user')
def user():
    if current_user.is_authenticated:
        email = current_user.email
        user_data = users.query.filter_by(email=email).one()
        data = urls.query.filter_by(email=email).all()

        print(data)
        print(user_data)
        print(email)
        return render_template('user/home.html', data=data, user=user_data)
    return redirect('/SignIn')


@app.route('/Edit_Profile')
def Edit_Profile():
    if current_user.is_authenticated:
        if request.method == "POST":
            email = current_user.email

            name = request.form['username']
            password = request.form['password']
            bio = request.form['bio']
            public_url = request.form['public_url']

            users.query.filter_by(email=current_user.email).update(
                {'email': email, 'username': name, 'password': password, 'bio': bio, 'public_url': public_url})
            db.session.commit()

        return redirect('/user')


@app.route('/add_url', methods=['GET', 'POST'])
def add_url():
    if current_user.is_authenticated:
        if request.method == "POST":
            email = current_user.email
            urlName = request.form['urlN']
            urlLink = request.form['urlL']
            newurl = urls(email, urlName, urlLink)
            db.session.add(newurl)
            db.session.commit()

            return redirect('/user')

        return render_template('user/addUrl.html')
    return redirect('/SignIn')


@app.route('/edit/<int:url_id>', methods=['GET', 'POST'])
def edit(url_id):
    if current_user.is_authenticated:
        email = current_user.email
        data = urls.query.filter_by(email=email, url_id=url_id).all()
        print(data[0].url + " " + data[0].url_name)
        if request.method == "POST":
            urlName = request.form['urlN']
            urlLink = request.form['urlL']
            urls.query.filter_by(url_id=url_id).update({'url_name': urlName, 'url': urlLink, 'email': email})
            db.session.commit()
            return redirect('/user')

        return render_template('user/editUrl.html', data=data[0])
    return redirect('/SignIn')


@app.route('/deleteUrl/<int:url_id>')
def deleteUrl(url_id):
    if current_user.is_authenticated:
        urls.query.filter_by(url_id=url_id).delete()
        db.session.commit()
        return redirect('/user')
    return redirect('/SignIn')


@app.route('/info')
def info():
    if current_user.is_authenticated:
        email = current_user.email
        leng = len(urls.query.filter_by(email=email).all())
        data = users.query.filter_by(email=email).one()
        return render_template('user/view_profile.html', totalURL=leng, user=data)

    return redirect('/Login')


@app.route('/info_change', methods=['GET', 'POST'])
def info_change():
    if current_user.is_authenticated:
        if request.method == "POST":
            email = current_user.email
            name = request.form['username']
            password = request.form['password']
            about = request.form['bio']
            public_url = request.form['public_url']
            users.query.filter_by(email=email).update({'email':email, 'username':name, 'password':password, 'bio':about, 'public_url':public_url})
            db.session.commit()
            return redirect('/user')

        email = current_user.email
        data = users.query.filter_by(email=email).one()
        print(data)
        return render_template('user/edit_profile.html', data=data)

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
