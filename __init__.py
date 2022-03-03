from flask import Flask
from flask_restful import Api
from configuration.config import app_config

def create_app(config_type : str):

    app = Flask(__name__,
    instance_relative_config=True)

    app.config.from_object(app_config[config_type])
    
    # db.app = app
    # db.init_app(app)
    # api = Api(app)

    # return app
    
    print(app_config[config_type])
    
    
create_app("dev")