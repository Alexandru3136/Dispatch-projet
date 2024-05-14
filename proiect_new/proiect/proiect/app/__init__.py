from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app, db)

    from .models import User  # Importul modelului aici pentru a asigura crearea tabelei în baza de date
    from .models import Comment  # Importul modelului aici pentru a asigura crearea tabelei în baza de date

    with app.app_context():
        db.create_all()  # Se crează automat tabelele bazei de date

    from .routes import setup_routes
    setup_routes(app)

    return app
