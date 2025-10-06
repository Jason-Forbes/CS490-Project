# app/routes.py

# This file defines the URL routes (pages) for our Flask app.
# Each route is connected to a Python function that tells Flask
# what HTML template to render when someone visits that URL.
from flask import Blueprint, render_template


# Create a Blueprint named 'main'.
# A Blueprint is a way to organize routes so we can keep our app modular and clean.
# Think of it as a group of related pages.
main_bp = Blueprint('main', __name__)

# Route for the home page ("/")
@main_bp.route("/")
def home():
    return render_template("login.html")



