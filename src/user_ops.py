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

load_dotenv(dotenv_path=r'..\configuration\.env')

create_user_args = reqparse.RequestParser()
create_user_args.add_argument("username",
                              type=str,
                              location="json")

create_user_args.add_argument("e_mail",
                              type=str,
                              location="json")

create_user_args.add_argument("password",
                              type=str,
                              location="json")

edit_user_args = reqparse.RequestParser()
edit_user_args.add_argument("first_name",
                            type=str,
                            location="json")

edit_user_args.add_argument("last_name",
                            type=str,
                            location="json")

class CreateUser(Resource):
    
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
        if re.fullmatch(self.REGEX_E_MAIL_VALIDATION, email):
            return email
        else:
            return {"error" : "E-mail is not valid!"}, 400
        
    def post(self):
        
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
                                   
            user_credentials = UserCredentials(first_name="Jon",
                                               last_name="Doe",
                                               user = user_id[0])
            user_credentials.save()
            
            return {"msg" : "User created!"}
            
        except Exception as e:
            print(e)
            return {"error" : str(e)}, 500
        
        
class UserLogin(Resource):
    
    def __init__(self):
        self.auth = request.authorization

    def get(self):

        try:
            username = self.auth.username

            if not self.auth or not self.auth.username or not self.auth.password:
                return {"error" : "Could not verify!"}, 401

            user = UserData.query.filter_by(username=self.auth.username).first()
            if not user:
                return {"error" : "Could not verify!"}, 401


            if check_password_hash(user.password, self.auth.password):
                token = jwt.encode({"public_id" : user.public_id,
                                    "exp" : datetime.utcnow() + timedelta(minutes=90) 
                                    },key = os.getenv("SECRET_KEY"))                              
                #token = token.decode("utf-8")         
                return {"token" : token}, 200

            return {"error" : "Could not verify!"}, 401
        
        except Exception as e:
            print(e)
            return {"error" : str(e)}, 500
        
# class UserCredentials(Resource):
#     pass    
