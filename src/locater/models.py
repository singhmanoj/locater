import datetime
import mongoengine as db

class City(db.Document):
    name = db.StringField(required=True)
    google_place_id = db.StringField(required=True, unique=True)
    southwest = db.GeoPointField(required=True)
    northeast = db.GeoPointField(required=True)
    point = db.GeoPointField(required=True)
    created_on = db.DateTimeField(default=datetime.datetime.now)
    modified_on = db.DateTimeField(default=datetime.datetime.now)
    is_verified = db.BooleanField(default=False)
    is_active = db.BooleanField(default=True)
    step_degree = db.FloatField()


    def save(self, *args, **kwargs):
        self.modified_on = datetime.datetime.now()  # To save the modified on
        from app import app
        if not self.step_degree:
            self.step_degree = app.config.get('STEP_DEGREE')

        super(City, self).save(*args, **kwargs)


class EmailSet(db.Document):
    """
    Just to increase the No of the query Set
    # This is not required if we purchase the commercial version
    """
    email = db.StringField(required=True, unique=True)
    is_blocked = db.BooleanField(default=False)
    is_limit = db.BooleanField(default=False)  # every night its should be False
    google_key = db.StringField(required=True)
    is_active = db.BooleanField(default=True)


class HospitalData(db.Document):
    name = db.StringField(required=True)
    google_place_id = db.StringField(required=True, unique=True)
    point = db.GeoPointField(required=True)
    address = db.StringField()
    phone_no = db.StringField()  # To get the phone no.
    created_on = db.DateTimeField(default=datetime.datetime.now)
    modified_on = db.DateTimeField(default=datetime.datetime.now)
    is_verified = db.BooleanField(default=False)
    is_active = db.BooleanField(default=True)
    city = db.ReferenceField(City)
    # This is temporary fields to get Phone No
    is_processing = db.BooleanField(default=False)
    is_processed = db.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.modified_on = datetime.datetime.now()  # To save the modified on
        super(HospitalData, self).save(*args, **kwargs)


class CrawlData(db.Document): # For the temporary data
    '''Crawling in the grid state step can be reduced if required
    '''
    point = db.GeoPointField(required=True)
    created_on = db.DateTimeField(default=datetime.datetime.now)
    modified_on = db.DateTimeField(default=datetime.datetime.now)
    is_processed = db.BooleanField(default=False)
    is_processing = db.BooleanField(default=False)  # for the worker
    city = db.ReferenceField(City)
    type = db.StringField(required=True)  # This is created automatically and it should be define in the setting file
    is_active = db.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.modified_on = datetime.datetime.now()  # To save the modified on

        super(CrawlData, self).save(*args, **kwargs)
