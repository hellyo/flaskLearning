#coding=utf-8
#app.config内容

import os

#获取当前文件所在目录的绝对路径
basedir=os.path.abspath(os.path.dirname(__file__)) 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'xxxxxxxxxxx'
    #程序结束时自动commit 数据
    SQLALCHEMY_COMMIT_ON_TEARDOWM = True
    MAIL_SUBJECT = '[FLASK TEST]'
    MAIL_SENDER = 'XX<xxxx@xxxx.com>'
    FLASK_ADMIN = os.environ.get('FLASK_ADMIN')

    @staticmethod
    def init_app(app):
        pass

class DevConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    #MAIL_USE_TLS
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or'sqlite:///' + os.path.join(basedir,'data_dev.sqlite')

class Testing(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or'sqlite:///' + os.path.join(basedir,'data_test.sqlite')
    TESTING = True

class Production(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or'sqlite:///' + os.path.join(basedir,'data.sqlite')


config = {
    "dev":DevConfig,
    "test":Testing,
    "production":Production,

    "default":DevConfig
}