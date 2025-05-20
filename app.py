from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://chiponda:Genesis#2030#@localhost:3306/school'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey"

# Initialize database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# User model
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    school = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

#Student Model
class Students(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Student_reg = db.Column(db.Integer, unique=True)
    Name = db.Column(db.String(250), unique=True, nullable=False)
    Surname = db.Column(db.String(250), unique=True, nullable=False)
    Dob = db.Column(db.String(250), unique=True, nullable=False)
    Grade= db.Column(db.String(250), nullable=False)
    Class= db.Column(db.String(250), nullable=False)
    Parent= db.Column(db.String(250), nullable=False)
    Gender= db.Column(db.String(250), nullable=False)
# Create database
with app.app_context():
    db.create_all()

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Home route
@app.route("/")
def home():
    return render_template("home.html")

# Register route
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        school=request.form.get("school_name")
        username = request.form.get("username")
        password = request.form.get("password")

        if Users.query.filter_by(school=school).first():
            return render_template("sign_up.html", error="School Already Registered already taken!")

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        new_user = Users(username=username, school=school,password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))
    
    return render_template("sign_up.html")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        school= request.form.get("school_name")
        password = request.form.get("password")

        user = Users.query.filter_by(username=username).filter_by(school=school).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

# Protected dashboard route
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=current_user.username)

# Logout route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))



@app.route('/students')
@login_required
def students():
    students= Students.query.all()
    return render_template('students.html', students=students)


@app.route('/add_data')
def add_data():
    return render_template('add_student.html')

@app.route('/delete/<int:id>')
def erase(id): 
    data = Students.query.get(id)
    db.session.delete(data)
    db.session.commit()
    return redirect('/students')

@app.route('/add', methods=["POST"])
def profile():
    Name = request.form.get("Name")
    Surname = request.form.get("Surname")
    Grade = request.form.get("Grade")
    Class =request.form.get("Class")
    Dob =request.form.get("Dob")
    Student_reg=request.form.get("Student_reg")
    Parent= request.form.get("Parent")
    Gender=request.form.get("Gender")

    if Name != '' and Surname != '' :
        s= Students(Name=Name, Surname=Surname,Grade=Grade,Class=Class,Dob=Dob,Student_reg=Student_reg,Parent=Parent,Gender=Gender)
        db.session.add(s)
        db.session.commit()
        return redirect('/students')
    else:
        return redirect('/students')
    
@app.route('/base')
def base():
    return render_template('data.html')



if __name__ == "__main__":
    with app.app_context():  # Needed for DB operations outside a request
        db.create_all() 
    app.run(debug=True)