import datetime
import mongoengine as db

class City(db.Document):
    name = db.StringField(required=True)
    google_place_id = db.StringField(unique=True)
    southwest = db.GeoPointField()
    northeast = db.GeoPointField()
    point = db.GeoPointField()
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

class Qualification(db.EmbeddedDocument):
    college = db.StringField()
    degree = db.StringField()
    completion_year = db.StringField()


class Availability(db.EmbeddedDocument):
    day = db.StringField()
    first_half_start_time = db.StringField()
    first_half_end_time = db.StringField()
    second_half_start_time = db.StringField()
    second_half_end_time = db.StringField()


class Specialty(db.EmbeddedDocument):
    specialty = db.StringField()
    sub_specialty = db.StringField()
    type = db.StringField()

class Doctors(db.EmbeddedDocument):
    doctor_name = db.StringField()
    summary = db.StringField()
    qualifications = db.EmbeddedDocumentListField(Qualification)
    is_local = db.BooleanField(default=True)
    is_male = db.BooleanField()
    available = db.EmbeddedDocumentListField(Availability)
    consultation_fee = db.FloatField()
    practice_time = db.IntField()
    specialties = db.EmbeddedDocumentListField(Specialty)


class HospitalData(db.Document):
    name = db.StringField(required=True)
    google_place_id = db.StringField(unique=True)
    s_id = db.StringField(unique=True)
    point = db.GeoPointField(required=True)
    address = db.StringField()
    phone_no = db.StringField()  # To get the phone no.
    doctors = db.EmbeddedDocumentListField(Doctors)
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
