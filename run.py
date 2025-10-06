from app import create_app


# This is the entry point of the Flask application.
# When you run `python run.py`, it will start the web server
# and launch the app in your browser.
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
