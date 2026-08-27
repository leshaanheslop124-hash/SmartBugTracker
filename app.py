from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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
# ADMIN ACCESS CHECK
# =========================

def admin_required():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("user_role") != "Admin":
        return redirect(url_for("dashboard"))

    return None


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

        user = User.query.filter_by(
            Email=email
        ).first()

        if user and user.IsActive and check_password_hash(
            user.PasswordHash,
            password
        ):

            session["user_id"] = user.UserID
            session["user_name"] = user.FirstName
            session["user_role"] = user.Role

            if user.Role == "Admin":
                return redirect(url_for("admin"))

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid email, password, or account access has been disabled."
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

        existing_user = User.query.filter_by(
            Email=email
        ).first()

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

    if session.get("user_role") == "Admin":
        return redirect(url_for("admin"))

    user_id = session["user_id"]


    # =========================
    # DASHBOARD STATISTICS
    # =========================

    # Total bugs reported by the employee
    # OR assigned to the employee.
    total_bugs = Bug.query.filter(
        db.or_(
            Bug.UserID == user_id,
            Bug.AssignedToUserID == user_id
        )
    ).count()


    # =========================
    # OPEN / ACTIVE BUGS
    # =========================

    # Counts bugs that this employee reported
    # OR bugs assigned to this employee.
    #
    # Closed bugs are not counted.

    open_bugs = Bug.query.filter(
        db.or_(
            Bug.UserID == user_id,
            Bug.AssignedToUserID == user_id
        ),
        Bug.Status != "Closed"
    ).count()


    # =========================
    # RESOLVED / COMPLETED BUGS
    # =========================

    # Counts bugs that this employee completed,
    # even if another employee originally reported them.

    resolved_bugs = Bug.query.filter(
        Bug.CompletedByUserID == user_id,
        Bug.Status == "Closed"
    ).count()


    # =========================
    # HIGH PRIORITY BUGS
    # =========================

    # Counts High and Critical priority bugs
    # reported by OR assigned to this employee.
    #
    # Closed bugs are not counted.

    high_priority = Bug.query.filter(
        db.or_(
            Bug.UserID == user_id,
            Bug.AssignedToUserID == user_id
        ),
        Bug.Priority.in_(["High", "Critical"]),
        Bug.Status != "Closed"
    ).count()


    # =========================
    # SHARED PROJECTS
    # =========================

    projects = Project.query.all()


    # =========================
    # MY REPORTED BUGS
    # =========================

    # Shows bugs personally reported by this employee.
    #
    # Closed bugs are removed from this active section.

    reported_bugs = Bug.query.filter(
        Bug.UserID == user_id,
        Bug.Status != "Closed"
    ).order_by(
        Bug.DateReported.desc()
    ).all()


    # =========================
    # CURRENT ASSIGNED BUGS
    # =========================

    # Shows active bugs currently assigned
    # to this employee.
    #
    # Closed bugs are removed.

    assigned_bugs = Bug.query.filter(
        Bug.AssignedToUserID == user_id,
        Bug.Status != "Closed"
    ).order_by(
        Bug.DateReported.desc()
    ).all()


    # =========================
    # RESOLVED / COMPLETED WORK
    # =========================

    # Shows bugs successfully completed by
    # this employee and approved by an administrator.
    #
    # This works even if another user originally
    # reported the bug.

    completed_bugs = Bug.query.filter(
        Bug.CompletedByUserID == user_id,
        Bug.Status == "Closed"
    ).order_by(
        Bug.DateReported.desc()
    ).all()


    # =========================
    # LOAD EMPLOYEE DASHBOARD
    # =========================

    return render_template(
        "dashboard.html",
        total_bugs=total_bugs,
        open_bugs=open_bugs,
        resolved_bugs=resolved_bugs,
        high_priority=high_priority,
        projects=projects,
        reported_bugs=reported_bugs,
        assigned_bugs=assigned_bugs,
        completed_bugs=completed_bugs
    )


# =========================
# PROFILE
# =========================

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(
        session["user_id"]
    )

    return render_template(
        "profile.html",
        user=user
    )


# =========================
# EDIT PROFILE
# =========================

@app.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(
        session["user_id"]
    )

    if request.method == "POST":

        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()
        email = request.form["email"].strip()

        existing_user = User.query.filter(
            User.Email == email,
            User.UserID != user.UserID
        ).first()

        if existing_user:

            return render_template(
                "edit_profile.html",
                user=user,
                error="That email address is already being used by another account."
            )

        user.FirstName = first_name
        user.LastName = last_name
        user.Email = email

        db.session.commit()

        session["user_name"] = user.FirstName

        return redirect(url_for("profile"))

    return render_template(
        "edit_profile.html",
        user=user
    )


# =========================
# CHANGE PASSWORD
# =========================

@app.route("/profile/change-password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(
        session["user_id"]
    )

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]


        # Check current password

        if not check_password_hash(
            user.PasswordHash,
            current_password
        ):

            return render_template(
                "change_password.html",
                user=user,
                error="Your current password is incorrect."
            )


        # Check that new passwords match

        if new_password != confirm_password:

            return render_template(
                "change_password.html",
                user=user,
                error="The new passwords do not match."
            )


        # Prevent reusing the same password

        if check_password_hash(
            user.PasswordHash,
            new_password
        ):

            return render_template(
                "change_password.html",
                user=user,
                error="Your new password must be different from your current password."
            )


        user.PasswordHash = generate_password_hash(
            new_password
        )

        db.session.commit()

        return redirect(url_for("profile"))

    return render_template(
        "change_password.html",
        user=user
    )


# =========================
# ADMIN
# =========================

@app.route("/admin")
def admin():

    access_check = admin_required()

    if access_check:
        return access_check


    total_users = User.query.count()


    total_employees = User.query.filter_by(
        Role="Employee",
        IsActive=True
    ).count()


    total_admins = User.query.filter_by(
        Role="Admin",
        IsActive=True
    ).count()


    active_users = User.query.filter_by(
        IsActive=True
    ).count()


    disabled_users = User.query.filter_by(
        IsActive=False
    ).count()


    admins = User.query.filter_by(
        Role="Admin"
    ).order_by(
        User.CreatedAt.desc()
    ).all()


    employees = User.query.filter_by(
        Role="Employee"
    ).order_by(
        User.CreatedAt.desc()
    ).all()


    return render_template(
        "admin.html",
        total_users=total_users,
        total_employees=total_employees,
        total_admins=total_admins,
        active_users=active_users,
        disabled_users=disabled_users,
        admins=admins,
        employees=employees,
        current_date=datetime.now()
    )


# =========================
# ADMIN BUG MANAGEMENT
# =========================

@app.route("/admin/bugs")
def admin_bugs():

    access_check = admin_required()

    if access_check:
        return access_check


    # Get all bugs except closed bugs

    bugs = Bug.query.filter(
        Bug.Status != "Closed"
    ).order_by(
        Bug.DateReported.desc()
    ).all()


    # Get all active employees

    employees = User.query.filter_by(
        Role="Employee",
        IsActive=True
    ).order_by(
        User.FirstName.asc()
    ).all()


    return render_template(
        "admin_bugs.html",
        bugs=bugs,
        employees=employees
    )


# =========================
# ASSIGN BUG TO EMPLOYEE
# =========================

@app.route("/admin/assign-bug/<int:bug_id>", methods=["POST"])
def assign_bug(bug_id):

    access_check = admin_required()

    if access_check:
        return access_check


    bug = Bug.query.get_or_404(
        bug_id
    )


    assigned_employee_id = request.form.get(
        "assigned_employee_id"
    )


    # Make sure an employee was selected

    if not assigned_employee_id:
        return redirect(url_for("admin_bugs"))


    # Make sure selected user is an active employee

    employee = User.query.filter_by(
        UserID=assigned_employee_id,
        Role="Employee",
        IsActive=True
    ).first()


    if not employee:
        return redirect(url_for("admin_bugs"))


    # Assign the bug

    bug.AssignedToUserID = employee.UserID


    # Change status

    bug.Status = "Assigned"


    db.session.commit()


    return redirect(
        url_for("admin_bugs")
    )
    

# =========================
# ADMIN VERIFY COMPLETED BUG
# =========================

@app.route("/admin/verify-bug/<int:bug_id>", methods=["POST"])
def verify_bug(bug_id):

    access_check = admin_required()

    if access_check:
        return access_check


    bug = Bug.query.get_or_404(
        bug_id
    )


    action = request.form.get(
        "action"
    )


    # =========================
    # APPROVE BUG
    # =========================

    if action == "approve":

        if bug.Status == "Awaiting Verification":

            bug.Status = "Closed"

            db.session.commit()


    # =========================
    # REJECT BUG
    # =========================

    elif action == "reject":

        if bug.Status == "Awaiting Verification":

            bug.Status = "Assigned"

            db.session.commit()


    return redirect(
        url_for("admin_bugs")
    )


# =========================
# CHANGE USER ROLE
# =========================

@app.route("/admin/change-role/<int:user_id>", methods=["POST"])
def change_role(user_id):

    access_check = admin_required()

    if access_check:
        return access_check


    current_admin_id = session.get(
        "user_id"
    )


    # Prevent admin from changing own role

    if user_id == current_admin_id:
        return redirect(url_for("admin"))


    user = User.query.get_or_404(
        user_id
    )


    if user.Role == "Employee":

        user.Role = "Admin"

    elif user.Role == "Admin":

        user.Role = "Employee"


    db.session.commit()


    return redirect(
        url_for("admin")
    )


# =========================
# DISABLE / RESTORE USER
# =========================

@app.route("/admin/toggle-status/<int:user_id>", methods=["POST"])
def toggle_user_status(user_id):

    access_check = admin_required()

    if access_check:
        return access_check


    current_admin_id = session.get(
        "user_id"
    )


    # Prevent admin from disabling own account

    if user_id == current_admin_id:
        return redirect(url_for("admin"))


    user = User.query.get_or_404(
        user_id
    )


    user.IsActive = not user.IsActive


    db.session.commit()


    return redirect(
        url_for("admin")
    )


# =========================
# CREATE BUG
# =========================

@app.route("/create_bug", methods=["GET", "POST"])
def create_bug():

    if "user_id" not in session:
        return redirect(url_for("login"))


    user_id = session["user_id"]


    # =========================
    # SHARED PROJECTS
    # =========================

    projects = Project.query.all()


    if request.method == "POST":

        project_id = request.form["project_id"]
        title = request.form["title"].strip()
        description = request.form["description"].strip()
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


            if any(
                word in description_lower
                for word in important_words
            ):

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


        db.session.add(
            new_bug
        )

        db.session.commit()


        return redirect(
            url_for("dashboard")
        )


    return render_template(
        "create_bug.html",
        projects=projects
    )


# =========================
# EDIT BUG
# =========================

@app.route("/edit_bug/<int:bug_id>", methods=["GET", "POST"])
def edit_bug(bug_id):

    if "user_id" not in session:
        return redirect(url_for("login"))


    user_id = session["user_id"]


    # Users can only edit their own bugs

    bug = Bug.query.filter_by(
        BugID=bug_id,
        UserID=user_id
    ).first_or_404()


    # Shared projects

    projects = Project.query.all()


    if request.method == "POST":

        project_id = request.form["project_id"]
        title = request.form["title"].strip()
        description = request.form["description"].strip()
        severity = request.form["severity"]
        status = request.form["status"]


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


            if any(
                word in description_lower
                for word in important_words
            ):

                priority = "High"

            else:

                priority = "Medium"


        else:

            priority = "Low"


        # =========================
        # UPDATE BUG
        # =========================

        bug.ProjectID = project_id
        bug.Title = title
        bug.Description = description
        bug.Severity = severity
        bug.Status = status
        bug.Priority = priority


        db.session.commit()


        return redirect(
            url_for("dashboard")
        )


    return render_template(
        "edit_bug.html",
        bug=bug,
        projects=projects
    )

# =========================
# ADMIN EDIT BUG
# =========================

@app.route("/admin/edit_bug/<int:bug_id>", methods=["GET", "POST"])
def admin_edit_bug(bug_id):

    access_check = admin_required()

    if access_check:
        return access_check

    bug = Bug.query.get_or_404(bug_id)

    projects = Project.query.all()

    if request.method == "POST":

        project_id = request.form["project_id"]
        title = request.form["title"].strip()
        description = request.form["description"].strip()
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

            if any(
                word in description_lower
                for word in important_words
            ):
                priority = "High"

            else:
                priority = "Medium"

        else:

            priority = "Low"

        # =========================
        # UPDATE BUG
        # =========================

        bug.ProjectID = project_id
        bug.Title = title
        bug.Description = description
        bug.Severity = severity
        bug.Priority = priority

        db.session.commit()

        return redirect(
            url_for("admin_bugs")
        )

    return render_template(
        "admin_edit_bug.html",
        bug=bug,
        projects=projects
    )

# =========================
# EMPLOYEE REPORT BUG COMPLETED
# =========================

@app.route("/complete_bug/<int:bug_id>", methods=["POST"])
def complete_bug(bug_id):

    # Employee must be logged in

    if "user_id" not in session:
        return redirect(url_for("login"))


    user_id = session["user_id"]


    # Find bug assigned to this employee

    bug = Bug.query.filter_by(
        BugID=bug_id,
        AssignedToUserID=user_id
    ).first_or_404()


    # Only assigned bugs can be reported completed

    if bug.Status != "Assigned":
        return redirect(url_for("dashboard"))


    # Record employee who completed the bug

    bug.CompletedByUserID = user_id


    # Send bug to administrator for verification

    bug.Status = "Awaiting Verification"


    db.session.commit()


    return redirect(
        url_for("dashboard")
    )


# =========================
# DELETE BUG
# =========================

@app.route("/delete_bug/<int:bug_id>", methods=["POST"])
def delete_bug(bug_id):

    if "user_id" not in session:
        return redirect(url_for("login"))


    user_id = session["user_id"]


    # Users can only delete their own bugs

    bug = Bug.query.filter_by(
        BugID=bug_id,
        UserID=user_id
    ).first_or_404()


    db.session.delete(
        bug
    )

    db.session.commit()


    return redirect(
        url_for("dashboard")
    )


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(debug=True)