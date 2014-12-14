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
    picks = ndb.StringProperty(repeated=True)
    count = ndb.IntegerProperty()
    points = ndb.FloatProperty()

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

# put picker information from rankings
def put_pickers(pickdict):
    for pickey in pickdict.keys():
        pickval=pickdict[pickey]
        picker=Picker(id=pickey, count=pickval.get('Count'),picks=pickval.get('Picks'), points=pickval.get('Points',0.0))  
        picker.put()

def put_rankings(rankings):
    week_no = int(current_week())
    ranking=Ranking(id=week_no)
    ranking.week_id=int(rankings[0].get('Week'))
    ranking.week_date=rankings[0].get('date')
    ranking.rankings_json=rankings
    ranking.put()
    put_pickers(rankings[-1])
        

