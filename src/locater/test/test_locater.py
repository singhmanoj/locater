from flask import Flask
import unittest
# Testing Template
import json

class TestSpecificationClass():
    '''The class should have test in name for the automatic loading.
    '''
    def setup(self):
        '''This is the setup method call before each test case in class 
        Please put the sample data here for database.
        '''
        from app import app
        try:
            print 'Loading Fixture'
        except Exception , e:
            raise Exception(e)
        self.client = app.test_client()

    def teardown(self):
        '''This is the teardown method after each test case in class 
        Distroy the database.
        '''
        print 'every thing is destroyed'
    #The name of the method shoud have test in it

    def test_index(self):
        '''Put the test case here.
        '''
        #print response.status_code,response.data
        assert 2+2 == 4, 'working fine'
