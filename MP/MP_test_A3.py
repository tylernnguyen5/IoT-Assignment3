# python3 -m unittest MP_test_A3.py

import unittest
from flask import Flask, session
from flask_session import Session
import importlib, importlib.util
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from sqlalchemy import or_, and_
from flask_api import api, db, User, Booking, Car, History

# The set up vairables for the test cases app and Google SQL access
app = Flask(__name__)

HOST="35.201.22.170"
USER="root"
PASSWORD="password"
DATABASE="CarshareTest"

class MasterPiTest(unittest.TestCase):
    """
    Notes: These defined test cases within this module are only the functions that were implemented for Assignment 3
    """

    def setUp(self):
        """
        This is for setting up the test cases with Flask app configuration and cloud database access. This will also init the database from flask_api.py with the app context
        """

        db = SQLAlchemy()
        app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://{}:{}@{}/{}".format(USER, PASSWORD, HOST, DATABASE)
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
        app.app_context().push()
        db.init_app(app)
        with app.app_context():
            db.create_all()

    def test_view_histories(self):
        """
        This test will check if the test database has the right number of records and that the query used get the right of records in Histories table in the test database.

        There are 50 rows in Histories table in the test database.

        Assertion: the number of rows of in Histories table from the query used flask_api.getAllHistories()
        """
        count = History.query.count()

        self.assertEqual(count, 50)


    def test_search_user(self):
        pass


    def test_update_car(self):
        pass


    def test_update_user(self):
        pass


    def test_view_issue_cars(self):
        """
        This test will check if the test database finds right number of cars with issue and that the query used get the right of records in Histories table in the test database.

        There are 2 cars with issue in Cars table in the test database.

        Assertion: the number of cars with issue in Cars table from the query used flask_api.showIssueCars()
        """

        count = Car.query.filter_by(have_issue = True).count()

        self.assertEqual(count, 2)  # Only car 10 has issue


    def test_search_car_with_voice(self):
        pass


if __name__ == "__main__":
    unittest.main()