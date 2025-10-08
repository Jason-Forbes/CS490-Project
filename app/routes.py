# app/routes.py

# This file defines the URL routes (pages) for our Flask app.
# Each route is connected to a Python function that tells Flask
# what HTML template to render when someone visits that URL.
from flask import Blueprint, render_template, request, jsonify
from app.authentication import supabase 


# Create a Blueprint named 'main'.
# A Blueprint is a way to organize routes so we can keep our app modular and clean.
# Think of it as a group of related pages.
main_bp = Blueprint('main', __name__)

# Route for the home page ("/")
@main_bp.route("/")
def home():
    return render_template("signup.html")


@main_bp.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    try:
        # Create Supabase account
        result = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        # If successful, return a success response
        if result.user:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "Sign-up failed. Please try again."})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
