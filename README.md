# SmartBugTracker

SmartBugTracker is a web-based bug tracking application developed as a Software Engineering project. The system allows software development teams and employees to report, manage, assign and track software bugs in one central application.

## Purpose

The purpose of SmartBugTracker is to provide a structured way for software teams to manage bugs throughout the development process. Instead of relying on notes or spreadsheets, users can record bugs in a central database and track their progress.

## Main Features

* User registration and login
* Secure password hashing
* Employee and Administrator roles
* Role-based access control
* Employee dashboard
* Administrator dashboard
* Bug reporting
* Bug editing and deletion
* Bug assignment to employees
* Bug severity levels
* Automatic bug priority calculation
* Employee bug completion workflow
* Administrator bug verification
* Completed work tracking
* User profile management
* Email address updates
* Password changing
* Account activation and disabling
* Project management and database storage
* Git and GitHub version control

## Smart Priority System

SmartBugTracker includes a rule-based priority system.

When a user creates or edits a bug, the system considers the selected severity and the bug description.

Critical and High severity bugs are automatically given the corresponding high priority.

For Medium severity bugs, the system checks the description for important terms such as:

* crash
* error
* failure
* failed
* broken
* security
* login

If an important term is detected, the bug can automatically receive High priority. Otherwise, it remains Medium priority.

This feature helps users identify potentially important bugs without having to manually determine the priority every time.

## Employee and Administrator Workflow

Employees can report bugs and view bugs assigned to them.

An Administrator can assign bugs to active employees.

Once an employee completes an assigned bug, the bug is sent to the Administrator for verification.

The Administrator can either:

* Approve the completed bug, which closes the bug.
* Reject the completed bug, which returns it to an assigned status.

Administrators can also manage user roles and account access.

## Technologies Used

* Python
* Flask
* HTML5
* CSS3
* JavaScript
* SQL Server
* SQLAlchemy
* pyodbc
* Git
* GitHub
* Visual Studio Code / Visual Studio

## Database

The application uses Microsoft SQL Server to store application data.

The main database entities include:

* Users
* Projects
* Bugs
* Comments

SQLAlchemy is used to communicate between the Flask application and the SQL Server database, while pyodbc provides the database connection.

## Project Structure

The project contains the Flask application, database models, configuration files, templates, static files and supporting documentation.

Important files include:

* `app.py` – Main Flask application and routes
* `models.py` – SQLAlchemy database models
* `config.py` – Application and database configuration
* `extensions.py` – Flask-SQLAlchemy setup
* `templates/` – HTML pages
* `static/` – CSS and other static resources
* `database/` – Database-related files

## Running the Application

1. Clone or download the SmartBugTracker repository.
2. Create and activate a Python virtual environment.
3. Install the required Python packages.
4. Configure the SQL Server database connection.
5. Ensure the SmartBugTracker database is available.
6. Start the Flask application.
7. Open the application in a web browser.

The application can be accessed locally through:

`http://127.0.0.1:5000`

## Version Control

Git was used throughout development to track changes to the project.

The project is hosted on GitHub:

https://github.com/leshaanheslop124-hash/SmartBugTracker

The repository contains the development history and commits showing the progress of the project.

## Project Status

SmartBugTracker has been developed as a final Software Engineering project and includes the core functionality required for reporting, managing, assigning and tracking software bugs.
