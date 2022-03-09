from project import create_flask_app
from common.settings.default import sqlconfig

app = create_flask_app(sqlconfig)

if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
