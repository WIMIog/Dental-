from app import app, db
from flask_migrate import Migrate
from flask.cli import FlaskGroup

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Setup Flask CLI group
cli = FlaskGroup(app)

if __name__ == "__main__":
    cli()
