from extensions import db


class User(db.Model):
    __tablename__ = "Users"

    UserID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)
    Role = db.Column(db.String(20), nullable=False, default="Employee")
    IsActive = db.Column(db.Boolean, nullable=False, default=True)
    CreatedAt = db.Column(db.DateTime, default=db.func.now())

    projects = db.relationship("Project", backref="user", lazy=True)
    bugs = db.relationship("Bug", backref="user", lazy=True)
    comments = db.relationship("Comment", backref="user", lazy=True)


class Project(db.Model):
    __tablename__ = "Projects"

    ProjectID = db.Column(db.Integer, primary_key=True)
    ProjectName = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(500))
    UserID = db.Column(
        db.Integer,
        db.ForeignKey("Users.UserID"),
        nullable=False
    )
    CreatedAt = db.Column(db.DateTime, default=db.func.now())

    bugs = db.relationship("Bug", backref="project", lazy=True)


class Bug(db.Model):
    __tablename__ = "Bugs"

    BugID = db.Column(db.Integer, primary_key=True)
    ProjectID = db.Column(
        db.Integer,
        db.ForeignKey("Projects.ProjectID"),
        nullable=False
    )
    UserID = db.Column(
        db.Integer,
        db.ForeignKey("Users.UserID"),
        nullable=False
    )
    Title = db.Column(db.String(150), nullable=False)
    Description = db.Column(db.Text, nullable=False)
    Severity = db.Column(db.String(20), nullable=False)
    Status = db.Column(db.String(20), nullable=False, default="Open")
    Priority = db.Column(db.String(20), nullable=False, default="Medium")
    DateReported = db.Column(db.DateTime, default=db.func.now())

    comments = db.relationship("Comment", backref="bug", lazy=True)


class Comment(db.Model):
    __tablename__ = "Comments"

    CommentID = db.Column(db.Integer, primary_key=True)
    BugID = db.Column(
        db.Integer,
        db.ForeignKey("Bugs.BugID"),
        nullable=False
    )
    UserID = db.Column(
        db.Integer,
        db.ForeignKey("Users.UserID"),
        nullable=False
    )
    CommentText = db.Column(db.Text, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=db.func.now())