__author__ = 'manoj'

from twisted.internet import task, defer, reactor
from txmongo import MongoConnection
import os
config_name = os.environ.get('locater_CONFIG_NAME', 'Development')
config_class = getattr(configurations, config_name)

@defer.inlineCallbacks
def task(mongoinstance):
    pass

@defer.inlineCallbacks
def append_task():
    mongo = yield get_connection()
    collection = mongo.locater.crawl_data
    active_task = yield collection.find({'is_processing': True, 'processed': False})
    print len(active_task)

@defer.inlineCallbacks
def loop_call():
    loopcall = task.LoopingCall(append_task)
    loopcall.start(1.0)

@defer.inlineCallbacks
def get_connection():
    mongo = yield MongoConnection(
        host=config_class.MONGODB_HOST['host'],
        port=config_class.MONGODB_HOST['port']
    )
    defer.returnValue(mongo)

if __name__ == '__main__':
    loop_call()
    reactor.run()
