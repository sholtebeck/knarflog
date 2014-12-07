"""
ndb.py

App Engine datastore models for Golf Ranking app

"""
from google.appengine.ext import ndb

class Week(db.Model):
    week_id = db.IntegerProperty(required=True)
    week_date = db.StringProperty()
    rankings = db.JsonProperty()
    results = db.JsonProperty

class User(db.Model):
    username = db.StringProperty(required=True)
    nickname = db.StringProperty()
    points = db.IntegerProperty()
    picks = db.StringListProperty()


