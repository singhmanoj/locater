from flask.ext.classy import FlaskView
from flask import Response
from flask.json import dumps
from flask import request
from locater.models import City, EmailSet, HospitalData
from mongoengine import DoesNotExist
from locater.tasks import create_city_latlonggrid
import json
import random
import requests

class CitySearchView(FlaskView):
    def post(self):
        response_dict = {}
        data = request.json

        if not data:
            data = request.form
        email = EmailSet.objects.filter(is_active=True, is_limit=False, is_blocked=False)
        if email.count() == 0:
            response_dict['message'] = 'No email is available for request'
            return Response(dumps(response_dict), status=400, content_type="application/json")
        else:
            email = email[random.randint(0, email.count()-1)]
        try:
            url_params = {
                'key': email.google_key,
                'address': '+'.join(data['city'].split(' '))
            }
            from app import app
            url = app.config.get('GOOGLE_API_CITY') % url_params
            response = requests.get(url)
            assert response.status_code == 200, 'Google Request Failed :: ' + url
            content = response.json()
            print content
            if content['status'] == 'OK':
                # Good extract results
                response_dict['data'] = []
                for result in content['results']:
                    if 'bounds' in result['geometry'].keys():
                        bounds = 'bounds'
                    else:
                        bounds = 'viewport'  # Not a good approach but can be modify
                    formated_data = {
                        'google_place_id': result['place_id'],
                        'name': result['formatted_address'],
                        'point': [
                            result['geometry']['location']['lat'],
                            result['geometry']['location']['lng'],
                        ],
                        'southwest': [
                            result['geometry'][bounds]['southwest']['lat'],
                            result['geometry'][bounds]['southwest']['lng'],
                        ],
                        'northeast': [
                            result['geometry'][bounds]['northeast']['lat'],
                            result['geometry'][bounds]['northeast']['lng'],
                        ]
                    }
                    response_dict['data'].append(formated_data)
                response_dict['message'] = 'Cities Found on Google'
                return Response(dumps(response_dict), status=200, content_type="application/json")
            elif content['status'] == 'ZERO_RESULTS':
                response_dict['message'] = 'No Cities Found on Google'
                response_dict['data'] = []
                return Response(dumps(response_dict), status=200, content_type="application/json")
            elif content['status'] == 'OVER_QUERY_LIMIT':
                response_dict['message'] = 'Email exceed the limit'
                email.is_limit = True
                email.save()
                response_dict['data'] = []
                return Response(dumps(response_dict), status=200, content_type="application/json")
            else:
                response_dict['message'] = 'Problem with the api hit to google' + json.dumps(content)
                response_dict['data'] = []
                return Response(dumps(response_dict), status=500, content_type="application/json")
        except KeyError, excp:
            response_dict['message'] = 'KeyError:: %s not in the request' % excp.message
            return Response(dumps(response_dict), status=400, content_type="application/json")
        except AssertionError, excp:
            response_dict['message'] = excp.message
            return Response(dumps(response_dict), status=400, content_type="application/json")



class CityView(FlaskView):
    def index(self):
        response_dict = {}
        cities = City.objects.all()
        response_dict['data'] = []
        for city in cities:
            data = {
                'google_place_id': city['google_place_id'],
                'name': city['name'],
                'southwest': city['southwest'],
                'northeast': city['northeast'],
                'point': city['point'],
                'step_degree': city['step_degree'],
                'is_verified': city['is_verified']
            }
            response_dict['data'].append(data)
        response_dict['message'] = 'Current Cities'
        return Response(dumps(response_dict), status=200, content_type="application/json")



    def post(self):
        response_dict = {}
        data = request.json
        if not data:
            data = request.form
        try:
            formated_data = {
                'name': data['name'],
                'southwest': data['southwest'],
                'northeast': data['northeast'],
                'point': data['point']
            }
        except KeyError, excp:
            response_dict['message'] = 'KeyError:: %s not in the request' % excp.message
            return Response(dumps(response_dict), status=400, content_type="application/json")

        try:
            city = City.objects.get(google_place_id=data['google_place_id'])
            response_dict['message'] = 'Record Found.. Cant be created'
            return Response(dumps(response_dict), status=400, content_type="application/json")
        except DoesNotExist, excp:
            city = City(**formated_data)
            city.save()
            response_dict['message'] = 'City Created'
            return Response(dumps(response_dict), status=200, content_type="application/json")



    def put(self, google_place_id):
        response_dict = {}
        data = request.json
        if not data:
            data = request.form
        try:
            formated_data = {
                'name': data['name'],
                'southwest': data['southwest'],
                'northeast': data['northeast'],
                'point': data['point'],
                'step_degree': data['step_degree'],
                'is_verified': False
            }
            city = City.objects.get(google_place_id=google_place_id)
            for key, value in formated_data.iteritems():
                setattr(city, key, value)
            city.save()
            response_dict['message'] = 'City Updated'
            return Response(dumps(response_dict), status=200, content_type="application/json")
        except DoesNotExist, excp:
            response_dict['message'] = 'No Record Found'
            return Response(dumps(response_dict), status=400, content_type="application/json")
        except KeyError, excp:
            response_dict['message'] = 'KeyError:: %s not in the request' % excp.message
            return Response(dumps(response_dict), status=400, content_type="application/json")

class CityVerifyView(FlaskView):
    def post(self):
        response_dict = {}
        data = request.json
        if not data:
            data = request.form
        try:
            city = City.objects.get(google_place_id=data['google_place_id'])
            verify = data['verify']
        except DoesNotExist, excp:
            response_dict['message'] = 'No Record Found'
            return Response(dumps(response_dict), status=400, content_type="application/json")
        except KeyError, excp:
            response_dict['message'] = 'KeyError:: %s not in the request' % excp.message
            return Response(dumps(response_dict), status=400, content_type="application/json")

        if verify:
            city.is_verified = True
        else:
            city.is_active = False

        city.save()
        if verify:
            create_city_latlonggrid.delay(city.google_place_id)
        response_dict['message'] = 'The city is Verified'
        return Response(dumps(response_dict), status=200, content_type="application/json")


class HospitalDataView(FlaskView):
    def index(self):
        response_dict = {}
        hospitals = HospitalData.objects.filter(is_processed=True, is_active=True)
        response_dict['data'] = []
        for hospital in hospitals:
            data = {
                'google_place_id': hospital['google_place_id'],
                'name': hospital['name'],
                'point': hospital['point'],
                'address': hospital['address'],
                'phone_no': hospital['phone_no'],
                'city': hospital.city.name
            }
            response_dict['data'].append(data)
        response_dict['message'] = 'Hospitals Present'
        return Response(dumps(response_dict), status=200, content_type="application/json")

    def put(self, google_place_id):
        response_dict = {}
        data = request.json
        if not data:
            data = request.form
        try:
            formated_data = {
                'name': data['name'],
                'point': data['point'],
                'address': data['address'],
                'phone_no': data['phone_no']
            }
            hospital = HospitalData.objects.get(google_place_id=google_place_id)
            for key, value in formated_data.iteritems():
                setattr(hospital, key, value)
            hospital.save()
            response_dict['message'] = 'Hospital Updated'
            return Response(dumps(response_dict), status=200, content_type="application/json")
        except DoesNotExist, excp:
            response_dict['message'] = 'Hospital Not Found'
            return Response(dumps(response_dict), status=400, content_type="application/json")
        except KeyError, excp:
            response_dict['message'] = 'KeyError:: %s not in the request' % excp.message
            return Response(dumps(response_dict), status=400, content_type="application/json")

class HospitalVerifyView(FlaskView):
    def post(self):
        response_dict = {}
        data = request.json
        if not data:
            data = request.form
        try:
            hospital = HospitalData.objects.get(google_place_id=data['google_place_id'])
            verify = data['verify']
        except DoesNotExist, excp:
            response_dict['message'] = 'No Record Found'
            return Response(dumps(response_dict), status=400, content_type="application/json")
        except KeyError, excp:
            response_dict['message'] = 'KeyError:: %s not in the request' % excp.message
            return Response(dumps(response_dict), status=400, content_type="application/json")

        if verify:
            hospital.is_verified = True
        else:
            hospital.is_active = False

        hospital.save()
        response_dict['message'] = 'The Hospital is Verified'
        return Response(dumps(response_dict), status=200, content_type="application/json")
