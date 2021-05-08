# importing modules
from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from abbrefy.config import Config

# instantiating  pymongo
mongo = PyMongo()

# instantiating bcrypt for password hash
bcrypt = Bcrypt()


def create_app(config_class=Config):
    application = Flask(__name__)
    application.config.from_object(Config)
    mongo.init_app(application)
    bcrypt.init_app(application)

    from abbrefy.users.routes import users
    from abbrefy.links.routes import links
    from abbrefy.main.routes import main
    application.register_blueprint(users)
    application.register_blueprint(links)
    application.register_blueprint(main)

    return application
