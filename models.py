"""
models.py

App Engine datastore models for Golf Ranking app

"""
from google.appengine.ext import ndb
from time import gmtime,strftime
import datetime

class Ranking(ndb.Model):
    week_id = ndb.IntegerProperty(required=True)
    week_date = ndb.StringProperty()
    rankings_json = ndb.JsonProperty()
    results_json = ndb.JsonProperty()
    
class Picker(ndb.Model):
    picks = ndb.StringProperty(repeated=True)
    count = ndb.IntegerProperty()
    points = ndb.FloatProperty()

# Current Week (YYWW)
def current_week():
    this_year=datetime.date.today().isocalendar()[0]%100
    this_week=datetime.date.today().isocalendar()[1]
    return (this_year*100)+(this_week-1)

# Current Day of the week (0=Mon,1=Tue,..,6=Sun)
def current_dotw():
    return datetime.datetime.now().weekday()

def current_year():
    return datetime.datetime.now().year

def add_player(picker,player):
    picker=Picker.get_by_id(picker)
    if player not in picker.picks:
        picker.picks.append(player)
        # sort available picks by name
        if picker=='Available':
            picks=picker.picks
            picker.picks=picks.sort()            
        picker.count+=1
        picker.put()
    return picker.picks

def drop_player(picker,player):
    picker=Picker.get_by_id(picker)
    if player in picker.picks:
        picker.picks.remove(player)
        picker.count-=1
        picker.put()
        return True
    else:
        return False

def get_picks(picker_name):
    picks={'Name': picker_name,'Count': 0,'Picks':[],'Points':0}
    picker=Picker.get_by_id(picker_name)
    if picker:
        picks={'Name': picker_name,'Count': picker.count,'Picks':picker.picks,'Points':picker.points}
    return picks

def all_picks():
    picks={}
    pickers=('Available','Mark','Steve')
    for picker in pickers:
        picks[picker]=get_picks(picker)
    return picks

def delete_ranking(week_id=current_week()):
    ranking = Ranking.get_by_id(week_id)
    if ranking:
        ranking.key.delete()
        return True
    else:
        return False
	
def get_rankings(week_id=current_week()):
    ranking = Ranking.get_by_id(week_id)
    if ranking:
        rankings = ranking.rankings_json
    else:
        rankings = None
    return rankings

def get_results(week_id=current_week()):
    ranking = Ranking.get_by_id(week_id)
    if ranking:
        results = ranking.results_json
    else:
        results = None
    return results

def get_weeks():
    weeks=[]
    for ranking in Ranking.query().order(-Ranking.week_id).fetch(50):
        if ranking.week_date and ranking.week_date.endswith(str(current_year())): 	
            week_no = ranking.week_id % 100
            week={ 'week_id': ranking.week_id, 'week_date': ranking.week_date + " (Week " + str(week_no) + ")" }
            weeks.append(week)
    return weeks

#Initialize Rankings for new year
def init_rankings(rankings):
    week_id = int(current_week())
    ranking = Ranking.get_by_id(week_id)
    ranking.week_id=int(rankings[0].get('Week'))
    ranking.week_date=rankings[0].get('date')
    ranking.rankings_json=rankings
    ranking.put()

# put picker information from rankings
def put_pickers(pickdict):
    for pickey in pickdict.keys():
        pickval=pickdict[pickey]
        picker=Picker(id=pickey, count=pickval.get('Count'),picks=pickval.get('Picks'), points=pickval.get('Points',0.0))  
        picker.put()

def put_rankings(rankings,results):
    rank_week =int(rankings[0].get('Week'))
    week_no = rankings[0].get('week_id',current_week())
    ranking=Ranking(id=week_no)
    ranking.week_id=week_no
    ranking.week_date=rankings[0].get('date')
    ranking.rankings_json=rankings
    ranking.results_json=results
    ranking.put()
 
def put_results(results):
    week_no = int(current_week())
    ranking=Ranking(id=week_no)
    ranking.week_id=int(week_no)    
    ranking.results_json=results
    ranking.put()

def update_week(week_id):
    ranking = Ranking.get_by_id(week_id)
    if ranking:
        ranking.week_id = week_id
        ranking.put()		