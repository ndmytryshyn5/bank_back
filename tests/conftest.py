import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from requests import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

import utils

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="module")
def db():
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def client():
    session = Session()
    yield session
    session.close()

@pytest.fixture(scope="module")
def test_user(db):
    user = {
        "email": utils.random_email(),
        "phone_number": utils.random_phone(db),
        "social_security": utils.random_ssn(db),
        "first_name": "Name",
        "last_name": "Surname",
        "date_of_birth": "1999-01-05",
        "address": "Address",
        "city": "City",
        "state": "State",
        "post_code": "00-000",
        "password": "p455w0rd"
    }

    yield user

    utils.clean_test_user(user, db)