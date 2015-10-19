from flask.ext.classy import FlaskView
from flask import Response
from flask.json import dumps
# from flask import request
import json

class SpecView(FlaskView):
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
