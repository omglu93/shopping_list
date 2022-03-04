from flask import Flask
from flask_restful import Api
from configuration.config import app_config
from src.app_database import db
from flask_migrate import Migrate
from src.user_ops import UserLogin, CreateUser

def create_app(config_type : str):

    app = Flask(__name__,
    instance_relative_config=True)

    app.config.from_object(app_config[config_type])
    
    db.app = app
    db.init_app(app)
    ### Database migration ###
    migrate = Migrate(app, db)
    # flask db init, migrate, upgrade
    
    api = Api(app)
    
    api.add_resource(CreateUser, "/create-user")
    api.add_resource(UserLogin, "/login")

    return app


if __name__ == "__main__":
    create_app("dev")