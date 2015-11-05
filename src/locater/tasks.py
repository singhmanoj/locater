__author__ = 'manoj'

import locater
from locater import celery
from locater.models import *
import datetime
from locater.utils import get_google_id_data

@celery.task
def add(a, b):
    print a + b

@celery.task
def create_city_latlonggrid(google_id):
    print google_id
    print 'City ::: ', City.objects.count()
    city = City.objects.get(google_place_id=google_id)
    print city.southwest
    lat = city.southwest["coordinates"][1]
    row = 0

    while lat < city.northeast["coordinates"][1]:
        # This is done to make the grid
        long = city.southwest["coordinates"][0] if row % 2 == 0 else city.southwest["coordinates"][0] + (city.step_degree/2)
        while long < city.northeast["coordinates"][0]:
            from app import app
            types = app.config.get('TYPES')
            for typ in types:
                data = {
                    'point': [lat, long],
                    'city': city,
                    'type': typ
                }
                print data
                CrawlData(**data).save()

            long += city.step_degree
        row += 1
        lat += city.step_degree


@celery.task
def merge_data():
    now = datetime.datetime.now()
    last_time = now - datetime.timedelta(hours=1)
    hospital = HospitalData.objects.filter(google_place_id=None, last_time_checked__lt=last_time)[0]
    hospital.last_time_checked = now
    hospital.save()
    google_data_id = get_google_id_data(hospital)  # function to map the data
    print google_data_id
    # if google_data_id:
    #     google_data_instance = GoogleHospitalData.objects.get(google_place_id=google_data_id)
    #     hospital.google_place_id = google_data_instance.google_place_id
    #     hospital.save()