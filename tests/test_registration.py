import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from extensions import db
from models import User
from app import app
from extensions import db
from models import User


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_register_new_user(client):

    email = "unittest_registration@example.com"

    # Remove the test user if it already exists
    with app.app_context():
        existing_user = User.query.filter_by(Email=email).first()

        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()

    response = client.post("/register", data={
        "first_name": "Unit",
        "last_name": "Test",
        "email": email,
        "password": "Password123"
    })

    assert response.status_code == 302

    with app.app_context():
        user = User.query.filter_by(
            Email=email
        ).first()

        assert user is not None
        assert user.FirstName == "Unit"
        assert user.LastName == "Test"

        db.session.delete(user)
        db.session.commit()


def test_register_duplicate_email(client):

    email = "unittest_duplicate@example.com"

    with app.app_context():

        existing_user = User.query.filter_by(
            Email=email
        ).first()

        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()

    # Register the first account
    client.post("/register", data={
        "first_name": "First",
        "last_name": "User",
        "email": email,
        "password": "Password123"
    })

    # Try registering another account using the same email
    response = client.post("/register", data={
        "first_name": "Second",
        "last_name": "User",
        "email": email,
        "password": "Password456"
    })

    assert response.status_code == 200
    assert b"An account with this email already exists." in response.data

    # Clean up the test user
    with app.app_context():

        user = User.query.filter_by(
            Email=email
        ).first()

        if user:
            db.session.delete(user)
            db.session.commit()