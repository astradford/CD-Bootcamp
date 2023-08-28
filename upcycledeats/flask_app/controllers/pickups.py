from flask import flash, render_template, request, session, url_for, redirect
from flask_app import app
from flask_app.models.pickups import Pickups, save_logo_filepath
from flask_app.models.partners import Partner
from datetime import datetime, timedelta
import locale
import os
from werkzeug.utils import secure_filename


# Dashboard - access upon verification of active session #
@app.route("/dashboard", methods=['GET'])
def dashboard():
    # checking for session #
    giver_id = session.get('gid')
    if not giver_id:
        return redirect('/logout')

    # pulling locations associated with giver in session #
    locations = Pickups.get_pickups_by_giver_id(giver_id)
    return render_template('giverdash.html', locations=locations)


# Add A Location form submission - upon validation of field criteria met #
@app.route("/new", methods=['GET', 'POST'])
def create():
    print("Session data:", session)
    # checking for session #
    if 'gid' not in session:
        print("gid not in session.")
        return redirect('/logout')

    if request.method == 'POST':
        # getting into the data dictionary #
        data = {
            'loc_name': request.form.get('loc_name', None),
            'loc_address': request.form.get('loc_address', None),
            'loc_city': request.form.get('loc_city', None),
            'loc_state': request.form.get('loc_state', None),
            'loc_zip': request.form.get('loc_zip', None),
            'loc_phone': request.form.get('loc_phone', None),
            'logo': request.files['logo'].read(),
            'pref_partnertype': request.form.get('pref_partnertype', None),
            'sched_days': ','.join(request.form.getlist('sched_days')),
            'sched_starthrs': request.form.get('sched_starthrs', None),
            'sched_endhrs': request.form.get('sched_endhrs', None),
            'instructions': request.form.get('instructions', None),
            'm_created': datetime.now(),
            'm_updated': datetime.now(),
            'g_id': session['gid'],
            'id': request.form.get('id', None)
        }

        # debugging the g_id/gid #
        print("Inserting g_id:", session['gid'])

        # listing data validation check and print for debugging #
        is_valid = Pickups.validate_listingdetails(data)
        print(f"Is form valid? : {is_valid}")

        # debiugging and redirect to create new with errors if validation fails #
        if not is_valid:
            print("Form validation failed. Redirecting.")
            flash("Form validation failed.", "validate_location")
            return redirect("/new")

        # successful creation logic or else#
        Pickups.create(data)
        print("Data should now be inserted.")
        flash("Your new location has been added. Yaayy!", "dashboard-success")
        return redirect("/dashboard")
    else:
        return render_template("pickup_add.html")


# View Locations page - access upon verification of active session #
@app.route("/location/<int:id>", methods=['GET'])
def show(id):
    all_pickups = Pickups.get_all()

    location = next(
        (pickup for pickup in all_pickups if pickup.id == id), None)

    if location is not None:
        return render_template('pickup_view.html', location=location, giver=location.giver)
    else:
        print("Debug: location is None!")
        return "Location not found", 404


# Edit a Location page - access upon verification of active session #
@app.route("/location/<int:id>/edit", methods=['GET', 'POST'])
def edit_location(id):
    if 'g_id' not in session:
        print("User not in sesh, redirecting to login")
        return redirect("/logout")

    location = app.session.query(Pickups).filter_by(id=id).first()
    if location is None:
        return "Record not found", 404

    if location.g_id != session['g_id']:
        flash("Sorry, you can only edit locations that you created.",
              "dashboard-alerts")
        return redirect("/dashboard")

    sched_days = location.sched_days
    print("Scheduled Days from DB:", sched_days)
    selected_days = sched_days.split(",") if sched_days else []
    print(f"Selected days are {selected_days}")

    total_seconds = location.sched_starthrs.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    formatted_time = f"{hours:02d}:{minutes:02d}"
    location.sched_starthrs = formatted_time
    location.sched_endhrs = formatted_time

    data = Pickups.get_all()
    location = next((location for location in data if Pickups.pid == id), None)

    if Pickups.pid != session['id']:
        flash("Sorry, you can only edit locations that you created.",
              "dashboard-alerts")
        print("User doesn't have edit rights, redirecting to login")
        return redirect("/dashboard")

    return render_template("pickup_edit.html", location=Pickups, selected_days=selected_days)


# Edit a Location form submission -  upon validation field criteria met #
@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    if 'gid' not in session:
        return redirect("/logout")

    if request.method == 'POST':
        data = {
            'loc_name': request.form.get('loc_name', None),
            'loc_address': request.form.get('loc_address', None),
            'loc_city': request.form.get('loc_city', None),
            'loc_state': request.form.get('loc_state', None),
            'loc_zip': request.form.get('loc_zip', None),
            'loc_phone': request.form.get('loc_phone', None),
            'pref_partnertype': request.form.get('pref_partnertype', None),
            'sched_days': ','.join(request.form.getlist('sched_days')),
            'sched_starthrs': request.form.get('sched_starthrs', None),
            'sched_endhrs': request.form.get('sched_endhrs', None),
            'instructions': request.form.get('instructions', None),
            'm_created': datetime.now(),
            'm_updated': datetime.now(),
            'g_id': session['gid'],
        }

        is_valid = Pickups.validate_listingdetails(data)

        if not is_valid:
            flash("Form validation failed.", "validate_location")
            return redirect(f"/edit/{id}")

        Pickups.update_one(id, data)
        flash("Your location has been edited. Woohoo!", "dashboard-success")
        return redirect("/dashboard")

    location = Pickups.get_one(id)
    return render_template("pickup_edit.html", location=location)


# Delete a Location function - upon validation of ownership #
@ app.route("/location/delete/<int:id>", methods=["POST"])
def delete(id):
    if 'gid' not in session:
        return redirect('/logout')

    location = Pickups.get_one(id)

    if location is None:
        flash("Location not found.", "dashboard-alerts")
        return redirect("/dashboard")

    if location['g_id'] != session['gid']:
        flash("Sorry, you can only delete locations that you created.",
              "dashboard-alerts")
        return redirect("/dashboard")

    Pickups.delete_one(id)
    flash("Success!! Location deleted successfully.", "dashboard-success")
    return redirect("/dashboard")


# Dashboard - view all of own locations
@app.route('/giverdash')
def giver_dashboard():
    locations_and_pickups = Pickups.get_all()
    return render_template('giverdash.html', locations=locations_and_pickups)


# View Location -- exploring saving files to allow rendering a file that was uploaded by a user on view page
UPLOAD_FOLDER = '../static/img/glogo/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        id = session['id']
        save_logo_filepath(filepath, id)

        return redirect(url_for('location'))
