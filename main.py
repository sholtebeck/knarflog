from flask import Flask, abort,jsonify, render_template, redirect, request
from google.appengine.api import memcache, users
import knarflog,datetime,json,models
import logging

app = Flask(__name__)
app.config['DEBUG'] = True
default_url='/app/index.html'
picks_url='/app/picks.html'
#logging.getLogger().setLevel(logging.DEBUG)

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
def logon_info():
    # check for login
    names={'sholtebeck':'Steve','mholtebeck':'Mark'}
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

def getPicks(username=None):
    picks = memcache.get('picks')
    if not picks:
        picks=models.get_picks(username)
    return picks   

@app.route('/')
def hello():
    """Redirect to default url"""
    return redirect(default_url, code=302)

@app.route('/about')
def about():
    return render_template('about.html', title='about', log=logon_info())

@app.route('/player/add', methods=['POST'])
def player_add():
    picker=get_current_user()
    player=json.loads(request.data).get('player')
    picks=models.add_player(picker,player)
    memcache.add('picks:'+picker,picks)
    picks=models.drop_player('Available',player)
    memcache.add('picks:Available',picks.sort())
    return jsonify({'success':True})

@app.route('/player/drop', methods=['POST'])
def player_drop():
    if not request.json or not 'player' in request.json:
        abort(400)
    picker=get_current_user()
    player=request.json.get('player')
    picks=models.drop_player(picker,player)
    picks=models.add_player('Available',player)
    return jsonify({'success':True})

@app.route('/api/picks', methods=['GET'])
def picks():
    return jsonify({'picks': getPicks()})

@app.route('/api/mypicks', methods=['GET'])
def my_picks():
    current_user=logon_info()
    username=current_user.get('name')
    pick = getRankings()[-1].get(username)
    pick['Picks'] = getPicks(username)
    pick['Count']=len(pick['Picks'])
    if pick['Count']<15:
        pick['Action']='Add'
        pick['Submit']='/player/add'
        pick['Players']=getPicks('Available')
    else:
        pick['Action']='Drop'
        pick['Submit']='/player/drop'
        pick['Players']=pick['Picks']
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

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

