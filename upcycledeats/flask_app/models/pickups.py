from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models.partners import Partner
from flask_app.models.givers import Giver
from datetime import datetime
import re

DB_NAME = 'upcycledeats_db'

# Regex rules for validation #
THREE_CHAR_REGEX = re.compile(r'^[a-zA-Z]{3}')
ZIP_REGEX = re.compile(r'^[0-9]{5}')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PHONE_REGEX = re.compile(r'^(?:\+1\s?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$')
ADDRESS_REGEX = re.compile(r'[0-9].*[a-zA-Z]|[a-zA-Z].*[0-9]')


# Defining Pickups data dictionary #
class Pickups:
    def __init__(self, data):
        self.id = data['id']
        self.p_id = data['p_id']
        self.g_id = data['g_id']
        self.m_created = data['m_created']
        self.m_updated = data['m_updated']
        self.loc_name = data['loc_name']
        self.loc_address = data['loc_address']
        self.loc_city = data['loc_city']
        self.loc_state = data['loc_state']
        self.loc_zip = data['loc_zip']
        self.loc_phone = data['loc_phone']
        self.pref_partnertype = data['pref_partnertype']
        self.sched_days = data['sched_days']
        self.sched_starthrs = data['sched_starthrs']
        self.sched_endhrs = data['sched_endhrs']
        self.instructions = data['instructions']


# Creating a new location record for potential pickup #


    @ classmethod
    def create(cls, data):
        print("Inside Pickups.create().")
        print(f"Data to insert: {data}")
        query = '''
                INSERT INTO pickups (g_id,loc_name,loc_address,loc_city, loc_phone, loc_state,loc_zip,pref_partnertype,sched_days,sched_starthrs, sched_endhrs, instructions, logo)
                VALUES (%(g_id)s,%(loc_name)s,%(loc_address)s,%(loc_city)s, %(loc_phone)s,%(loc_state)s,%(loc_zip)s,%(pref_partnertype)s,%(sched_days)s,%(sched_starthrs)s,%(sched_endhrs)s,%(instructions)s,%(logo)s);
                '''
        print(f"Executing query: {query}")

        return connectToMySQL(DB_NAME).query_db(query, data)


# Retrieving all pickups, merge with givers and partners #


    @classmethod
    def get_all(cls):
        query = """
            SELECT * FROM pickups
            LEFT JOIN givers ON pickups.g_id = givers.gid
            LEFT JOIN partners ON pickups.p_id = partners.pid
            ORDER BY pickups.id DESC;
        """
        request_query_pickups = connectToMySQL(DB_NAME).query_db(query)

        if request_query_pickups is False:
            print("Query failed")
            return []

        data = []

        for pickup_data in request_query_pickups:
            partner_data = {
                'pid': pickup_data['pid'],
                'p_name': pickup_data['p_name'],
                'p_type': pickup_data['p_type'],
                'p_address': pickup_data['p_address'],
                'p_city': pickup_data['p_city'],
                'p_state': pickup_data['p_state'],
                'p_zip': pickup_data['p_zip'],
                'p_con_fname': pickup_data['p_con_fname'],
                'p_con_lname': pickup_data['p_con_lname'],
                'p_con_phone': pickup_data['p_con_phone'],
                'p_con_email': pickup_data['p_con_email'],
                'p_con_password': pickup_data['p_con_password'],
                'p_logo': pickup_data['p_logo'],
                'p_auth': pickup_data['p_auth'],
                'p_created': pickup_data['p_created'],
                'p_updated': pickup_data['p_updated'],
                'p_accounttype': pickup_data['p_accounttype']
            }

            giver_data = {
                'gid': pickup_data['gid'],
                'gauth': pickup_data['gauth'],
                'gfname': pickup_data['gfname'],
                'glname': pickup_data['glname'],
                'gphone': pickup_data['gphone'],
                'gemail': pickup_data['gemail'],
                'gpass': pickup_data['gpass'],
                'account_type': pickup_data['account_type'],
                'gcreated': pickup_data['gcreated'],
                'gupdated': pickup_data['gupdated']
            }

            pickup_data = {
                'id': pickup_data['id'],
                'p_id': pickup_data['p_id'],
                'g_id': pickup_data['g_id'],
                'm_created': pickup_data['m_created'],
                'm_updated': pickup_data['m_updated'],
                'loc_name': pickup_data['loc_name'],
                'loc_address': pickup_data['loc_address'],
                'loc_city': pickup_data['loc_city'],
                'loc_state': pickup_data['loc_state'],
                'loc_zip': pickup_data['loc_zip'],
                'loc_phone': pickup_data['loc_phone'],
                'pref_partnertype': pickup_data['pref_partnertype'],
                'sched_days': pickup_data['sched_days'],
                'sched_starthrs': pickup_data['sched_starthrs'],
                'sched_endhrs': pickup_data['sched_endhrs'],
                'instructions': pickup_data['instructions'],
            }

            pickup = cls(pickup_data)
            partner = Partner(partner_data)
            giver = Giver(giver_data)

            pickup.partner = partner
            pickup.giver = giver

            data.append(pickup)

        return data


# Retrieving all locations associated with one giver  #


    @classmethod
    def get_pickups_by_giver_id(cls, giver_id):
        query = "SELECT * FROM pickups WHERE g_id = %(giver_id)s;"
        data = {
            'giver_id': giver_id
        }
        results = connectToMySQL(DB_NAME).query_db(query, data)
        pickups = []
        for result in results:
            pickups.append(cls(result))
        return pickups

# Get one location listing
    @staticmethod
    def get_one(id):
        query = "SELECT * FROM pickups WHERE id = %(id)s;"
        data = {'id': id}
        response_query_user = connectToMySQL(DB_NAME).query_db(query, data)
        if response_query_user:
            return response_query_user[0]
        else:
            return None


# Retrieving all pickups associated with one partner #


    @classmethod
    def get_pickups_by_partner_id(cls, partner_id):
        query = "SELECT * FROM pickups WHERE p_id = %(partner_id)s;"
        data = {
            'partner_id': partner_id
        }
        results = connectToMySQL(DB_NAME).query_db(query, data)
        pickups = []
        for result in results:
            pickups.append(cls(result))
        return pickups

# Updating one location by id #
    @classmethod
    def update_one(cls, id, data):
        query = '''
            UPDATE pickups
            SET loc_name = %(loc_name)s, loc_address = %(loc_address)s, loc_city = %(loc_city)s, loc_state = %(loc_state)s, 
            loc_zip = %(loc_zip)s, pref_partnertype = %(pref_partnertype)s, 
            sched_days = %(sched_days)s, sched_starthrs = %(sched_starthrs)s, 
            sched_endhrs = %(sched_endhrs)s, loc_phone = %(loc_phone)s,instructions = %(instructions)s
            WHERE id = %(id)s;
        '''
        data['id'] = id
        return connectToMySQL(DB_NAME).query_db(query, data)


# Deleting one location by id #


    @classmethod
    def delete_one(cls, id):
        query = "DELETE FROM pickups WHERE pickups.id=%(id)s;"
        return connectToMySQL(DB_NAME).query_db(query, {'id': id})


# Validating a giver in session created a location and is eligible to update/delete it


    @staticmethod
    def validate_giver_creator(giver_id, pickup_id):
        query = "SELECT g_id FROM pickups WHERE id = %(pickup_id)s;"
        data = {
            'pickup_id': pickup_id
        }
        result = connectToMySQL(DB_NAME).query_db(query, data)
        if result and result[0]['g_id'] == giver_id:
            return True
        return False


# Validate new listing details for giver #


    @staticmethod
    def validate_listingdetails(publish):
        print("Inside validate_listingdetails().")
        print(f"Data to validate: {publish}")

        is_valid = True
        print(publish)
        if not THREE_CHAR_REGEX.match(publish['loc_name']):
            flash('Company name must contain at least 3 letters.', 'publish')
            is_valid = False
        if not PHONE_REGEX.match(publish['loc_phone']):
            flash('Phone number must contain 7 digits.', 'publish')
            is_valid = False
        if not ADDRESS_REGEX.match(publish['loc_address']):
            flash('Street address must be properly formatted.', 'publish')
            is_valid = False
        if not THREE_CHAR_REGEX.match(publish['loc_city']):
            flash('City must contain at least 3 letters.', 'publish')
            is_valid = False
        loc_state = publish.get('loc_state', None)
        if loc_state == 'State':
            flash('State must be selected.', 'publish')
            is_valid = False
        if not ZIP_REGEX.match(publish['loc_zip']):
            flash('Zip must contain at least 3 digits.', 'publish')
            is_valid = False
        if not publish.get('sched_days'):
            flash('You must select pickup day(s).', 'publish')
            is_valid = False
        if publish.get('sched_starthrs') in [None, '', '-:--']:
            flash('Please select a pickup start time.', 'publish')
            is_valid = False
        if publish.get('sched_endhrs') in [None, '', '-:--']:
            flash('Please select a pickup end time.', 'publish')
            is_valid = False
        if publish.get('instructions') in [None, '']:
            flash('Please add instructions.', 'publish')
            is_valid = False

        return is_valid

# Explore saving down a file


def save_logo_filepath(filepath, id):
    query = "UPDATE pickups SET logo = %(filepath)s WHERE id = %(id)s;"
    data = {'filepath': filepath, 'id': id}
    connectToMySQL(DB_NAME).query_db(query, data)
