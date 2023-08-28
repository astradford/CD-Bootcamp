from flask import flash, redirect, render_template, request, session
from flask_app import app
from flask_app.models.givers import Giver


# Home page #
@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

# Login page #


@app.route("/login", methods=['GET'])
def login():
    return render_template("login.html")

# Dashboard page#


@app.route("/dashboard", methods=['GET'])
def giverdash():
    print("in the giverdash")
    return render_template("giverdash.html")


# Account registration form submission - upon verifying criteria met #
@app.route("/register", methods=['POST'])
def register_user():
    validation_response = Giver.validate_giverregistration(request.form)
    print("Validation Response:", validation_response)

    is_valid = validation_response.get('is_valid', False)

    if not is_valid:
        return redirect("/")

    data = {
        'account_type': request.form['account_type'],
        'gfname': request.form['gfname'],
        'glname': request.form['glname'],
        'gemail': request.form['gemail'],
        'gpass': request.form['gpass'],
        'gauth': request.form['gauth']
    }
    print("Data Dictionary:", data)
    new_user_id = Giver.create(data)
    print("New User ID:", new_user_id)

    session['gid'] = new_user_id
    session['gfname'] = request.form['gfname']

    return redirect("/dashboard")


# Login form submission - upon verifying criteria met #
@app.route("/login_user", methods=['POST'])
def login_user():
    login_data = {
        'gemail': request.form['gemail'],
        # removed bcrypt due to issue after installing latest flask version
        'gpass': request.form['gpass']
    }
    validation_result = Giver.validate_giverlogin(login_data)
    is_valid = validation_result.get('is_valid', False)
    if not is_valid:
        return redirect('/')

    user = validation_result.get('givers', None)
    if user is None:
        return redirect('/')

    session['gid'] = 'id'
    session['gfname'] = user['gfname']

    return redirect("/dashboard")


# Routing for logging out partner and clearing session #
@app.route("/logout", methods=['GET'])
def logout():
    session.clear()
    return redirect("/login")


# Routing 404s #
@app.errorhandler(404)
def page_not_found(e):
    return redirect("/")


# Clear session for testing #
@app.route('/clear_session', methods=['GET'])
def clear_session():
    session.clear()
    return "Session cleared"
