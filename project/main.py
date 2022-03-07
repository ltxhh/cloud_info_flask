from project.resources import create_flask_app
from common.settings.default import sqlconfig
# from flask_restful import request
# from flask import jsonify
# from datetime import datetime, timedelta
# from common.utils.jwt_utils import generate_jwt, verify_jwt

app = create_flask_app(sqlconfig)

# @app.route('/login', methods=['POST'])
# def login():
#     print("sdfghjkl")
#     print(request.data)
#     name = request.data.get('name')
#     pwd = request.args.get('pwd')
#     print(name, pwd)
#     if name and pwd:
#         expire = datetime.utcnow() + timedelta(hours=2)
#         token = generate_jwt({'name': name}, expire)
#         return jsonify({'code': 200, 'token': token, 'name': name})
#     return jsonify({'code': 500, 'msg': 'error'})


# @app.route('/index')
# def index():
#     token = request.form.get('token')
#     payload = verify_jwt(token)
#     if payload:
#         return jsonify({'code': 200, 'token': token})
#     else:
#         return 'Token not working'


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
