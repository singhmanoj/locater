__author__ = 'manoj'

from app import celery, app
from locater.models import *

@celery.task()
def add(a, b):
    print a + b

@celery.task()
def create_city_latlonggrid(google_id):
    city = City.objects.get(google_id)

    lat = city.southwest[0]
    row = 0

    while lat < city.northeast[0]:
        # This is done to make the grid
        long = city.southwest[1] if row % 2 == 0 else city.southwest[1] + (city.step_degree/2)
        while long < city.northeast[1]:
            types = app.config.get('TYPES')
            for typ in types:
                data = {
                    'point': [lat, long],
                    'city': city,
                    'type': typ
                }
                CrawlData(**data).save()

            long += city.step_degree
        lat += city.step_degree
