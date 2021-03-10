from flask import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

email=None
app = Flask(__name__, template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
db = SQLAlchemy(app)

class Database(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(50), nullable=False)
    short_bio = db.Column(db.String(300), nullable=False)
    member_type = db.Column(db.String(50), nullable=False)
    profile_pic = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.now(pytz.timezone('Asia/Kolkata')))

    def __repr__(self):
        return '<Account %r>' %self.id

class MatchDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    reciever = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default = datetime.now(pytz.timezone('Asia/Kolkata')))
    accept = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return '<Match %r>' %self.id


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    global email
    if request.method == 'POST':
        if request.form['email'] and request.form['password']:
            query = Database.query.filter_by(email = request.form['email']).first()
            if query is None:
                error = 'Invalid Credentials. Please try again.'
            elif request.form['email'] == query.email and request.form['password'] == query.password:
                email=query.email
                return redirect('/dashboard')
            else:
                error = 'Invalid Credentials. Please try again.'
        else:
            error = 'Enter your E-mail and Password'
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET','POST'])
def signup():
    error = None
    if request.method == 'POST':
        query = Database.query.filter_by(email = request.form['email']).first()
        if query is None:
            temp_name=request.form['name']
            temp_email=request.form['email']
            temp_password=request.form['password']
            temp_disp=request.form['display_name']
            temp_shortbio=request.form['shortbio']
            temp_mt=request.form['member_type']
            temp_profilepic=request.form['profile_pic']
            new_acc = Database(name=temp_name,  email=temp_email, password=temp_password, display_name=temp_disp, short_bio=temp_shortbio, member_type=temp_mt, profile_pic=temp_profilepic)
            try:
                db.session.add(new_acc)
                db.session.commit()
                return redirect('/')
            except:
                error='Cannot sign up!'
        else:
            error = 'Account already exists!'       
    return render_template('signup.html', error=error)

@app.route('/dashboard')
def dashboard():
    global email
    query = Database.query.filter_by(email = email).first()
    if query is not None:
        tasks = Database.query.order_by(Database.id).all()
        return render_template('dashboard.html', email=query.email, disp = query.display_name, items=tasks)
    else:
        return 'Illegal Access!'

@app.route('/logout')
def logout():
    email=None
    return redirect('/')

@app.route('/match', methods=['POST'])
def match():
    global email
    query = Database.query.filter_by(email = email).first()
    tasks = Database.query.order_by(Database.id).all()
    error=None
    match_from=email
    match_to=request.form['match']
    new_match=MatchDB(sender=match_from, reciever=match_to)
    try:
        db.session.add(new_match)
        db.session.commit()
    except:
        error='Cannot Match!'
    return render_template('dashboard.html',error=error, disp = query.display_name, items=tasks)

@app.route('/viewmatches')
def viewmatch():
    global email
    error=None
    query1 = MatchDB.query.filter_by(reciever = email).all()
    query = Database.query.filter_by(email = email).first()
    
    if query1 is not None:
        error=None
    else:
        error='No matches found! :('
    return render_template('matches.html', disp = query.display_name, items=query1, error=error)

@app.route('/acceptmatch', methods=['POST'])
def acceptmatch():
    global email
    error=None
    query = Database.query.filter_by(email = email).first()
    query1 = MatchDB.query.filter_by(reciever = email).all()
    tasks = Database.query.order_by(Database.id).all()
    if request.method == 'POST':
        t_id=request.form['match']
        task = MatchDB.query.filter_by(id=t_id).first()
        if task is not None:
            task.accept = True
            try:
                db.session.commit()
            except:
                error="Cant update! Try again!"
    return render_template('dashboard.html', disp = query.display_name, items=tasks, error=error)
if __name__ == "__main__":
    app.run(debug=True)