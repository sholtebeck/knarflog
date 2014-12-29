from flask import Flask, abort,json,jsonify, render_template, redirect, request
from google.appengine.api import memcache, users
import knarflog,datetime,models
import logging

app = Flask(__name__)
app.config['DEBUG'] = True
default_url='/app/index.html'
picks_url='/picks'
#logging.getLogger().setLevel(logging.DEBUG)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
def logon_info():
    # check for login
    names={'sholtebeck':'Steve','mholtebeck':'Mark','skipfloguser':'Steve'}
    log={'nickname':'guest', 'url_link':users.create_login_url(request.url), 'url_title': 'Login' }
    if users.get_current_user():
        log['nickname']=nickname=users.get_current_user().nickname()
        log['name'] = names.get(nickname,nickname)
        log['url_link'] = users.create_logout_url(request.url)
        log['url_title'] = 'Logout'
    #hack to fix the caller url to redirect to the default page
    log['url_link']=log['url_link'].replace('/api/user',default_url)
    return log 

# Routine to fetch the information
def get_current_user():
    current_user=logon_info()
    return current_user.get('name')

def getRankings(week_id=models.current_week()):
    rankings = memcache.get('rankings:'+str(week_id))
    if not rankings:
        rankings = models.get_rankings(week_id)
    if not rankings:
        rankings=knarflog.get_rankings()
        models.put_rankings(rankings)
    memcache.add('rankings:'+str(week_id), rankings)
    return rankings   

def myPicks(username):
    picks=models.get_picks(username)
    return picks   

def getPicks():
    picks = memcache.get('picks')
    if not picks:
        picks=getRankings(1451)[-1]
        for picker in picks.keys():
            picks[picker]=myPicks(picker)
        memcache.add('picks',picks)
    return picks   

    
@app.route('/')
def main():
    """Redirect to default url"""
    if users.get_current_user():
        return redirect(default_url, code=302)
    else:
        return redirect(users.create_login_url(default_url), code=302)

@app.route('/about')
def about():
    return render_template('about.html', title='about', log=logon_info())

@app.route('/api/picks', methods=['GET'])
@app.route('/api/picks/<picker>', methods=['GET'])
def picks(picker=None):
    if picker:
        picks=myPicks(picker)
    else:
        picks=getPicks()
    return jsonify({'picks': picks})

@app.route('/api/mypicks', methods=['GET'])
def my_picks():
    current_user=logon_info()
    username=current_user.get('name')
    pick=myPicks(username)
    pick['Max']=knarflog.MAXPICKS
    if pick['Count']<pick['Max'] and models.current_dotw()<4:
        pick['Available']=sorted(myPicks('Available')['Picks'])
    return jsonify({'picks': pick})

@app.route('/api/rankings', methods=['GET'])
def api_rankings():
    rankings = getRankings()
    return jsonify({'headers': rankings[0],'players': rankings[1:-1], 'pickers': rankings[-1].values() })

@app.route('/api/rankings/<int:week_id>', methods=['GET'])
def api_week_rankings(week_id):
    # pull direct from the datastore
    rankings = getRankings(week_id)
    return jsonify({'headers': rankings[0],'players': rankings[1:-1], 'pickers': rankings[-1].values() })

@app.route('/api/user', methods=['GET'])
def get_user():
    current_user=logon_info()
    return jsonify({'user':current_user })

@app.route('/player/add', methods=['POST'])
def player_add():
    if not request.json or not 'player' in request.json:
        abort(400)
    picker=get_current_user()
    player=json.loads(request.data).get('player')
    success=models.drop_player('Available',player)
    if success:
        picks=models.add_player(picker,player)
        memcache.delete('picks')
        message="Added "+player
    else:
        message=player+ " is no longer available"
    return jsonify({'success':success,'message':message})

@app.route('/player/drop', methods=['POST'])
def player_drop():
    if not request.json or not 'player' in request.json:
        abort(400)
    picker=get_current_user()
    player=request.json.get('player')
    success=models.drop_player(picker,player)
    if success:
        picks=models.add_player('Available',player)
        memcache.delete('picks')
        message="Dropped "+player
    else:
        message="Unable to drop "+player    
    return jsonify({'success':success,'message':message})

@app.route('/ranking', methods=['GET'])
@app.route('/ranking/<int:week_id>', methods=['GET'])
def ranking(week_id=models.current_week()):
    rankings = getRankings(week_id)
    header=rankings[0]
    header['Year']=models.current_year()
    players=[player for player in rankings[1:-1] if player.get('Picker')]
    pickers=[picker for picker in rankings[-1].values() if picker.get('Name')]
    if pickers[1]['Points']>pickers[0]['Points']:
        pickers.reverse()
    return render_template('ranking.html', header=header,players=players,pickers=pickers)

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

