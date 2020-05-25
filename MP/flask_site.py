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


# Home page
@site.route('/home')
def homePage():
    """Display Home page. This page is where the user has successfully logged in and grant access to the application

    Returns:
        .html -- The Home page of the web application
    """
    response = requests.get("http://127.0.0.1:5000/car/unbooked")
    data = json.loads(response.text)
    return render_template('home.html', cars = data)


# Car Search page
@site.route('/car/search')
def carSearchPage():
    """Display Car Search page with fields of filters for the user to search with

    Returns:
        .html -- The Car Search page of the web application
    """
    return render_template('car_search.html')
