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

HOST= "35.201.22.170"
USER= "root"
PASSWORD= "password"
DATABASE= "CarshareTest"

class MasterPiTest(unittest.TestCase):
    """
    This modules contains the unit tests for the features that were implemented in Assignment 3 for part A and B

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
        """
        This test will apply 3 filters to search for users, which are the username, lastname and role.

        There are:

        - 1 user with the username of 'user10'

        - 1 user with the last name of 'Hil'

        - 2 users with the 'Manager' role

        This query used for this test has the same logic with the query used for flask_api.userSearch() endpoint.

        Assertion: the number of users found is 4
        """
        # Search with 3 filters
        username_filter = "an_user10 "
        lname_filter = "Fra"
        role_filter = "Manager"

        # Use the query from the endpoint to test
        users = db.session.query(User).filter(or_(  User.username   == username_filter, 
                                                    User.lname      == lname_filter,
                                                    User.role       == role_filter)).count()
        self.assertEqual(users, 4)


    def test_update_car(self):
        """
        The test will try to update a row in the Car table. That row has the ID of '1' in the table on the cloud database.

        The fields to be updated are:

        - make            : "Lambo"

        - body_type       : "Sport"

        - colour          : "Red"

        - seats           : "2"

        - location        : "-37.814, 144.96332"

        - cost_per_hour   : "50.00"

        - booked          : "0"

        - have_issue      : "0"


        This query used for this test has the same logic with the query used for flask_api.udpateCarInfo() endpoint.

        Assertion: after updated, a query to search for the new unique make will be executed
        """
        # Values for update
        _id = 1
        make            = "Lambo"
        body_type       = "Sport"
        colour          = "Red"
        seats           = "2"
        location        = "-37.814, 144.96332"
        cost_per_hour   = "50.00"
        booked          = "0"
        have_issue      = "0"
         

        car = db.session.query(Car).filter_by(id = _id).first()

        if car is not None:
            car.make            = make
            car.body_type       = body_type
            car.colour          = colour
            car.seats           = seats
            car.location        = location
            car.cost_per_hour   = cost_per_hour
            car.booked          = bool(booked)
            car.have_issue      = bool(have_issue)

            # Commit changes
            db.session.commit()

        # Search for the updated car and assert
        updated = db.session.query(Car).filter_by(make = make).first()

        self.assertTrue((updated is not None)) 


    def test_update_user(self):
        """
        The test will try to update a row in the Users table. That row has the ID of '1' in the table on the cloud database.

        The fields to be updated are:

        - username  : "user_num1"

        - email     : "user_num1@carshare.com"

        - fname     : "Thach"

        - lname     : "Nguyen" 

        - role      : "Admin"

        This query used for this test has the same logic with the query used for flask_api.udpateUserInfo() endpoint.

        Assertion: after updated, a query to search for the new username will be executed
        """
        # Values for update (no update for password)
        _id = 1
        username = "user_num1"
        email = "user_num1@carshare.com"
        fname = "Thach"
        lname = "Nguyen" 
        role = "Admin"

        user = db.session.query(User).filter_by(id = _id).first()

        if user is not None:
            user.username    = username
            user.email       = email
            user.fname       = fname
            user.lname       = lname
            user.role        = role

            # Commit changes
            db.session.commit()

        # Search for the updated user and assert
        updated = db.session.query(User).filter_by(username = username).first()

        self.assertTrue((updated is not None))        


    def test_view_issue_cars(self):
        """
        This will test the query used in flask_api.showIssueCars() to see whether the query return the right number of cars with issue in the Cars table.

        There are 2 cars with issue in Cars table in the test database.

        Assertion: the number of cars with issue in Cars table 
        """

        count = Car.query.filter_by(have_issue = 1).count()

        self.assertEqual(count, 2)  # Only car 9 and 10 have issue

    
    def test_car_voice_search(self):
        """
        This will test the logic that we use for flask_api.carVoiceSearch()

        It will split a string into a list of keywords then run a query to find any cars with those keywords in every column in the Cars table.

        The search string: "Blue SUV Honda"

        There are: 

        - 2 blue cars

        - 4 SUV cars

        - 4 Honda cars

        After removing duplication, the result should return 6 cars.

        Assertion: the number of cars with issue in Cars table
        """
        # Retrieve string of keywords
        keywords = "Blue SUV Honda"

        # Split the string into a [list] of keywords
        _list = keywords.split()

        found = [] # Empty list

        # For each keyword, search in every column in the Car table
        for keyword in _list:
            cars = db.session.query(Car).filter(or_(Car.make            == keyword, 
                                                    Car.body_type       == keyword,
                                                    Car.colour          == keyword,
                                                    Car.seats           == keyword,
                                                    Car.location        == keyword,
                                                    Car.cost_per_hour   == keyword)).all()
            
            for car in cars: # For each row found
                # Add found rows into the list
                found.append(car)

        # After searching for all the keywords, remove duplication from the list
        filtered = list(set(found))
            
        # Assertion
        self.assertEqual(len(filtered), 6)

        

    def test_report_car(self):
        """
        This test will search for a car in the Cars table and change its issue status. Then do an assertion.

        This query used for this test has the same logic with the query used for flask_api.reportCar() endpoint.

        Assertion: the number of cars that have issue is 1
        """
        # Update all rows with no issue
        cars = db.session.query(Car).filter_by(have_issue = 1).all()

        for car in cars:
            car.have_issue = 0

        # Change 1 row and test
        car_id = 5

        car = db.session.query(Car).filter_by(id = car_id).first()
        
        if car is not None:
            car.have_issue = 1
            
            # Commit changes
            db.session.commit()
        else:
            print("[ERROR] No car was found")

        # Search for the updated car and assert
        updated = db.session.query(Car).filter_by(have_issue = 1).count()

        self.assertEqual(updated, 1)


    def test_get_MACs(self):
        """
        This test will retrieve the Bluetooth MAC's adresses of all the Engineers in the cloud database in Users table and put them in a list.

        In the Users test table, there are 2 Engineers with one MAC's address for each in the 'device' column.

        Assertion: the number of MAC's addresses retrieved is 2
        """
        users = User.query.filter_by(role = "Engineer").all()

        addresses = [usr.device for usr in users]   # Get the device addresses and put them in a list

        self.assertEqual(len(addresses), 2)



if __name__ == "__main__":
    unittest.main()