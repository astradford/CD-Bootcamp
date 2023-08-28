from flask import Flask
# (removed encryption due to persistent Bcrypt error after upgrading flask and since not listed in requirements for project)
# from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "mysecretkey"
# bcrypt = Bcrypt(app)
