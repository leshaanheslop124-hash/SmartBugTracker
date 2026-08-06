from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from config import Config
from models import User

app = Flask(__name__)

# Load database configuration
app.config.from_object(Config)

# Initialise SQLAlchemy
db.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        # Find user by email
        user = User.query.filter_by(Email=email).first()

        # Check user exists and password is correct
        if user and check_password_hash(user.PasswordHash, password):

            session["user_id"] = user.UserID
            session["user_name"] = user.FirstName

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if email already exists
        existing_user = User.query.filter_by(Email=email).first()

        if existing_user:
            return render_template(
                "register.html",
                error="An account with this email already exists."
            )

        # Hash the password before storing it
        password_hash = generate_password_hash(password)

        # Create new user
        new_user = User(
            FirstName=first_name,
            LastName=last_name,
            Email=email,
            PasswordHash=password_hash
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)