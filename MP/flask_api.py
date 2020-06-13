from flask import Flask, Blueprint, request, jsonify, render_template, flash, redirect, url_for, session, escape
from flask_sqlalchemy import SQLAlchemy 
from flask_marshmallow import Marshmallow 
import os, requests, json
from flask import current_app as app
from passlib.hash import sha256_crypt
from sqlalchemy import or_, and_
from calendar_for_api import Calendar
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons
from dynaconf import FlaskDynaconf

api = Blueprint("api", __name__)
ACCESS_TOKEN="o.vMLEwFOCGBzUDzOCxqQ4Mdsda7m6KNHL"
db = SQLAlchemy() # for accessing database
ma = Marshmallow() # for serializing objects


# Declare Calendar object
calendar = Calendar()


# DECLARING THE MODELS

# USER
class User(db.Model):
    """Declaring User model with its fields and properties (the Users table in Carshare database on Google Cloud SQL)

    Arguments:
        db {SQLAlchemy} -- for accessing Carshare database on Google Cloud SQL
    """      
    __tablename__   = "Users"
    id              = db.Column(db.Integer,     primary_key = True,     autoincrement = True)
    username        = db.Column(db.String(),    nullable = False,       unique = True)
    password        = db.Column(db.String(),    nullable = False)
    email           = db.Column(db.String(),    nullable = False,       unique = True)
    fname           = db.Column(db.String(),    nullable = False)
    lname           = db.Column(db.String(),    nullable = False)
    role            = db.Column(db.String(),    nullable = False)
    device          = db.Column(db.String(),    nullable = True)
    
    def __init__(self, username, password, email, fname, lname, role, device):
        """inits User with data

        Arguments:
            username {str} -- User's username
            password {str} -- User's password
            email {str} -- User's email
            fname {str} -- User's first name
            lname {str} -- User's last name
            role {str}  -- User's role (Customer/ Admin/ Manager/ Engineer)
            device {str}-- User's Bluetoothe MAC Address
        """
        self.username   = username
        self.password   = password
        self.email      = email
        self.fname      = fname
        self.lname      = lname
        self.role       = role
        self.device     = device

class UserSchema(ma.Schema):
    """This part defined structure of JSON response of our endpoint for User model. Here we define the keys in our JSON response. The fields that will be exposed.

    Arguments:
        ma {Marshmallow} -- for serializing objects
    """
    class Meta:
        # Fields to expose (not exposing password)
        fields = ('id', 'username', 'email', 'fname', 'lname', 'role', 'device')

user_schema = UserSchema()              # an instance of UserSchema
users_schema = UserSchema(many=True)    # instances of list of UserSchema


# CAR
class Car(db.Model):
    """Declaring Car model with its fields and properties (the Cars table in Carshare database on Google Cloud SQL)

    Arguments:
        db {SQLAlchemy} -- for accessing Carshare database on Google Cloud SQL
    """ 
    __tablename__   = "Cars"
    id              = db.Column(db.Integer,         primary_key = True,     autoincrement = True)
    make            = db.Column(db.String(),        nullable = False)
    body_type       = db.Column(db.String(),        nullable = False)
    colour          = db.Column(db.String(),        nullable = False)
    seats           = db.Column(db.Integer(),       nullable = False)
    location        = db.Column(db.String(),        nullable = False)
    cost_per_hour   = db.Column(db.Float(4, 2),     nullable = False)
    booked          = db.Column(db.Boolean(),       nullable = False)
    have_issue      = db.Column(db.Boolean(),       nullable = False)

    def __init__(self, make, body_type, colour, seats, location, cost_per_hour, booked, have_issue):
        """inits Car with data

        Arguments:
            make {str} -- The make/brand of the car
            body_type {str} -- The body type of the car (Sedan/ SUV/ etc.)
            colour {str} -- The colour of the car
            seats {int} -- The number of seats in the car
            location {str} -- The current location of the car, presented in latitude and longitude
            cost_per_hour {float(4, 2)} -- The cost per hour of the car in AUD
            booked {boolean} -- The car's availability, whether the car is booked or not
            have_issue {boolean} -- The car's issue status, whether the car needs to be repaired or not
        """
        self.make           = make
        self.body_type      = body_type
        self.colour         = colour
        self.seats          = seats
        self.location       = location
        self.cost_per_hour  = cost_per_hour
        self.booked         = booked
        self.have_issue     = have_issue

class CarSchema(ma.Schema):
    """This part defined structure of JSON response of our endpoint for Car model. Here we define the keys in our JSON response. The fields that will be exposed.

    Arguments:
        ma {Marshmallow} -- for serializing objects
    """
    class Meta:
        # Fields to expose
        fields = ('id', 'make', 'body_type', 'colour', 'seats', 'location', 'cost_per_hour', 'booked', 'have_issue')

car_schema = CarSchema()            # an instance of CarSchema
cars_schema = CarSchema(many=True)  # instances of list of CarSchema


# BOOKING
class Booking(db.Model):
    """Declaring Booking model with its fields and properties (the Bookings table in Carshare database on Google Cloud SQL)

    Arguments:
        db {SQLAlchemy} -- for accessing Carshare database on Google Cloud SQL
    """ 
    __tablename__   = "Bookings"
    id              = db.Column(db.Integer,     primary_key = True,         autoincrement = True)
    user_id         = db.Column(db.String(),    nullable = False)
    car_id          = db.Column(db.String(),    nullable = False)
    begin_time      = db.Column(db.DateTime(),  nullable = False)
    return_time     = db.Column(db.DateTime(),  nullable = False)
    ongoing         = db.Column(db.Boolean(),   nullable = False)
    
    def __init__(self, user_id, car_id, begin_time, return_time, ongoing):
        """inits Booking with data

        Arguments:
            user_id {int} -- User ID of the user who books the car
            car_id {int} -- Car ID of the car which is booked
            begin_time {datetime} -- The beginning date and time of the finished booking
            return_time {datetime} -- The return date and time of the finished booking
            ongoing {Boolean} -- The status of the booking. When the user comes to the booking and unlock the car, the ongoing status will be set to True
        """
        self.user_id        = user_id
        self.car_id         = car_id
        self.begin_time     = begin_time
        self.return_time    = return_time
        self.ongoing        = ongoing

class BookingSchema(ma.Schema):
    """This part defined structure of JSON response of our endpoint for Booking model. Here we define the keys in our JSON response. The fields that will be exposed.

    Arguments:
        ma {Marshmallow} -- for serializing objects
    """
    class Meta:
        # Fields to expose (not exposing id)
        fields = ('user_id', 'car_id', 'begin_time', 'return_time', 'ongoing')

booking_schema = BookingSchema()            # an instance of BookingSchema
bookings_schema = BookingSchema(many=True)  # instances of list of BookingSchema


# HISTORY
class History(db.Model):
    """Declaring History model with its fields and properties (the Histories table in Carshare database on Google Cloud SQL)

    Arguments:
        db {SQLAlchemy} -- for accessing Carshare database on Google Cloud SQL
    """ 
    __tablename__   = "Histories"
    id              = db.Column(db.Integer,     primary_key = True,         autoincrement = True)
    user_id         = db.Column(db.String(),    nullable = False)
    car_id          = db.Column(db.String(),    nullable = False)
    begin_time      = db.Column(db.DateTime(),  nullable = False)
    return_time     = db.Column(db.DateTime(),  nullable = False)
    
    def __init__(self, user_id, car_id, begin_time, return_time):
        """inits History with data

        Arguments:
            user_id {int} -- User ID of the user who books the car
            car_id {int} -- Car ID of the car which is booked
            begin_time {datetime} -- The beginning date and time of the finished booking
            return_time {datetime} -- The return date and time of the finished booking
        """
        self.user_id        = user_id
        self.car_id         = car_id
        self.begin_time     = begin_time
        self.return_time    = return_time

class HistorySchema(ma.Schema):
    """This part defined structure of JSON response of our endpoint for History model. Here we define the keys in our JSON response. The fields that will be exposed.

    Arguments:
        ma {Marshmallow} -- for serializing objects
    """
    class Meta:
        # Fields to expose (not exposing id)
        fields = ('user_id', 'car_id', 'begin_time', 'return_time')

history_schema = HistorySchema()            # an instance of HistorySchema
histories_schema = HistorySchema(many=True) # instances of list of HistorySchema

# ENDPOINTS

# Endpoint to register
@api.route("/register", methods = ["GET", "POST"])
def register():
    """
    To register:
        - Variables will be declared from the form data
        - Username and email will be checked if they are taken
        - If they are taken:
            - User will be redirected to Registration page
        - If they are not taken:
            - The password will be hashed
            - A new row will be declared (newUser) and added to Users table
            - User will be redirected to Login page
    """

    if request.method=="POST":
        # Get form data
        username        = request.form.get("username")
        password        = request.form.get("password")
        email           = request.form.get("email")
        fname           = request.form.get("fname")
        lname           = request.form.get("lname")
        role            = request.form.get("role")

        # Check if the username or email has already been registered
        registered = db.session.query(User).filter(or_( User.username == username, 
                                                        User.email == email)).first()

        if registered is not None:
            flash("The username or email ALREADY EXISTS. Cannot be used for registration", "danger")
            
            return redirect(url_for('site.registerPage'))
        else:
            flash("The username and email DO NOT EXIST. Can be used for registration")
            
            # Hash the password before insertion
            hashed_password = sha256_crypt.hash(str(password))
            
            # Prepare row and add to the database
            newUser = User( username = username, 
                            password = hashed_password, 
                            email = email, 
                            fname = fname, 
                            lname = lname, 
                            role = role,
                            device = None)
            db.session.add(newUser)

            # Commit changes
            db.session.commit()

            flash("You are registered and can now login","success")
            return redirect(url_for('site.loginPage'))  # Go to Login page after registration

    return render_template('register.html')


# Endpoint to login 
@api.route("/login", methods=["GET", "POST"])
def login():
    """
    To login:
        - Username will be checked in Users table to see if validated
        - If the username does not exist:
            - User will be redirected to Login page
        - If the username exists:
            - Stored password of that username will be retrieved
            - Submitted password will be verified
            - If verfied:
                - User ID (session data) will be set
                - User will be redirected to Home page
            - If failing verification:
                - User will be redirected to Login page
    """

    if request.method=="POST":
        # Get form data
        username    = request.form.get("username")
        password    = request.form.get("password")

        # Query 
        data = db.session.query(User.id, User.password, User.role).filter_by(username = username).first()

        if data is None: # If username does not exist
            flash("Invalid Username!", "error")
            return render_template('login.html')
        else: # If username exists
            user_id = data[0]
            stored_password = data[1] 
            user_role = data[2]
            # Verify password
            if sha256_crypt.verify(password, stored_password):
                # flash("You are now logged in!", "success")

                # Set session data
                session["user_id"] = user_id
                session["username"] = username
                session["role"] = user_role
                return redirect(url_for('site.homePage'))
            else:
                flash("Invalid Password!", "error")
                return render_template('login.html') 
 
    return render_template('login.html')


# Endpoint to logout
@api.route('/logout')
def logout():
    """
    When the user logouts:
        - User ID (session data) will be removed
        - User will be redirected to Index page
    """

   # Remove the user ID from the session if it is there
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash("You are now logged out!", "danger")
    return redirect(url_for('site.index'))


# Endpoint to view histories (user-specified)
@api.route("/history/<user_id>", methods = ["GET"])
def getUserHistories(user_id):
    """
    When the user chooses to view histories:
        - User ID will be retrieved from session data
        - Pass the User ID to the URL
        - A query will be executed to return all the histories of the targeted user
    """

    histories = History.query.filter_by(user_id = user_id).all()

    result = histories_schema.dump(histories)

    return jsonify(result)


# Endpoint to show all UNBOOKED cars
@api.route("/car/unbooked", methods = ["GET"])
def getUnbookedCars():
    """
    All cars whose unbooked column set to False will be returned from the Cars table
    """

    cars = Car.query.filter_by(booked = False).all()

    result = cars_schema.dump(cars)

    return jsonify(result)


# Endpoint to search for cars
@api.route("/car/search", methods = ["GET", "POST"])
def carSearch():
    """
    To search for cars:
        - Filters will be declared from form data
        - A query with OR conditions will be executed to find the filtered cars
        - The result will be displayed in Car Search Result page
    """

    if request.method=="POST":
        _id             = request.form.get("id")
        make            = request.form.get("make")
        body_type       = request.form.get("body_type")
        colour          = request.form.get("colour")
        seats           = request.form.get("seats")
        location        = request.form.get("location")
        cost_per_hour   = request.form.get("cost_per_hour")
        booked          = request.form.get("booked")        # if this field is null, it's equivalent to 0 (False)
        have_issue      = request.form.get("have_issue")    # if this field is null, it's equivalent to 0 (False) 

        cars = db.session.query(Car).filter(or_(Car.id              == _id, 
                                                Car.make            == make,
                                                Car.body_type       == body_type,
                                                Car.colour          == colour,
                                                Car.seats           == seats,
                                                Car.location        == location,
                                                Car.cost_per_hour   == cost_per_hour,
                                                Car.booked          == booked,
                                                Car.have_issue      == have_issue)).all()
        
        result = cars_schema.dump(cars)
        return render_template('car_search_result.html', cars = result)

    return render_template('car_search.html')


# Endpoint to make a booking
@api.route("/booking/make", methods = ["GET", "POST"])
def makeABooking():
    """
    To make a booking:
        - Varibables will be declared from the form data
        - Especially for begin/return time:
            - HTML does not support input type Datetime
            - So we use to 2 separated input types in the form data: date and time
            - Variables begin_datetime and return_datetime will be a result of combining the inputs above (will be used for begin_time/return_time column in the Bookings table)
        - A new row for the new booking will be created and added to the Bookings table
        - The booked car's availability will be updated in the Cars table (booked column will be set to True)
        - An event will be also created to add to the Google Calendar:
            - Information about the User ID, Car ID, summary and duration of the event will be declared
        - User will be redirected to the Home page after the booking is made
    """

    if request.method=="POST":
        # Get input from form data
        # Resource to handle date/time values: https://www.w3schools.com/html/html_form_input_types.asp
        user_id     = session.get("user_id")
        car_id      = request.form.get("car_id")
        begin_date  = request.form.get("begin_date")
        begin_time  = request.form.get("begin_time")
        return_date = request.form.get("return_date")
        return_time = request.form.get("return_time")

        begin_datetime  = "{} {}".format(begin_date, begin_time) 
        return_datetime = "{} {}".format(return_date, return_time) 

        # Prepare object for database insertion
        newBooking = Booking(   user_id = user_id,
                                car_id = car_id,
                                begin_time = begin_datetime,
                                return_time = return_datetime,
                                ongoing = False)

        # Add new row to the database
        db.session.add(newBooking)

        # Update car's availability 
        car = Car.query.get(car_id) 
        car.booked = True

        # Commit changes
        db.session.commit()

        # Add event to Google Calendar
        event = {
            'summary': 'Carshare Booking Reservation',
            'description': f'userId: {user_id} and carId: {car_id}',
            'start': {
                'dateTime': begin_datetime.replace(' ', 'T') + ':00+10:00',  # '2020-05-02T10:00:00+10:00'
            },
            'end': {
                'dateTime': return_datetime.replace(' ', 'T') + ':00+10:00',
            },
        }
        calendar.insert(event)

        flash("Booking made")

        return redirect(url_for('site.homePage'))

    return render_template('make_a_booking.html')


# Endpoint to cancel a booking
@api.route("/booking/cancel", methods = ["GET", "POST"])
def cancelABooking():
    """
    When the user chooses to cancel a booking:
        - Variables will be declared from the form data
        - Especially for begin time:
            - HTML does not support input type Datetime
            - So we use to 2 separated input types in the form data: date and time
            - Variables begin_datetime will be a result of combining the inputs above (will be used for begin_time column in the Bookings table)
        - A query will be executed to find right booking in the Bookings table and removed
        - The booked car's availability will be updated in the Cars table (booked column will be set to False)
        - An event will be also removed from the Google Calendar
        - User will be redirected to the Home page after the booking is cancelled
    """

    if request.method=="POST":
        # Get input from form data
        # Resource to handle date/time values: https://www.w3schools.com/html/html_form_input_types.asp
        user_id     = session.get("user_id")
        car_id      = request.form.get("car_id")
        begin_date  = request.form.get("begin_date")
        begin_time  = request.form.get("begin_time")

        begin_datetime  = "{} {}".format(begin_date, begin_time) 

        # Prepare object for database insertion
        booking = db.session.query(Booking).filter( Booking.user_id == user_id,
                                                    Booking.car_id == car_id,
                                                    Booking.begin_time == begin_datetime).first()

        # Delete row from the database
        db.session.delete(booking)

        # Update car's availability 
        car = Car.query.get(car_id)
        car.booked = False

        # Commit changes
        db.session.commit()

        # Delete event from Google Calendar
        calendar.delete(user_id, car_id, begin_datetime)

        flash("Booking cancelled")

        return redirect(url_for('site.homePage'))

    return render_template('cancel_a_booking.html')


# Endpoint to unlock a car
@api.route("/car/unlock", methods = ["PUT"])
def unlockCar():
    """
    When the user choose to unlock the car on Agent Pi and the request is send via TCP socket:
        - User ID, Car ID and booking begin time will be retrieved from the form data
        - Access Bookings table to find the right row, in order to see if the user provides the correct booking details
        - Set the ongoing status of the booking to True
    """
    
    user_id     = request.form.get("user_id")
    car_id      = request.form.get("car_id")
    begin_time  = request.form.get("begin_time")

    # Check if this is the right user with the right booked car and time 
    booking = db.session.query(Booking).filter_by(  user_id = user_id,
                                                    car_id = car_id,
                                                    begin_time = begin_time).first()

    # Activate booking
    if booking is not None:
        booking.ongoing = 1

        # Commit changes
        db.session.commit()

        flash("Unlocked Car")

        return "unlocked"
    else: return None


# Endpoint to lock a car
@api.route("/car/lock", methods = ["PUT"])
def lockCar():
    """
    When the user choose to lock the car on Agent Pi and the request is send via TCP socket:
        - User ID and Car ID will be retrieved from the form data
        - The user can only lock the car if the booking status is ongoing, which means the car has been unlocked
        - Access Bookings table to find the row which has the right User ID, Car ID and the ongoing status is True
        - Begin and return time of the booking will be passed to specific variables (to be recorded in Histories table later)
        - The target booking will be removed to indicate the booking has finished
        - A record will be added to Histories table
        - Car's availability will be updated in the Cars table
    """

    user_id     = request.form.get("user_id")
    car_id      = request.form.get("car_id")

    # Find the booking
    booking = db.session.query(Booking).filter_by(  user_id = user_id,
                                                    car_id = car_id,
                                                    ongoing = 1).first()
    
    if booking is not None:
        begin_time = booking.begin_time
        return_time = booking.return_time

        # Record finished booking to History table
        newHistory = History(   user_id = user_id,
                                car_id = car_id,
                                begin_time = begin_time,
                                return_time = return_time)
        db.session.add(newHistory)

        # Remove record from Booking table
        db.session.delete(booking)

        # Update car's availability
        car = Car.query.get(car_id) 
        car.booked = False

        # Commit changes
        db.session.commit()

        flash("Locked Car")

        return "locked"
    else: return None


# Endpoint to get car's location with Google Maps API
@api.route("/car/location/<car_id>", methods = ["GET"])
def showCarLocation(car_id):
    """
    The function will: 
        - Access Cars table 
        - Search for the car with the right id
        - Get its location
        - Define latitude and longitude variables 
        - Use the varibles for the Google Map API to show its location
    """

    # Get the targeted car and get its location (latitude and longitude)
    car_id = car_id
    car = Car.query.get(car_id) 
    location = car.location

    myLat = location.split(", ")[0]
    myLng = location.split(", ")[1]

    return render_template("car_location.html",
        car_id=car_id,
        lat = myLat, lng = myLng)


# Endpoint to check login credentials from Agent Pi
@api.route("/ap_login", methods = ["POST"])
def apLogin():
    """This request comes from the TCP server (server_MP.py). Credentials are sent in form data to check the validty.
    An User ID will be returned to the Agent Pi if successful.

    Returns:
        str -- User ID if valid credentials. None for the otherwise
    """
    username     = request.form.get("username")
    password     = request.form.get("password")

    data = db.session.query(User.id, User.password).filter_by(username = username).first()

    if data is None: # If username does not exist
        return None
    else: # If username exists
        user_id = data[0]
        stored_password = data[1] 

        # Verify password
        if sha256_crypt.verify(password, stored_password): #Validated
            return str(user_id)
        else: # Invalidated
            return None

# ===================================================================================

# Most of new changes for A3 go below

# NOT TESTED (waiting on templates/other implementation)
# Endpoint to view all histories
@api.route("/history", methods = ["GET"])
def getAllHistories():
    """
    This will be used to display all rental history on Admin's Home page.
    This endpoint will return all data in the History table on the cloud database

    Returns:
        JSON -- All histories in the History table
    """

    histories = History.query.all()

    result = histories_schema.dump(histories)

    return jsonify(result)

# NOT TESTED (waiting on templates/other implementation)
# Endpoint to search for users
@api.route("/user/search", methods = ["GET", "POST"])
def userSearch():
    """
    To search for users:
        - Filters will be declared from the form data
        - A query with OR conditions will be executed to find the filtered users
        - The result will be displayed in User Search Result page

    For GET request: this endpoint will render the User Search page.

    For POST request: this endpoint will render the User Search Result page after running the query with the data specified from the form.

    Returns:
        HTML -- The User Search page or the User Search Result page based on the request
    """
    # POST method
    if request.method=="POST":
        userID      = request.form.get("user_id")
        username    = request.form.get("username")
        email       = request.form.get("email")
        fname       = request.form.get("fname")
        lname       = request.form.get("lname")
        role        = request.form.get("role")


        users = db.session.query(User).filter(or_(User.id   == userID, 
                                                User.username   == username,
                                                User.email      == email,
                                                User.fname      == fname,
                                                User.lname      == lname,
                                                User.role       == role)).all()
        
        result = users_schema.dump(users)

        return render_template('user_search_result.html', users = result)

    # GET method
    return render_template('user_search.html')


# NOT TESTED (waiting on templates/other implementation)
# Endpoint to update car info
@api.route("/car/update/<car_id>", methods = ["GET","POST"])
def updateCarInfo(car_id):
    """
    For GET request: 
    
        - This endpoint will render the Update Car Info page

        - When the Admin have searched and selected the right car that he wants to edit the info (from the Car Search Result page), he will be redirect to this endpoint.

        - This endpoint will display a form with the data of the car selected from the previous page fetched in.

        - The admin will edit the fields and submit the form to finalize the car info.


    For POST request: 

        - This endpoint will get the update data from the form

        - A query to find the car with the right Car ID will be exceuted

        - If the car with the right ID is found, update will be applied and redirect the user to the Home page

    Returns:
        HTML -- The Update Car Info page
    """
    # POST method
    if request.method == "POST":
        make            = request.form.get("make")
        body_type       = request.form.get("body_type")
        colour          = request.form.get("colour")
        seats           = request.form.get("seats")
        location        = request.form.get("location")
        cost_per_hour   = request.form.get("cost_per_hour")
        booked          = request.form.get("booked")
        have_issue      = request.form.get("have_issue")

        # Query to find the car with the right car ID 
        car = db.session.query(Car).filter_by(id = car_id).first()

        # Update the fields
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

            # Use get_flashed_message() to debug if the car info is updated
            flash("Updated Car")

            # After updating, the Admin will be redirect back to the Home page
            return redirect(url_for('site.homePage'))


    # GET method
    # Search for the car to fetch the data in to the form for Admin
    car = Car.query.filter_by(id = car_id).first()

    result = car_schema.dump(car)

    return render_template('update_car_info.html', data = result)


# NOT TESTED (waiting on templates/other implementation)
# Endpoint to update user info
@api.route("/user/update/<user_id>", methods = ["GET","POST"])
def updateUserInfo(user_id):
    """
    For GET request: 
    
        - This endpoint will render the Update User Info page

        - When the Admin have searched and selected the right user that he wants to edit the info (from the User Search Result page), he will be redirect to this endpoint.

        - This endpoint will display a form with the data of the user selected from the previous page fetched in.

        - The admin will edit the fields and submit the form to finalize the user info.


    For POST request: 

        - This endpoint will get the update data from the form

        - A query to find the user with the right User ID will be exceuted

        - If the user with the right ID is found, update will be applied and redirect the user to the Home page

    Returns:
        HTML -- The Update User Info page
    """
    # PUT method
    if request.method=="POST":
        username    = request.form.get("username")
        email       = request.form.get("email")
        fname       = request.form.get("fname")
        lname       = request.form.get("lname")
        role        = request.form.get("role")
        device      = request.form.get("device")

        # Query to find the user with the right user ID 
        user = db.session.query(User).filter_by(id = user_id).first()

        # Update the fields
        if user is not None:
            user.username    = username
            user.email       = email
            user.fname       = fname
            user.lname       = lname
            user.role        = role
            user.device      = device

            # Commit changes
            db.session.commit()

            # Use get_flashed_message() to debug if the car info is updated
            print("Updated User")

            # After updating, the Admin will be redirect back to the Home page
            return redirect(url_for('site.homePage'))

    # GET method
    # Search for the car to fetch the data in to the form for Admin
    user = User.query.filter_by(id = user_id).first()

    result = user_schema.dump(user)

    return render_template('update_user_info.html', data = result)


# NOT TESTED (waiting on templates/other implementation)
# Endpoint to show cars that have issue
@api.route("/car/issue", methods = ["GET"])
def showIssueCars():
    """
    This endpoint will access Cars table to retrieve rows with have_issue column that are set to True.

    These rows will be showed on the Home page for Engineer.

    Returns:
        JSON -- All cars in the Cars table with issue
    """
    cars = Car.query.filter_by(have_issue = True).all()

    result = cars_schema.dump(cars)

    return jsonify(result)

# NOT TESTED (waiting on templates/other implementation)
# Endpoint to search for cars using VOICE RECOGNITION
@api.route("/car/search/voice", methods = ["GET", "POST"])
def carVoiceSearch():
    """
    To search for cars with voice recognition:
        - The keywords will be submitted using a POST method
        - The string of keywords will then be splited and each keyword will be searched in the database 
        - For each row found with the keyword, it will be added to a list called 'found'
        - After searching for all the keywords, the 'found' list will be filtered to remove duplicating rows
        - After filtered, the result will be returned in a jsonified object
    """
    # POST method
    if request.method=="POST":
        # Retrieve string of keywords
        keywords = request.form.get("keywords")

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
        
        result = cars_schema.dump(filtered)
        
        return jsonify(result)



# NOT TESTED!
# Endpoint for the admin to report cars
@api.route("/car/report/<car_id>", methods = ["POST","GET"])
def reportCar(car_id):
    """
    This endpoints will execute when the 'Report' button in the Report Issue Car page is clicked.
    It will use the Car ID got from that row of data to retrieve the car and set the 
    have_issue argument from 0 to 1 (False to True) and doesn't change anything when the have_issue argument is already True.

    - Argument: int - car_id

    For GET request: This endpoint will render the page Car Report Issue.

    For POST request: This endpoint update the have_issue attribute for the car that as car_id matching the argument, then it will send push notification to Engineer phone via Push buttlet with defined ACCESS TOKEN then return to Admin Home Page.

     Returns:
        HTML -- Report Car Page or Admin Home Page

    """
    # POST method
    if request.method == 'POST':
        car_id    = request.form.get("car_id")

        car = db.session.query(Car).filter_by(id = car_id).first()
        
        if (car.have_issue == 1):
            print("Error! This car was already reported for having issue!")
        else:
            car.have_issue = 1

        # Commit changes
        db.session.commit()
        flash("Reported issue")

        #Send notification to Engineer Phone
        message1 = "Issue with car number {}: ".format(car_id)
        message2 = request.form.get("issue_description")
        message = message1 + message2
        ip_address = os.popen('hostname -I').read()
        data_send = {"type": "note", "title": ip_address, "body": message}
 
        resp = requests.post('https://api.pushbullet.com/v2/pushes', data=json.dumps(data_send),
                         headers={'Authorization': 'Bearer ' + ACCESS_TOKEN, 
                         'Content-Type': 'application/json'})
        if resp.status_code != 200:
            raise Exception('Something wrong')
        else:
            print('complete sending')
        return redirect(url_for('site.homePage'))
        
    # GET method
    return render_template('car_report_issue.html', car_id = car_id)
  

# NOT TESTED (waiting on templates/other implementation)
# Endpoint to get trusted Bluetooth MAC addresses of the Engineers from Users table
@api.route("/user/engineer/device", methods = ["GET"])
def getMACs():
    """
    This endpoint will access Users table to retrieve the trusted Bluetooth MAC addresses of the Engineers (from the 'device' column).

     Returns:
        list of str -- A list of Engineers' trusted Bluetooth MAC addresses
    """
    users = User.query.filter_by(role = "Engineer").all()

    if users is not None:
        addresses = [usr.device for usr in users]   # Get the device addresses and put them in a list

        return json.dumps(addresses)
    else: return None


# Endpoint to show all cars
@api.route("/car/all", methods = ["GET"])
def getAllCars():
    """
    This endpoint will access Cars table to retrieve all rows.

     Returns:
        JSON -- All cars in the Cars table   
    """

    cars = Car.query.all()

    result = cars_schema.dump(cars)

    return jsonify(result)


# Endpoint to search for cars of Admin
@api.route("/car/search_admin", methods = ["GET", "POST"])
def carSearchAdmin():
    """

    For GET request: this endpoint will render the Car Search page for Admin.

    For POST request: this endpoint will render the Car Search Result page after running the query with the data specified from the form.
    
    To search for cars:
        - Filters will be declared from form data
        - A query with OR conditions will be executed to find the filtered cars
        - The result will be displayed on the page

    Returns:
        HTML -- The Update Car Info page

    """

    if request.method=="POST":
        _id             = request.form.get("id")
        make            = request.form.get("make")
        body_type       = request.form.get("body_type")
        colour          = request.form.get("colour")
        seats           = request.form.get("seats")
        location        = request.form.get("location")
        cost_per_hour   = request.form.get("cost_per_hour")
        booked          = request.form.get("booked")        # if this field is null, it's equivalent to 0 (False)
        have_issue      = request.form.get("have_issue")    # if this field is null, it's equivalent to 0 (False) 

        cars = db.session.query(Car).filter(or_(Car.id              == _id, 
                                                Car.make            == make,
                                                Car.body_type       == body_type,
                                                Car.colour          == colour,
                                                Car.seats           == seats,
                                                Car.location        == location,
                                                Car.cost_per_hour   == cost_per_hour,
                                                Car.booked          == booked,
                                                Car.have_issue      == have_issue)).all()
        
        result = cars_schema.dump(cars)
        return render_template('car_search_result_update.html', cars = result)
    return render_template('car_search.html')