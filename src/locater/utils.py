__author__ = 'manoj'
from locater.models import GoogleHospitalData
import difflib

def get_google_id_data(hospital):
    from app import app
    configuration = app.config

    # distance Factors and the city
    google_instance = GoogleHospitalData.objects.filter(
        point__near=hospital.point,
        point__max_distance=configuration.get('MAX_ALLOWED_DISTANCE'),
        city=hospital.city
    )

    # Now fuzzy matching starts
    # name, address
    # field not present phone_no
    if google_instance.count() > 1:
        # name
        names = google_instance.distinct('name')
        matches = difflib.get_close_matches(hospital.name, names, cutoff=0.9)
        google_instance = google_instance.filter(name__in=matches)

        if google_instance.count() == 1:
            print google_instance[0].name
            return google_instance[0]
        elif google_instance.count() > 1:
            print 'Google Value:: '
            print google_instance.count()
        elif google_instance.count() == 0:
            matches = difflib.get_close_matches(hospital.name, names, cutoff=0.3)
            google_instance = google_instance.filter(name__in=matches)
            # print google_instance.count()

