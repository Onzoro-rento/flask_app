import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# グローバル変数
app = None

# モジュール
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    global app
    app = Flask(__name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'))

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_plans.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from .auth.routes import auth_bp
    from .plans.routes import plans_bp
    from .history.routes import history_bp
    from .errors import show_404_page

    app.register_blueprint(auth_bp)
    app.register_blueprint(plans_bp)
    app.register_blueprint(history_bp)
    app.register_error_handler(404, show_404_page)

    return app