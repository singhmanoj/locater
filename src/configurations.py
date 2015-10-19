import os

class Base(object):
    DEBUG = False
    TESTING = False

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CACHE_TYPE = 'simple'
    SECRET_KEY = 'the-secret-key-is-not-here'
    CELERY_IMPORTS = ['locater.tasks']
    CSRF_ENALED = True
    GOOGLE_API_CITY = 'https://maps.googleapis.com/maps/api/geocode/json?key=%(key)s'  # Limit 2500 Request/Day
    GOOGLE_API_PLACES = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%(location)s&rankby=distance&types=%(type)s&key=%(key)s'  # Limit 1000 Request/Day
    GOOGLE_API_PLACE_DETAILS = 'https://maps.googleapis.com/maps/api/place/details/json?placeid=%(google_place_id)s&key=%(key)s'
    STEP_DEGREE = 0.1  # LAT = 11.123KM and For LONG = 8.657  For Both apply pythagorus theorem # To make rectangular boundary
    TYPES = ["hospital", "dentist", "doctor"]
    MAX_RUN = 5
    TASK_LIMIT = 200

class Production(Base):
    DEBUG = False
    TESTING = False

        
class Development(Base):
    DEBUG = True
    TESTING = False
    MONGODB_HOST = {'DB': 'locater', 'host':'localhost','port':27017}

# class Testing(Base):
#     TESTING = True
#     DEBUG = True
#     MONGODB_SETTINGS ={'DB':'rocket_test','host':'mongo','port':27017}
