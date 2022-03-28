from flask import Flask
from common.models import db
from common.cache import cache
from flask_restful import Api
from flask_cors import CORS
from project.resources.users import user_bp
from project.resources.channel import text_bp
from project.resources.userChannels import channels_bp
from project.resources.news import news_bp
from project.resources.collects import collect_bp
from logs.logs import setup_log
from flask_apscheduler import APScheduler
from common.utils.middlewares import jwt_authentication
from common.cron_task.new_task import update_recommend_list
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

# 实例化 APScheduler
scheduler = APScheduler()


def create_flask_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.before_request(jwt_authentication)
    app.register_blueprint(user_bp)
    app.register_blueprint(text_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(collect_bp)
    app.register_blueprint(channels_bp)
    setup_log('testing')
    db.init_app(app)
    cache.init_app(app=app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    Api(app)
    # 配置定时任务
    executors = {
        'default': ThreadPoolExecutor(10)
    }
    app.scheduler = BackgroundScheduler(executors=executors)
    # 每隔一分钟执行一次
    app.scheduler.add_job(update_recommend_list, trigger='interval', hours=1, args=[cache, app])
    app.scheduler.add_job(update_recommend_list, trigger='date', args=[cache, app])
    # app.scheduler.add_job(func=cron_test, trigger='interval', seconds=10)
    # app.scheduler.add_job(func=GetUserAttentionNew, trigger='date')
    app.scheduler.start()
    return app
