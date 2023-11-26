from uuid import uuid4
from abbrefy import bcrypt, mongo
from datetime import datetime
from flask import session
from abbrefy.links.models import Link
import safe


# the User class
class User:
    # initializing the class
    def __init__(self, username=None, email=None, password=None):
        self.username = username
        self.email = email
        self.password = password
        self.url = 'https://abbrefy.xyz/me/dashboard/'

    # signup helper function
    def signup(self):

        try:
            user = {
                'public_id': uuid4().hex,
                'username': self.username.lower(),
                'email': self.email.lower(),
                'password': bcrypt.generate_password_hash(
                    self.password).decode('utf-8'),
                'join_date': datetime.utcnow()
            }

            mongo.db.users.insert_one(user)

            new_link = Link(url=self.url,
                            author=user['public_id'])
            response = new_link.abbrefy()

        except:
            return False

        return True

    # creating a user session
    @staticmethod
    def init_session(user):
        session['is_authenticated'] = True
        del user['password']
        del user['_id']
        session['current_user'] = user
        session.permanent = True
        return user

    # signin helper function
    def signin(self, signin_data):
        # querying user from db with username
        user = mongo.db.users.find_one(
            {"username": signin_data['identifier'].lower()})

        # validating user and password
        if user and bcrypt.check_password_hash(user["password"], signin_data['password']):
            return self.init_session(user)

        else:
            # querying user from db  with email
            user = mongo.db.users.find_one(
                {"email": signin_data['identifier'].lower()})

            # validating user and password
            if user and bcrypt.check_password_hash(user["password"], signin_data['password']):
                return self.init_session(user)

        return False

    # signout helper function
    @staticmethod
    def signout():
        if session['is_authenticated'] and session['current_user']:
            session['is_authenticated'] = False
            del session['current_user']
        return True

    # send password reset helper function@
    def reset_password(self, email):
        user = self.check_email(email)
        send_mail(user['public_id'], user['email'])
        return True

    # email validator helper function
    @staticmethod
    def check_email(email):
        return mongo.db.users.find_one({"email": email.lower()})

    # username validator helper function
    @staticmethod
    def check_username(username):
        return mongo.db.users.find_one({"username": username.lower()})

    # link retrieval helper function
    @staticmethod
    def my_links(user):
        links = mongo.db.links.find(
            {"author": user}).sort('date_created', -1)
        return links

    # link retrieval helper function
    @staticmethod
    def my_links_asc(user):
        links = mongo.db.links.find(
            {"author": user})
        return links

    # user retrieval helper function
    @staticmethod
    def get_user(public_id):
        return mongo.db.users.find_one({"public_id": public_id})

    # update password helper function
    def update_password(self, id, password):
        try:
            updateData = {}
            user = self.get_user(id)
            # encrypting the new password
            newPassword = bcrypt.generate_password_hash(
                password).decode("utf-8")
            updateData["password"] = newPassword
            # creating the update and commiting to the DB
            if len(updateData) > 0:
                update = {"$set": updateData}
                filterData = {'public_id': user['public_id']}
                mongo.db.users.update_one(filterData, update)
            return True
        # handling exception
        except:
            return False

    # profile update helper function
    def update_profile(self, id, data):
        try:
            updateData = {}
            user = self.get_user(id)
            for key in data:
                # checking for username change
                if key == "usernameData":
                    if user['username'] == data[key]:
                        continue
                    updateData["username"] = data[key]
                # checking for password change
                if key == "passwordData":
                    if not (bcrypt.check_password_hash(user['password'], data[key]['oldPassword'])):
                        return False
                    strong = safe.check(data[key]['newPassword'])
                    if not strong:
                        return True
                    newPassword = bcrypt.generate_password_hash(
                        data[key]['newPassword']).decode("utf-8")
                    updateData["password"] = newPassword

            # creating the update and commiting to the DB
            if len(updateData) > 0:
                update = {"$set": updateData}
                filterData = {'public_id': user['public_id']}
                mongo.db.users.update_one(filterData, update)

            # getting the new data of the user
            userUpdate = self.get_user(id)
            # starting a new session for the user
            userData = self.init_session(userUpdate)

            response = {
                "status": True,
                "message": "Your profile has been updated successfully",
                "userData": userData
            }

        except:
            response = {
                "status": False,
                "error": "Something went wrong. Please try again."
            }
            # return response
        return response

    # generate API Key helper function
    def generate_api_key(self, id):

        try:
            # getting the user object
            user = self.get_user(id)
            # retrieving all the user's API keys
            userKeys = self.get_keys(user['public_id'])
            # validating user hasn't created more than 2 API keys
            if userKeys.count() >= 2:
                return False

            # creating the API key object
            key = {
                "author": user['public_id'],
                "apiKey": uuid4().hex,
                "dateCreated": datetime.utcnow()
            }
            # adding the API key to the database
            mongo.db.keys.insert(key)

            del key["_id"]

        except:

            response = {
                "status": False,
                "message": "Something went wrong. Please try again."
            }

            return response

        response = {
            "status": True,
            "message": "API Key successfully generated",
            "apiData": key
        }
        return response

    # retrieve API Key helper function
    @staticmethod
    def get_key_owner(key):
        key = mongo.db.keys.find_one({"apiKey": key})
        if key:
            return key['author']
        return None

    # retrieve all API Key helper function
    @staticmethod
    def get_keys(user):
        return mongo.db.keys.find({"author": user})

    # retrieve one API Key helper function
    @staticmethod
    def get_key(user):
        return mongo.db.keys.find_one({"author": user})['apiKey']

    # delete API Key helper function
    def delete_api_key(self, user, key):
        try:
            # getting the key owner
            author = self.get_key_owner(key)

            if author != user:
                return False

            # deleting the API key from the database
            mongo.db.keys.delete_one({"apiKey": key})

        except:

            response = {
                "status": False,
                "message": "Something went wrong. Please try again."
            }

            return response

        response = {
            "status": True,
            "message": "API Key successfully deleted",
        }
        return response


from abbrefy.users.tools import send_mail
