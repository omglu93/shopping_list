import re
import uuid
import jwt
import os
from flask_restful import reqparse, Resource
from src.app_database import UserData, UserCredentials
from werkzeug.security import generate_password_hash,check_password_hash
from flask import request
from datetime import datetime, timedelta
from src.token_val import token_required
from dotenv import load_dotenv
from configuration.config import Configuration


from src.services.email_gen import flask_send_email

load_dotenv(dotenv_path=r'..\configuration\.env')

create_user_args = reqparse.RequestParser()
create_user_args.add_argument("username",
                              type=str,
                              location="json",
                              required=True)

create_user_args.add_argument("e_mail",
                              type=str,
                              location="json",
                              required=True)

create_user_args.add_argument("password",
                              type=str,
                              location="json",
                              required=True)

edit_user_args = reqparse.RequestParser()
edit_user_args.add_argument("first_name",
                            type=str,
                            location="json",
                            required=True)

edit_user_args.add_argument("last_name",
                            type=str,
                            location="json",
                            required=True)

reset_password = reqparse.RequestParser()
reset_password.add_argument("username",
                            type=str,
                            location="json",
                            required=True)

request_new_password = reqparse.RequestParser()
request_new_password.add_argument("new_password",
                                  type=str,
                                  location="json",
                                  required=True)
request_new_password.add_argument("confirm_password",
                                  type=str,
                                  location="json",
                                  required=True)

class CreateUser(Resource):
    
    """ Class used to create and store an user in the database

    Endpoints: /api/v1/create-user
    
    HTTP methods: POST
    """
    
    REGEX_E_MAIL_VALIDATION = re.compile(r"([A-Za-z0-9]+[.-_])" \
                                         r"*[A-Za-z0-9]+@[A-Za-" \
                                         r"z0-9-]+(\.[A-Z|a-z]{2,})+")
    
    
    def __init__(self) -> None:
        
        args = create_user_args.parse_args()
        self.username = args["username"]
        self.e_mail = self._email_validator(args["e_mail"])
        self.password = args["password"]
        self.public_id = str(uuid.uuid4())
        
        
    def _email_validator(self, email):
        """Uses regex to evaulate email

        Args:
            email (str): user provided email

        Returns:
            returns either an email or an error msg for the user
        """
        if re.fullmatch(self.REGEX_E_MAIL_VALIDATION, email):
            return email
        else:
            return {"error" : "E-mail is not valid!"}, 400
        
    def post(self):
        
        """ Stores user input in database
        
        Example request:
            {"username" : "omar",
            "e_mail" : "omargluhic932@gmail.com",
            "password" : "thisisapassword"}
        """

        
        try:
            ### Password validation ###
            if len(self.password) < 8:
                return {"error" : "Password is too short!"}, 400
            
            self.password = generate_password_hash(self.password,
                                                method="pbkdf2:sha256")  

            ### Username validation ###
            
            if len(self.username) < 6:
                return {"error" : "Username is too short!"}, 400
            
            if UserData.query.filter_by(username=self.username).first() is not None:
                return {"error": "Username already taken!"}, 409
            
            ### Email validation ###
            
            if UserData.query.filter_by(email=self.e_mail).first() is not None:
                return {"error": "E-mail already taken!"}, 409
            
            new_user = UserData(self.username,
                                self.e_mail,
                                self.password,
                                self.public_id)
            new_user.save()
            
            user_id = UserData.query.with_entities(UserData.id) \
                                    .filter_by(username=self.username).first()
            
            # Default credentials are Jon and Doe
            # The user can change this in another endpoint               
            user_credentials = UserCredentials(first_name="Jon",
                                               last_name="Doe",
                                               user = user_id[0])
            user_credentials.save()
            
            return {"msg" : "User created!"}, 200
            
        except Exception as e:
            print(e)
            return {"error" : str(e)}, 500
        
        
class UserLogin(Resource):
    
    """ Class used to validate user authorization and
    create/return a token with a 90 minute lifetime

    Endpoints: /api/v1/login
    
    HTTP methods: GET
    """
    
    def __init__(self):
        self.auth = request.authorization

    def get(self):
        
        """ Validates user input and return a token
                
        Example request:
            Authorization header with username and password
        """
        
        try:

            if not self.auth or not self.auth.username or not self.auth.password:
                return {"error" : "Could not verify!"}, 401

            user = UserData.query.filter_by(username=self.auth.username).first()
            if not user:
                return {"error" : "Could not verify!"}, 401
            
            print(Configuration.SECRET_KEY)
            # 90 minute runtime
            if check_password_hash(user.password, self.auth.password):
                # token = jwt.encode({"public_id" : user.public_id,
                #                     "exp" : datetime.utcnow() + timedelta(minutes=90) 
                #                     },key = os.getenv("SECRET_KEY"), algorithm="HS256")
                token = jwt.encode({"public_id" : user.public_id,
                                    "exp" : datetime.utcnow() + timedelta(minutes=90) 
                                    },key = Configuration.SECRET_KEY, algorithm="HS256")   
                Configuration                                  
                return {"token" : token}, 200

            return {"error" : "Could not verify!"}, 401
        
        except Exception as e:
            print(e)
            return {"error" : str(e)}, 500
        
class UserCred(Resource):
    
    """ Class used to update user credentials

    Endpoints: /api/v1/edit-user
    
    HTTP methods: POST
    """
    
    def __init__(self):
        
        args = edit_user_args.parse_args()
        self.first_name = args["first_name"]
        self.last_name = args["last_name"]
        
    @token_required
    def put(self, user):
        """ Updates user credentials (first and last name), token is required
        and it passes the user id to the put function.

        Example request:
        
        {"first_name" : "Omar",
        "last_name" : "Gluhic"}
        """
        
        if self._check_contains_number(self.first_name) == True:
            return {"error": "First name cannot contain number"}, 400
        
        if len(self.first_name) < 2:
            return {"error": "First name too short!"}, 400
        
        if self._check_contains_number(self.last_name) == True:
            return {"error": "Last name cannot contain number"}, 400
        
        if len(self.last_name) < 2:
            return {"error": "Last name too short!"}, 400
        
        try:
            user_data = UserData.query.filter_by(id = user).first()
            
            user_cred = UserCredentials.query.filter_by(user = user_data.id).first()
            
            # Just in case no user credentials are in the database
            if user_cred is None:
                new_name = UserCredentials(first_name=self.first_name,
                                            last_name=self.last_name,
                                            user = user_data.id)
                new_name.save()
            else:
                user_cred.first_name = self.first_name
                user_cred.last_name = self.last_name
                
                user_cred.save()
            return {"msg" : "User info updated!"}, 200
        
        except Exception as e:
            print(e)
            return {"error", str(e)}, 500
    
    def _check_contains_number(self, input_credentials):
        
        """Checks if the string has any numbers and returns
        either True or Flase

        Args:
            input_credentials (str): credentials given

        Returns:
            Boolean
        """
        return bool(re.search(r"\d", input_credentials))


class ForgotPassword(Resource):
    
    """Class that handels the e-mail reset process.
    
    HTTP methods: GET, PUT
    """
    
    def get(self):
        """ Takes a usergiven username and sends a reset token
        to the users e-mail (e-mail taken from the database). For this we
        use a configured gmail.

        Example request:
        {"username":"omar_glu"}
        """
        
        args = reset_password.parse_args()
        
        self.username = args["username"]
            
        try:
            user_data = UserData.query.filter_by(username = self.username).first()
            
            if user_data is None:
                return {"error" : "No user with this username"}, 400
            

            
            email = user_data.email.split()
            subject = "Password Reset"
            sender = "pythontestemailsflask@gmail.com"
            
            token = jwt.encode({"public_id" : user_data.public_id,
                                        "exp" : datetime.utcnow() + timedelta(minutes=90) 
                                        },key = os.getenv("SECRET_KEY"), algorithm="HS256")
            
            flask_send_email(subject, sender, email, token)
            return {"msg": "E-mail with the reset token has been sent"}
        except Exception as e:
            print(e)
            return {"error", str(e)}, 500
        
    @token_required
    def put(self, user):
        
        """ Takes in the token provided in the email along with the new
        password and a confirmation of the new password. The user_id is provided
        by the warper function above so it knows which user is requesting the change.

        Example request:
        
            {"new_password": "123456788",
            "confirm_password" : 123456788}
        """
        
        args = request_new_password.parse_args()
        
        new_password = args["new_password"]
        confirm_password = args["confirm_password"]
        
        if new_password != confirm_password:
            return {"error" : "Passwords do not match!"}, 400
        
        if len(new_password) < 8:
            return {"error" : "Password is too short!"}, 400
        try:    
            
            new_password = generate_password_hash(new_password,
                                                    method="pbkdf2:sha256") 
            
            user_data = UserData.query.filter_by(id = user).first()
            print(user_data.password)
            
            user_data.password = new_password
            user_data.save()
            
            return {"msg": "Password has been updated!"}
       
        except Exception as e:
            print(e)
            return {"error", str(e)}, 500