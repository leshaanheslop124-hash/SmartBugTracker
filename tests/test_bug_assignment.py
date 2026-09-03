import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from extensions import db
from models import User, Project, Bug

@pytest.fixture
def test_data():

    with app.app_context():

        # Create test administrator
        admin = User(
            FirstName="Test",
            LastName="Admin",
            Email="unittest_admin@example.com",
            PasswordHash="testpassword",
            Role="Admin",
            IsActive=True
        )

        # Create active employee
        employee = User(
            FirstName="Test",
            LastName="Employee",
            Email="unittest_employee@example.com",
            PasswordHash="testpassword",
            Role="Employee",
            IsActive=True
        )

        # Create inactive employee
        inactive_employee = User(
            FirstName="Inactive",
            LastName="Employee",
            Email="unittest_inactive@example.com",
            PasswordHash="testpassword",
            Role="Employee",
            IsActive=False
        )

        db.session.add(admin)
        db.session.add(employee)
        db.session.add(inactive_employee)

        db.session.commit()

        # Create test project
        project = Project(
            ProjectName="Unit Test Project",
            Description="Project created for unit testing",
            UserID=admin.UserID
        )

        db.session.add(project)
        db.session.commit()

        # Create test bug
        bug = Bug(
            ProjectID=project.ProjectID,
            UserID=admin.UserID,
            Title="Unit Test Bug",
            Description="Bug created for assignment testing",
            Severity="Medium",
            Status="Open",
            Priority="Medium"
        )

        db.session.add(bug)
        db.session.commit()

        yield admin, employee, inactive_employee, project, bug

        # Clean up test data
        db.session.delete(bug)
        db.session.delete(project)
        db.session.delete(inactive_employee)
        db.session.delete(employee)
        db.session.delete(admin)

        db.session.commit()


def test_assign_bug_to_active_employee(test_data):

    admin, employee, inactive_employee, project, bug = test_data

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["user_id"] = admin.UserID

        response = client.post(
            f"/admin/assign-bug/{bug.BugID}",
            data={
                "assigned_employee_id": employee.UserID
            }
        )

        assert response.status_code == 302

        with app.app_context():

            updated_bug = db.session.get(Bug, bug.BugID)

            assert updated_bug.AssignedToUserID == employee.UserID
            assert updated_bug.Status == "Assigned"


def test_assign_bug_without_employee(test_data):

    admin, employee, inactive_employee, project, bug = test_data

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["user_id"] = admin.UserID

        response = client.post(
            f"/admin/assign-bug/{bug.BugID}",
            data={}
        )

        assert response.status_code == 302

        with app.app_context():

            updated_bug = db.session.get(Bug, bug.BugID)

            assert updated_bug.AssignedToUserID is None
            assert updated_bug.Status == "Open"


def test_assign_bug_to_inactive_employee(test_data):

    admin, employee, inactive_employee, project, bug = test_data

    with app.test_client() as client:

        with client.session_transaction() as session:
            session["user_id"] = admin.UserID

        response = client.post(
            f"/admin/assign-bug/{bug.BugID}",
            data={
                "assigned_employee_id": inactive_employee.UserID
            }
        )

        assert response.status_code == 302

        with app.app_context():

            updated_bug = db.session.get(Bug, bug.BugID)

            assert updated_bug.AssignedToUserID is None
            assert updated_bug.Status == "Open"