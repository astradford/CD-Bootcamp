from flask_app import app
from flask_app.controllers import pickups
from flask_app.controllers import givers

if __name__ == "__main__":
    app.run(debug=True, port=5700)
