import jwt
import os
from functools import wraps
from flask import request
from src.app_database import UserData
from dotenv import load_dotenv
from configuration.config import Configuration
load_dotenv(dotenv_path=r'..\configuration\.env')

def token_required(function):

    """ Creates a warper function for functions that
    require some sort of token validation. The token is
    decoded using the public id and secret key, if the 
    token is ok the inner function will resume.
    """
    @wraps(function)
    def decorated(*args, **kwargs):
        print("Validator is running!")
        try:
            data = request.headers["authorization"]
            token = str.replace(str(data), "Bearer ", "")
            print("Token check is running!")
        except:
            return {"error" : "Authorization is missing!"}, 401
        
        if not token:
            return {"error" : "Token is missing"}, 401
        try:
            # data = jwt.decode(token, key = os.getenv("SECRET_KEY"), algorithms="HS256")
            data = jwt.decode(token, key = Configuration.SECRET_KEY, algorithms="HS256")

            current_user = UserData.query.filter(UserData.public_id == data["public_id"]).first()
        except:
           return {"message" : "Token is invalid"}, 401
        return function(*args, current_user.id, **kwargs) #current_user.username,
    return decorated