import os
from dotenv import load_dotenv   


load_dotenv(dotenv_path=r'..\configuration\.env')
class Configuration(object):
    
    """ Configuration options shared for all instances
    of the Flask app.
    """
    SECRET_KEY="topsecretkey"
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    MAIL_SERVER="smtp.googlemail.com"
    MAIL_PORT=587
    MAIL_USE_TLS=1
    MAIL_USERNAME="pythontestemailsflask@gmail.com"
    MAIL_PASSWORD="thisisjustatestemail"

    POSTGRES_USER="admin_user"
    POSTGRES_PASSWORD="password"
    POSTGRES_HOST="db"
    POSTGRES_PORT=5432
    POSTGRES_DB="task_db"

    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
class DevConfig(Configuration):
    
    """ Development configuration for Flask app
    """

class TestingConfig(Configuration):
    """ Testing cconfiguration for Flask app
    """
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://admin_user:password@localhost:5432/task_db"
    
    
class ProductionConfig(Configuration):
    
    """ Production configuration for Flask app
    """
    
    TESTING = False
    DEBUG = False
    
app_config = {"dev": DevConfig,
              "test": TestingConfig,
              "product": ProductionConfig
              }    

if __name__ == "__main__":
        
    
        
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    POSTGRES_DB="localhost"
    #SQLALCHEMY_TRACK_MODIFICATIONS = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
