from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL
import re

# Was unable to finish this side of the platform, focused on givers #

DB_NAME = 'upcycledeats_db'

TWO_CHAR_REGEX = re.compile(r'^[a-zA-Z]{2}')
THREE_CHAR_REGEX = re.compile(r'^[a-zA-Z]{3}')
EIGHT_CHAR_REGEX = re.compile(r'^[a-zA-Z]{8}')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]{7}')


# Defining Partner data dictionary #

class Partner:
    def __init__(self, data):
        self.pid = data['pid']
        self.p_name = data['p_name']
        self.p_type = data['p_type']
        self.p_address = data['p_address']
        self.p_city = data['p_city']
        self.p_state = data['p_state']
        self.p_zip = data['p_zip']
        self.p_con_fname = data['p_con_fname']
        self.p_con_lname = data['p_con_lname']
        self.p_con_phone = data['p_con_phone']
        self.p_con_email = data['p_con_email']
        self.p_con_password = data['p_con_password']
        self.p_logo = data['p_logo']
        self.p_auth = data['p_auth']
        self.p_created = data['p_created']
        self.p_updated = data['p_updated']
        self.p_accounttype = data['p_accounttype']


# Registering a new partner account #


    @classmethod
    def create(cls, data):
        query = '''
                INSERT INTO partners (p_name, p_type, p_address, p_city, p_state, p_zip, p_con_fname, p_con_lname, p_con_phone, p_con_email, p_con_password, p_logo, p_auth, p_accounttype)
                VALUES (%(p_name)s,%(p_type)s,%(p_address)s,%(p_city)s,%(p_state)s,%(p_zip)s,%(p_con_fname)s,%(p_con_lname)s,%(p_con_phone)s,%(p_con_email)s,%(p_con_password)s,%(p_logo)s,%(p_auth)s,%(p_accounttype)s);
                '''
        return connectToMySQL(DB_NAME).query_db(query, data)


# Retrieveing all partners #


    @classmethod
    def get_all(cls):
        query = "SELECT * FROM partners;"
        results = connectToMySQL(DB_NAME).query_db(query)
        partners = []
        for partner in results:
            partners.append(cls(partner))
        return partners


# Get one partner by email #


    @classmethod
    def get_partner_by_email(cls, data):
        query = '''
                SELECT * FROM partners WHERE email = %(email)s
                '''
        results = connectToMySQL(DB_NAME).query_db(query, data)
        if len(results) < 1:
            return False
        return cls(*results)


# Valdate registration details for partner #

    @staticmethod
    def validate_partnerregistration(register):
        query = '''
                SELECT * FROM partners WHERE email=%(email)s
                '''
        response_query_user = connectToMySQL(DB_NAME).query_db(query, register)

        is_valid = True
        print(register)
        if register['account_type'] == 'food_pantry' or register['account_type'] == 'shelter' or register['account_type'] == 'farm' or register['account_type'] == 'compost_company':
            if not THREE_CHAR_REGEX.match(register['company_name']):
                flash('Company names must contain at least 3 letters.', 'register')
                is_valid = False
            if not EMAIL_REGEX.match(register['fname']):
                flash("Your email is formatted incorrectly.", 'register')
                is_valid = False
            if not EMAIL_REGEX.match(register['lname']):
                flash("Your email is formatted incorrectly.", 'register')
                is_valid = False
            if not EMAIL_REGEX.match(register['email']):
                flash("Your email is formatted incorrectly.", 'register')
                is_valid = False

        return is_valid


# Validation of login criteria #


    @staticmethod
    def validate_partnerlogin(login):
        is_valid = True
        query = '''
                SELECT * FROM partners WHERE email=%(email)s
                '''
        response_query_user = connectToMySQL(DB_NAME).query_db(query, login)

        if not len(response_query_user) >= 1:
            flash("The email entered does not exist.", "login")
            is_valid = False
            return {'partner': response_query_user, 'is_valid': is_valid}

        return {'partner': response_query_user[0], 'is_valid': is_valid}
