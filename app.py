from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from config import Config
from models import User, Project, Bug, Comment


app = Flask(__name__)

# Load database configuration
app.config.from_object(Config)

# Secret key for sessions
app.secret_key = app.config["SECRET_KEY"]

# Initialise SQLAlchemy
db.init_app(app)


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return render_template("index.html")


# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(Email=email).first()

        if user and check_password_hash(user.PasswordHash, password):

            session["user_id"] = user.UserID
            session["user_name"] = user.FirstName

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email or password."
        )

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))
# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(Email=email).first()

        if existing_user:

            return render_template(
                "register.html",
                error="An account with this email already exists."
            )

        password_hash = generate_password_hash(password)

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


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    total_bugs = Bug.query.filter_by(UserID=user_id).count()

    open_bugs = Bug.query.filter_by(
        UserID=user_id,
        Status="Open"
    ).count()

    resolved_bugs = Bug.query.filter_by(
        UserID=user_id,
        Status="Resolved"
    ).count()

    high_priority = Bug.query.filter_by(
        UserID=user_id,
        Priority="High"
    ).count()

    projects = Project.query.filter_by(
        UserID=user_id
    ).all()

    bugs = Bug.query.filter_by(
        UserID=user_id
    ).order_by(
        Bug.DateReported.desc()
    ).all()

    return render_template(
        "dashboard.html",
        total_bugs=total_bugs,
        open_bugs=open_bugs,
        resolved_bugs=resolved_bugs,
        high_priority=high_priority,
        projects=projects,
        bugs=bugs
    )


# =========================
# CREATE BUG
# =========================

@app.route("/create_bug", methods=["GET", "POST"])
def create_bug():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    projects = Project.query.filter_by(
        UserID=user_id
    ).all()

    if request.method == "POST":

        project_id = request.form["project_id"]
        title = request.form["title"]
        description = request.form["description"]
        severity = request.form["severity"]

        # =========================
        # SMART PRIORITY SYSTEM
        # =========================

        description_lower = description.lower()

        if severity == "Critical":
            priority = "Critical"

        elif severity == "High":
            priority = "High"

        elif severity == "Medium":

            important_words = [
                "crash",
                "crashes",
                "error",
                "failure",
                "failed",
                "broken",
                "security",
                "login"
            ]

            if any(word in description_lower for word in important_words):
                priority = "High"
            else:
                priority = "Medium"

        else:
            priority = "Low"

        # =========================
        # CREATE BUG
        # =========================

        new_bug = Bug(
            ProjectID=project_id,
            UserID=user_id,
            Title=title,
            Description=description,
            Severity=severity,
            Status="Open",
            Priority=priority
        )

        db.session.add(new_bug)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template(
        "create_bug.html",
        projects=projects
    )


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(debug=True)