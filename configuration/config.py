from asyncio.format_helpers import _format_callback_source
import os


class Configuration(object):
    
    """ Configuration options shared for all instances
    of the Flask app.
    """
    DEBUG = False
    SECRET_KEY=os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS")
    
    

class DevConfig(Configuration):
    
    """ Development configuration for Flask app
    """
    
    DEBUG = True
    

class TestingConfig(Configuration):
    """ Testing cconfiguration for Flask app
    """
    
    TESTING = True
    # Specific database for testing
    # SQLALCHEMY_DATABASE_URI =
    
class ProductionConfig(Configuration):
    
    """ Production configuration for Flask app
    """
    
    TESTING = False
    DEBUG = False
    
app_config = {"dev": DevConfig,
              "test": TestingConfig,
              "product": ProductionConfig
              }    
