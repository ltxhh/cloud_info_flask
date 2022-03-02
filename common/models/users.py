from common.models import db
from datetime import datetime


# 用户表
# 1.用户模型
class User(db.Model):
    """
    用户基本信息
    """
    __tablename__ = 'user_basic'

    class STATUS:
        ENABLE = 1
        DISABLE = 0

    uid = db.Column(db.Integer, primary_key=True, doc='用户ID')
    mobile = db.Column(db.String(32), doc='手机号')
    password = db.Column(db.String(32), doc='密码')
    user_name = db.Column(db.String(32), doc='昵称')
    profile_photo = db.Column(db.String(64), doc='头像')
    last_login = db.Column(db.DateTime, doc='最后登录时间')
    is_media = db.Column(db.Boolean, default=False, doc='是否是自媒体')
    is_verified = db.Column(db.Boolean, default=False, doc='是否实名认证')
    introduction = db.Column(db.String(128), doc='简介')
    certificate = db.Column(db.String(64), doc='认证')
    article_count = db.Column(db.Integer, default=0, doc='发帖数')
    following_count = db.Column(db.Integer, default=0, doc='关注的人数')
    fans_count = db.Column(db.Integer, default=0, doc='被关注的人数（粉丝数）')
    like_count = db.Column(db.Integer, default=0, doc='累计点赞人数')
    read_count = db.Column(db.Integer, default=0, doc='累计阅读人数')

    account = db.Column(db.String(32), doc='账号')
    email = db.Column(db.String(64), doc='邮箱')
    status = db.Column(db.Integer, default=1, doc='状态，是否可用')

    news = db.relationship('News', backref="news", uselist=False)
    comment = db.relationship('Comment', backref=db.backref('comments'), uselist=False)
    search = db.relationship('SearchHistory', backref=db.backref('searches'), uselist=False)


# 2.用户关注关系表
class Ratation(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey("user_basic.uid"), primary_key=True)
    foller_id = db.Column(db.Integer, db.ForeignKey("user_basic.uid"), primary_key=True)
    relation = db.Column(db.Boolean, doc='状态(1,关注;0, 取消)')
    create_time = db.Column(db.DateTime, default=datetime.now, doc='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')
    user = db.relationship('User', foreign_keys=user_id)
    foller = db.relationship('User', foreign_keys=foller_id)


# 4.用户频道表
user_channel = db.Table(
    'user_channel',
    db.Column('uid', db.Integer, db.ForeignKey('user_basic.uid'), primary_key=True, doc="用户ID"),
    db.Column('cid', db.Integer, db.ForeignKey('news_channel.cid'), primary_key=True, doc="频道ID"),
    db.Column('is_delete', db.Boolean, doc="状态(1, 可用;0, 不可用)"),
    db.Column('create_time', db.DateTime, default=datetime.now, doc="创建时间"),
    db.Column('update_time', db.DateTime, default=datetime.now, doc="更新时间"),
    db.Column('sequence', db.Integer, default=0, doc='序号')
)


# 3.频道表
class Channel(db.Model):
    """
    新闻频道
    """
    __tablename__ = 'news_channel'

    cid = db.Column(db.Integer, primary_key=True, doc='频道ID')
    cname = db.Column(db.String(32), doc='频道名称')
    ctime = db.Column(db.DateTime, default=datetime.now, doc='创建时间')
    utime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')
    sequence = db.Column(db.Integer, default=0, doc='序号')
    is_visible = db.Column(db.Boolean, default=False, doc='是否可见')
    is_default = db.Column(db.Boolean, default=False, doc='是否默认')
    user = db.relationship('User', secondary=user_channel, backref=db.backref('channels'))
    news = db.relationship('News', backref='channel', uselist=False)


# 6.用户收藏表
collection = db.Table(
    'collection',
    db.Column('user_id', db.Integer, db.ForeignKey('user_basic.uid'), primary_key=True, doc="用户ID"),
    db.Column('news_id', db.Integer, db.ForeignKey('news_basic.nid'), primary_key=True, doc="资讯ID"),
    db.Column('is_delete', db.Boolean, doc='状态(1,关注;0, 取消)'),
    db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间'),
    db.Column('update_time', db.DateTime, default=datetime.now, onupdate=datetime.now, doc='更新时间')
)


# 5.资讯表
class News(db.Model):
    """
    文章基本信息表
    """
    __tablename__ = 'news_basic'

    class STATUS:
        DRAFT = 0  # 草稿
        UNREVIEWED = 1  # 待审核
        APPROVED = 2  # 审核通过
        FAILED = 3  # 审核失败
        DELETED = 4  # 已删除
        BANNED = 5  # 封禁

    STATUS_ENUM = [0, 1, 2, 3]

    nid = db.Column(db.Integer, primary_key=True, doc='文章ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user_basic.uid'), doc='用户ID')
    channel_id = db.Column(db.Integer, db.ForeignKey('news_channel.cid'), doc='频道ID')
    title = db.Column(db.String(64), doc='标题')
    cover = db.Column(db.String(32), doc='封面')
    is_advertising = db.Column(db.Boolean, default=False, doc='是否投放广告')
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    status = db.Column(db.Integer, default=0, doc='帖文状态')
    reviewer_id = db.Column(db.Integer, doc='审核人员ID')
    review_time = db.Column(db.DateTime, doc='审核时间')
    delete_time = db.Column(db.DateTime, doc='删除时间')
    comment_count = db.Column(db.Integer, default=0, doc='评论数')
    good_count = db.Column(db.Integer, default=0, doc='点赞数')
    allow_comment = db.Column(db.Boolean, default=True, doc='是否允许评论')
    reject_reason = db.Column(db.String(64), doc='驳回原因')
    utime = db.Column(db.DateTime, default=datetime.now, doc='更新时间')
    content = db.Column(db.Text, doc='帖文内容')

    comment = db.relationship('Comment', backref=db.backref('article'))
    user = db.relationship('User', secondary=collection, backref=db.backref('user'))


# 7.评论表
class Comment(db.Model):
    """
    文章评论
    """
    __tablename__ = 'news_comment'

    class STATUS:
        UNREVIEWED = 0  # 待审核
        APPROVED = 1  # 审核通过
        FAILED = 2  # 审核失败
        DELETED = 3  # 已删除

    cmid = db.Column(db.Integer, primary_key=True, doc='评论ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user_basic.uid'), doc='用户ID')
    article_id = db.Column(db.Integer, db.ForeignKey('news_basic.nid'), doc='文章ID')
    parent_id = db.Column(db.Integer, db.ForeignKey('news_comment.cmid'), doc='被评论的评论id')
    like_count = db.Column(db.Integer, default=0, doc='点赞数')
    reply_count = db.Column(db.Integer, default=0, doc='回复数')
    content = db.Column(db.String(128), doc='评论内容')
    is_top = db.Column(db.Boolean, default=False, doc='是否置顶')
    status = db.Column(db.Integer, default=1, doc='评论状态')
    ctime = db.Column(db.DateTime, default=datetime.now, doc='创建时间')


# 8.评论点赞表
class CommentLiking(db.Model):
    """
    评论点赞
    """
    __tablename__ = 'news_comment_liking'

    liking_id = db.Column(db.Integer, primary_key=True, doc='主键ID')
    user_id = db.Column(db.Integer, doc='用户ID')
    comment_id = db.Column(db.Integer, doc='评论ID')
    ctime = db.Column('create_time', db.DateTime, default=datetime.now, doc='创建时间')
    is_deleted = db.Column(db.Boolean, default=False, doc='是否删除')


# 9.搜索历史
class SearchHistory(db.Model):
    sid = db.Column(db.Integer, primary_key=True, doc='搜索记录ID')
    content = db.Column(db.String(128), doc="用户搜索内容")
    user_id = db.Column(db.Integer, db.ForeignKey('user_basic.uid'), doc="用户ID")
