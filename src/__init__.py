from flask import Flask
from flask_restful import Api
from src.services.email_gen import flask_mail
from configuration.config import app_config
from src.app_database import db
from flask_migrate import Migrate
from src.user_ops import ForgotPassword, UserLogin, CreateUser, UserCred
from src.shopping_ops import ShoppingListClass, ShoppingListAnalytics
from src.items_ops import ItemManipulation


def create_app(config_type : str):
    app = Flask(__name__,
    instance_relative_config=True)
    app.config.from_object(app_config[config_type])
    print(app_config[config_type].SQLALCHEMY_DATABASE_URI)
    db.app = app
    db.init_app(app)
    
    ### Database migration ###
    migrate = Migrate(app, db)
    # flask db init, migrate, upgrade
    
    flask_mail.init_app(app)
    # Add prefix for version control
    api = Api(app, prefix="/api/v1")
    
    api.add_resource(CreateUser, "/create-user")
    api.add_resource(UserLogin, "/login")
    api.add_resource(ForgotPassword, "/login/forgot-password")
    api.add_resource(UserCred, "/edit-user")
    api.add_resource(ShoppingListClass, "/shopping-lists")
    api.add_resource(ItemManipulation, "/shopping-lists/items")
    api.add_resource(ShoppingListAnalytics, "/shopping-lists/overview")

    return app


if __name__ == "__main__":
    create_app("dev")