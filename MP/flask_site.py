from flask import Flask, Blueprint, request, jsonify, render_template, flash, redirect, url_for, session, escape
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os, requests, json
from flask import current_app as app

site = Blueprint("site", __name__)

# CLIENT WEB PAGES

# Welcome page
@site.route('/')
def index():
    """Display Index page

    Returns:
        .html -- The Index page of the web application
    """
    return render_template('index.html')


# Register page
@site.route('/register')
def registerPage():
    """Display Registration page

    Returns:
        .html -- The Registration page of the web application
    """
    return render_template('register.html')


# Login page
@site.route('/login')
def loginPage():
    """Display Login page

    Returns:
        .html -- The Login page of the web application
    """
    return render_template('login.html')


# Home page for Customer
@site.route('/home')
def homePage():
    """Display Home page based on the role of the user. This page is where the user has successfully logged in and grant access to the application.

    There are 4 roles of the user: Customer, Admin, Manager and Engineer

    There is a session variable which is set when the user logged in to identify the role of the user   -   session['role']

    Based on the role, the Home page will differ. For example:
    
    - The Admin will be able to see a list of all the cars so that s/he can report any issue

    - The Manager will be able to see graphs based on the data from the cloud database to make better decision
    
    - The Engineer will be able to see the issue cars that have been reported and see their location with a click
    
    Returns:
        .html -- The Home page of the web application based on the role of the user
    """ 

    user_role = session["role"]
    
    if (user_role == "Admin"):
        response = requests.get("http://127.0.0.1:5000/car/all")
        data = json.loads(response.text)
        return render_template('home_admin.html', cars = data)
    
    elif (user_role == "Customer"):
        response = requests.get("http://127.0.0.1:5000/car/unbooked")
        data = json.loads(response.text)
        return render_template('home.html', cars = data)
    
    elif (user_role == "Engineer"):
        response = requests.get("http://127.0.0.1:5000/car/issue")
        data = json.loads(response.text)
        return render_template('home_engineer.html', cars = data)
    
    elif (user_role == "Manager"):
        return render_template('home_manager.html')
    


# Car Search page
@site.route('/car/search')
def carSearchPage():
    """Display Car Search page with fields of filters for the user to search with

    Returns:
        .html -- The Car Search page of the web application
    """
    return render_template('car_search.html')


@site.route('/showHistories')
def showHistoriesPage():
    """
    This endpoint is for display the page with all the rental histories for the Admin

    Returns:
        .html -- a page with all rental histories 
    """
    response = requests.get("http://127.0.0.1:5000/history")
    data = json.loads(response.text)
    return render_template('show_histories.html', histories = data)