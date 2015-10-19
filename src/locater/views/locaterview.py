from flask.ext.classy import FlaskView
from flask import Response
from flask.json import dumps
from flask import request
from locater.models import City
from mongoengine import DoesNotExist
from locater.tasks import create_city_latlonggrid
import json

class CityView(FlaskView):
    def index(self):
        '''EndPoint for the SpecificationTemplates GET method for url  /spec/?Page=<int>
        
        It returns the complete secification in page form 

        :param request: Incoming Flask request
        :return: ---Flask Response Object with json dump  Response object with the response_dict
        :response_dict have status_code,status,data,pages     
        '''
        response_dict = {}
        response_dict['status'] = {}
        response_dict['status']['success'] = True
        return Response(dumps(response_dict), status=200, content_type="application/json")


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
