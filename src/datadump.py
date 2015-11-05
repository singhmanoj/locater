__author__ = 'manoj'

from twisted.internet import task, defer, reactor
from txmongo import MongoConnection
import configurations
import os
import treq
import random
# sync things
from locater.models import HospitalData, City, Doctors, Availability, Specialty, Qualification
from mongoengine import DoesNotExist
import json
import time

config_name = os.environ.get('locater_CONFIG_NAME', 'Development')
config_class = getattr(configurations, config_name)
semaphore = defer.DeferredSemaphore(config_class.MAX_RUN)
mongo = None


@defer.inlineCallbacks
def defer_task(mongoinstance):
    try:
        page = 1
        while True:
            mongo = yield get_connection()
            collection = mongo.locater.city
            # get email
            url_params = {
                'city': mongoinstance['name'],
                'number': str(page)
            }
            url = config_class.SITE_URL % url_params
            print 'FETCHING DATA:: ', url
            response = yield treq.get(str(url))
            assert response.code == 200, 'Fetching Data is Failed'
            content = yield response.content()
            content = json.loads(content)
            if len(content['results']) == 0:
                break
            else:
                processed_response(content, mongoinstance)
            page += 1
            time.sleep(1)
        yield collection.update_one({'_id': mongoinstance['_id']}, {'$set': {'is_processed': True}}, upsert=False)
    except AssertionError, e:
        print 'LOG ERROR::', str(e), url
    finally:
        yield collection.update_one({'_id': mongoinstance['_id']}, {'$set': {'is_processing': False}}, upsert=False)


@defer.inlineCallbacks
def append_task():
    mongo = yield get_connection()
    collection = mongo.locater.city
    active_task = yield collection.find({'is_processing': True, 'is_processed': False})
    for i in xrange(config_class.TASK_LIMIT - len(active_task)):
        mongoinstance = yield collection.find_one({'is_processing': False, 'is_processed': False})
        if mongoinstance:
            semaphore.run(defer_task, mongoinstance)
            yield collection.update_one({'_id': mongoinstance['_id']}, {'$set': {'is_processing': True}}, upsert=False)

def processed_response(content, mongoinstance):
    '''

    :param content:
    :return:
    '''
    '''
    name = db.StringField(required=True)
    s_id = db.StringField(unique=True, sparse=True)
    point = db.GeoPointField(required=True)
    address = db.StringField()
    phone_no = db.StringField()  # To get the phone no.
    doctors = db.EmbeddedDocumentListField(Doctors)
    created_on = db.DateTimeField(default=datetime.datetime.now)
    modified_on = db.DateTimeField(default=datetime.datetime.now)
    is_verified = db.BooleanField(default=False)
    is_active = db.BooleanField(default=True)
    city = db.ReferenceField(City)

    doctor_name = db.StringField()
    summary = db.StringField()
    qualifications = db.EmbeddedDocumentListField(Qualification)
    is_local = db.BooleanField(default=True)
    is_male = db.BooleanField()
    available = db.EmbeddedDocumentListField(Availability)
    consultation_fee = db.FloatField()
    practice_time = db.IntField()
    specialties = db.EmbeddedDocumentListField(Specialty)


    '''
    for result in content['results']:
        try:
            hospital = HospitalData.objects.get(s_id=result['practice_id'])
            if result['latitude'] and result['longitude']:
                hospital.point = [
                        result['longitude'],
                        result['latitude']
                    ]
            hospital.name = result['clinic_name']
            hospital.city = City.objects.get(name=mongoinstance['name'])
        except DoesNotExist, e:
            data = {
                'name': result['clinic_name'],
                's_id': result['practice_id'],
                'point': [
                    result['longitude'],
                    result['latitude']
                ],
                'city': City.objects.get(name=mongoinstance['name'])
            }
            hospital = HospitalData(**data)
            hospital.doctors = []
        doctor = Doctors()
        doctor.doctor_name = result['doctor_name']
        doctor.summary = result['summary']
        doctor.is_local = result['is_resident_doctor']
        doctor.is_male = True if result['gender'] == 'm' else False
        doctor.consultation_fee = result['consultation_fees']
        doctor.practice_exp = result['experience_years']
        doctor.qualifications = []
        for qual in result['qualifications']:
            data = {
                'completion_year': qual['completion_year'],
                'college': qual['college'],
                'degree': qual['qualification']
            }
            qualification = Qualification(**data)
            doctor.qualifications.append(qualification)

        doctor.available = []
        for day, timing in result['visit_timings'].iteritems():
            data = {
                'day': day,
                'first_half_start_time': timing['session1_start_time'],
                'first_half_end_time': timing['session1_end_time'],
                'second_half_start_time': timing['session2_start_time'],
                'second_half_end_time': timing['session2_end_time']
            }
            available = Availability(**data)
            doctor.available.append(available)

        doctor.specialties = []
        for special in result['specialties']:
            data = {
                'specialty': special['specialty'],
                'sub_specialty': special['sub_specialty'],
                'type': special['doctor_label']
            }
            specialty = Specialty(**data)
            doctor.specialties.append(specialty)
        hospital.doctors.append(doctor)
        hospital.save()

def loop_call():
    loopcall = task.LoopingCall(append_task)
    loopcall.start(1.0)

@defer.inlineCallbacks
def get_connection():
    global mongo
    try:
        yield mongo.locater.hospital_data.find()
    except:
        mongo = yield MongoConnection(
            host=config_class.MONGODB_HOST['host'],
            port=config_class.MONGODB_HOST['port']
        )
    defer.returnValue(mongo)


def get_cities():
    import requests
    url = config_class.SITE_URL % {"city": '', "number": str(1)}
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()
        for city_name in results['cities']:
            try:
                city = City.objects.get(name=city_name.lower())
            except DoesNotExist:
                city = City()
                city.name = city_name.lower()
                city.save()
    else:
        print 'LOG ERROR:: Getting the cities'


if __name__ == '__main__':
    # get_cities()
    loop_call()
    reactor.run()
