from flask import Flask, render_template
from extensions import db
from config import Config

app = Flask(__name__)

# Load database configuration
app.config.from_object(Config)

# Initialise SQLAlchemy
db.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug=True)