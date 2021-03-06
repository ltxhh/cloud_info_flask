from common.models.models import *
from common.models.book import Book
from common.models import db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from project.main import app

manage = Manager(app)
migrate = Migrate(app, db)
manage.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manage.run()
