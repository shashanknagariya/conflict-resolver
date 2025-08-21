from flask import Flask, render_template, request, redirect, url_for, session
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# Tell Flask to look for templates and static files in root dir
app = Flask(__name__, template_folder=".", static_folder=".")
app.secret_key = os.urandom(24)


@app.route("/")
def home():
    logging.debug("Home page accessed")
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    logging.debug("Login route accessed, method: %s", request.method)

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        logging.debug("Login attempt with username: %s", username)

        if username == "admin" and password == "password":
            session["user"] = username
            logging.info("Login successful for user: %s", username)
            return redirect(url_for("dashboard"))
        else:
            logging.warning("Invalid login attempt for user: %s", username)
            return "Invalid Credentials", 401

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    logging.debug("Dashboard route accessed")
    if "user" not in session:
        logging.warning("Unauthorized dashboard access attempt")
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])


@app.route("/logout")
def logout():
    user = session.pop("user", None)
    logging.info("User logged out: %s", user)
    return redirect(url_for("login"))


if __name__ == "__main__":
    logging.info("Starting Flask app")
    app.run(debug=True)
