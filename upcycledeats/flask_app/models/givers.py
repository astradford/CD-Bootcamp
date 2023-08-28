from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL
import re


DB_NAME = 'upcycledeats_db'

THREE_CHAR_REGEX = re.compile(r'^[a-zA-Z]{3}')
EIGHT_CHAR_REGEX = re.compile(r'^[a-zA-Z]{8}')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]{7}')


# Defining Giver data dictionary #

class Giver:
    def __init__(self, data):
        self.gid = data['gid']
        self.gfname = data['gfname']
        self.glname = data['glname']
        self.gphone = data['gphone']
        self.gemail = data['gemail']
        self.gpass = data['gpass']
        self.gauth = data['gauth']
        self.account_type = data['account_type']
        self.gcreated = data['gcreated']
        self.gupdated = data['gupdated']


# Registering a new giver account #

    @classmethod
    def create(cls, data):
        # need to convert to fit database record format as a tinyint(1)
        data['gauth'] = 1 if data.get('gauth') == 'on' else 0

        query = '''
                INSERT INTO givers (gfname, glname, gemail, gpass, gauth, account_type)
                VALUES (%(gfname)s,%(glname)s,%(gemail)s,%(gpass)s,%(gauth)s,%(account_type)s);
                '''
        return connectToMySQL(DB_NAME).query_db(query, data)


# Retrieveing all givers #

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM givers;"
        results = connectToMySQL(DB_NAME).query_db(query)
        givers = []
        for giver in results:
            givers.append(cls(giver))
        return givers


# Get one giver by email #

    @classmethod
    def get_giver_by_email(cls, data):
        query = '''
                SELECT * FROM givers WHERE gemail = %(gemail)s
                '''
        results = connectToMySQL(DB_NAME).query_db(query, data)
        if len(results) < 1:
            return False
        # return cls(*results)
        return cls(results[0]) if results else None


# Validate registration details for giver #

    @staticmethod
    def validate_giverregistration(register):
        query = '''
                SELECT * FROM givers WHERE gemail=%(gemail)s
                '''
        response_query_user = connectToMySQL(DB_NAME).query_db(query, register)

        print("Register data:", register)
        print("Response query user:", response_query_user)

        is_valid = True
        if register['account_type'] == 'Select Account Type':
            flash("Account type must be selected.", "register")
            is_valid = False
        if not THREE_CHAR_REGEX.match(register['gfname']):
            flash("First name must contain at least 3 letters.", 'register')
            is_valid = False
        if not THREE_CHAR_REGEX.match(register['glname']):
            flash("Last name must contain at least 3 letters.", 'register')
            is_valid = False
        if not EMAIL_REGEX.match(register['gemail']):
            flash("Email is formatted incorrectly.", 'register')
            is_valid = False
        if not PASSWORD_REGEX.match(register['gpass']):
            flash("Password must contain at least 7 characters.", 'register')
            is_valid = False
        if 'gauth' not in register or register['gauth'] != "on":
            flash('You must certify your authority.', 'register')
            is_valid = False
        if len(response_query_user) >= 1:
            flash(
                "This email address has already been registered. Log In.", 'register')
            is_valid = False

        print("Register data:", register)
        print("Response query user:", response_query_user)
        return {'is_valid': is_valid}


# Validation of giver login criteria #


    @staticmethod
    def validate_giverlogin(login):
        is_valid = True
        query = '''
                SELECT * FROM givers WHERE gemail=%(gemail)s and gpass=%(gpass)s
                '''
        response_query_user = connectToMySQL(DB_NAME).query_db(query, login)

        print("Register data:", login)
        print("Response query user:", response_query_user)

        if not len(response_query_user) >= 1:
            flash("The email and/or password entered does not exist.", "login")
            is_valid = False
            return {'giver': response_query_user, 'is_valid': is_valid}

        return {'givers': response_query_user[0], 'is_valid': is_valid}
