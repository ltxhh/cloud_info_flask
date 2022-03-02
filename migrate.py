from common.models.users import User
from common.models import db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from project.main import app
import os
print(os.getcwd())

manage = Manager(app)
migrate = Migrate(app, db)
manage.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manage.run()
