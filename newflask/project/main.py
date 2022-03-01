from project.resources import Create_flask_app
from common.settings.defaul import SqlConfig

app = Create_flask_app(SqlConfig)

if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
