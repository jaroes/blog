from os import environ
from flask import Flask 
from . import db
from . import auth

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='mykey',
        DATABASE_HOST=environ.get('FLASK_DATABASE_HOST'),
        DATABASE_PASSWORD=environ.get('FLASK_DATABASE_PASSWORD'),
        DATABASE_USER=environ.get('FLASK_DATABASE_USER'),
        DATABASE=environ.get('FLASK_DATABASE')
    )
    db.init_app(app)

    app.register_blueprint(auth.bp)

    @app.route('/hola')
    def hola():
        return 'Chanz'
    
    return app