"""
models.py

App Engine datastore models for Golf Ranking app

"""
from google.appengine.ext import ndb
import datetime

class Ranking(ndb.Model):
    week_id = ndb.IntegerProperty(required=True)
    week_date = ndb.StringProperty()
    rankings_json = ndb.JsonProperty()
    
class Picker(ndb.Model):
    name = ndb.StringProperty(required=True)
    points = ndb.FloatProperty()
    picks = ndb.StringProperty(repeated=True)

def current_week():
    now=datetime.datetime.now()
    this_week=100*(now.year-2000)+now.isocalendar()[1]-1
    return int(this_week) 

def get_rankings(week_id=current_week()):
    ranking = Ranking.get_by_id(week_id)
    if ranking:
        rankings = ranking.rankings_json
    else:
        rankings = None
    return rankings

def put_rankings(rankings):
    week_no = int(current_week())
    ranking=Ranking(id=week_no)
    ranking.week_id=int(rankings[0].get('Week'))
    ranking.week_date=rankings[0].get('date')
    ranking.rankings_json=rankings
    ranking.put()

# write picker info
def put_pickers(pickdict):
    pickers=[Picker(id=pickey['Name'],name=pickey['Name'],picks=pickey['Picks'],points=pickey['Points']) for pickey in pickdict.values()]
    ndb.put_multi(pickers)

    

