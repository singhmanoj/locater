__author__ = 'manoj'

from twisted.internet import task, defer, reactor
from txmongo import MongoConnection
import configurations
import os
import treq
import random
# sync things
from locater.models import HospitalData
from mongoengine import DoesNotExist
import json

config_name = os.environ.get('locater_CONFIG_NAME', 'Development')
config_class = getattr(configurations, config_name)
semaphore = defer.DeferredSemaphore(config_class.MAX_RUN)
mongo = None


@defer.inlineCallbacks
def defer_task(mongoinstance, email):
    print mongoinstance, email
    try:
        mongo = yield get_connection()
        collection = mongo.locater.crawl_data
        collection_email = mongo.locater.email_set
        # get email
        url_params = {
            'location': ','.join([str(coordinate) for coordinate in mongoinstance['point']]),
            'type': mongoinstance['type'],
            'key': email['google_key']
        }
        url = config_class.GOOGLE_API_PLACES % url_params
        print url
        response = yield treq.get(str(url))
        assert response.code == 200, 'Fetching Data is Failed'
        content = yield response.content()
        content = json.loads(content)
        if content['status'] == 'OK':
            processed_response(content, mongoinstance)
            yield collection.update_one({'_id': mongoinstance['_id']}, {'$set': {'is_processed': True}}, upsert=False)
            while 'next_page_token' in content.keys():
                yield sleep(5)  #sleep for next few seconds
                temp_url = url + '&pagetoken=%s' % content['next_page_token']
                response = yield treq.get(str(temp_url))
                assert response.code == 200, 'Fetching Data is Failed with PageToken'
                content = yield response.content()
                content = json.loads(content)
                if content['status'] == 'OK':
                    # process request
                    processed_response(content, mongoinstance)
                else:
                    # This request is not processed
                    print 'LOG ERROR:: pagetoken call is failed' + json.dumps(content)
                    yield collection.update_one({'_id': mongoinstance['_id']}, {'$set': {'is_processed': False}}, upsert=False)

        elif content['status'] == 'OVER_QUERY_LIMIT':
            yield collection_email.update_one({'_id': email['_id']}, {'$set': {'is_limit': True}}, upsert=False)
        elif content['status'] == 'ZERO_RESULTS':
            yield collection.update_one({'_id': mongoinstance['_id']}, {'$set': {'is_processed': True}}, upsert=False)
        else:
            print 'LOG ERROR status 200::', content['status'], url


    except AssertionError, e:
        print 'LOG ERROR::', str(e), url
    finally:
        yield collection.update_one({'_id': mongoinstance['_id']}, {'$set': {'is_processing': False}}, upsert=False)


@defer.inlineCallbacks
def append_task():
    mongo = yield get_connection()
    collection = mongo.locater.crawl_data
    active_task = yield collection.find({'is_processing': True, 'is_processed': False})
    for i in xrange(config_class.TASK_LIMIT - len(active_task)):
        mongoinstance = yield collection.find_one({'is_processing': False, 'is_processed': False})
        email = yield get_email()
        if mongoinstance and email:
            print 'LOG INFO:: Task Added'
            semaphore.run(defer_task, mongoinstance, email)
            yield collection.update_one({'_id': mongoinstance['_id']}, {'$set': {'is_processing': True}}, upsert=False)
    print len(active_task)

def sleep(secs):
    d = defer.Deferred()
    reactor.callLater(secs, d.callback, None)
    return d

def processed_response(content, mongoinstance):
    for result in content['results']:
        try:
            data = {
                'google_place_id': result['place_id'],
                'name': result['name'],
                'address': result['vicinity'],
                'point': [
                    result['geometry']['location']['lat'],
                    result['geometry']['location']['lng']
                ],
                'city': mongoinstance['city']
            }
            try:
                hospital = HospitalData.objects.get(google_place_id=data['google_place_id'])
            except DoesNotExist, e:
                hospital = HospitalData(**data)
                hospital.save()
        except Exception, e:
            print 'LOG ERROR::Processing Request:', str(e)

def loop_call():
    loopcall = task.LoopingCall(append_task)
    loopcall.start(1.0)

@defer.inlineCallbacks
def get_connection():
    global mongo
    try:
        yield mongo.locater.crawl_data.find()
    except:
        mongo = yield MongoConnection(
            host=config_class.MONGODB_HOST['host'],
            port=config_class.MONGODB_HOST['port']
        )
    defer.returnValue(mongo)

@defer.inlineCallbacks
def get_email():
    mongo = yield get_connection()
    collection = mongo.locater.email_set
    email = yield collection.find({'is_blocked': False, 'is_limit': False, 'is_active': True})
    if len(email) == 0:
        defer.returnValue(None)
    else:
        defer.returnValue(email[random.randint(0, len(email) - 1)])


if __name__ == '__main__':
    loop_call()
    reactor.run()
