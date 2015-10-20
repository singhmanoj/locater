from flask import Flask
from celery import Celery
from mongoengine import connect
from flask.ext.admin import Admin
import os
import configurations

app = None
admin = Admin()
celery = None
config_name = os.environ.get('locater_CONFIG_NAME', 'Development')
config_class = getattr(configurations, config_name)
connect(config_class.MONGODB_HOST['DB'], host='mongodb://%(host)s:%(port)s/%(DB)s' % config_class.MONGODB_HOST)

def create_app(package_name='locater'):
    """Returns a :class:`Flask` application instance configured with common
    functionality for the locater platform.

    :param package_name: application package name
    :param package_path: application package path
    :param config_name: can have one of [production, development, testing]
    """
    global app

    app = Flask(package_name, instance_relative_config=True)

    app.config.from_object('configurations.%s'%config_name.title())

    # app.jinja_loader = jinja2.ChoiceLoader([
    #     app.jinja_loader,
    #     jinja2.FileSystemLoader('locater/templates/'),
    # ])
    global celery
    celery = create_celery_app(app)
    from locater.views import CityVerifyView, CityView, CitySearchView
    CityVerifyView.register(app)
    CityView.register(app)
    CitySearchView.register(app)
    from locater.views import HospitalDataView, HospitalVerifyView
    HospitalDataView.register(app)
    HospitalVerifyView.register(app)
    admin.init_app(app)
    return app

def create_celery_app(app=None):
    app = app or create_app()
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
