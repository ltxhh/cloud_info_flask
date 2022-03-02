from project.resources import create_flask_app
from common.settings.sql_config import sqlconfig

app = create_flask_app(sqlconfig)

if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
